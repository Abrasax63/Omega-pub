"""RESUME25: private local CPU training state, no reconstruction or model download.
The caller owns a durable private directory; no checkpoint upload is performed.
"""
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import random
import shutil
import stat
import tempfile
from pathlib import Path

FIELDS = ('model', 'revision', 'tokenizer_sha', 'data_sha', 'plan_sha')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensors(model, trainable):
    return [(name, value) for name, value in model.named_parameters() if value.requires_grad == trainable]


def tensor_hash(named):
    h = hashlib.sha256()
    for name, value in named:
        h.update(name.encode())
        h.update(str(tuple(value.shape)).encode())
        h.update(str(value.dtype).encode())
        h.update(value.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def rng():
    import numpy as np
    import torch
    s = np.random.get_state()
    return dict(torch=torch.random.get_rng_state(), python=random.getstate(),
                numpy=[s[0], s[1].tolist(), s[2], s[3], s[4]])


def set_rng(state):
    import numpy as np
    import torch
    n = state['numpy']
    torch.random.set_rng_state(state['torch'])
    random.setstate(state['python'])
    np.random.set_state((n[0], np.asarray(n[1], dtype=np.uint32), n[2], n[3], n[4]))


def validate_context(context):
    need(set(context) == set(FIELDS), 'CONTEXT_FIELDS')
    need(all(isinstance(v, str) and v for v in context.values()), 'CONTEXT_VALUES')


def runtime_fingerprint(model):
    """Record observed numerical controls; this is not a determinism proof."""
    import torch
    packages = {}
    for name in ('torch', 'numpy', 'transformers', 'peft', 'accelerate', 'tokenizers', 'safetensors'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    cpu = {}
    cpuinfo = Path('/proc/cpuinfo')
    if cpuinfo.is_file():
        for line in cpuinfo.read_text().splitlines():
            if ':' in line:
                key, value = map(str.strip, line.split(':', 1))
                if key in ('vendor_id', 'model name', 'flags') and key not in cpu:
                    cpu[key] = value
    config = getattr(model, 'config', None)
    return dict(python=platform.python_version(), machine=platform.machine(), cpu=cpu,
                packages=packages, cpu_capability=torch.backends.cpu.get_cpu_capability(),
                torch_build_sha=hashlib.sha256(torch.__config__.show().encode()).hexdigest(),
                threads=torch.get_num_threads(), interop_threads=torch.get_num_interop_threads(),
                mkldnn_enabled=torch.backends.mkldnn.enabled,
                deterministic_algorithms=torch.are_deterministic_algorithms_enabled(),
                matmul_precision=torch.get_float32_matmul_precision(),
                attention_implementation=getattr(config, '_attn_implementation', None))


def save(model, optimizer, destination, context, next_step):
    import torch
    validate_context(context)
    need(type(next_step) is int and next_step >= 0, 'CURSOR')
    need(all(p.device.type == 'cpu' for p in model.parameters()), 'CPU_ONLY')
    destination = Path(destination)
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    need(not parent.is_symlink() and stat.S_IMODE(parent.stat().st_mode) & 0o077 == 0, 'PRIVATE_PARENT_REQUIRED')
    need(not destination.exists() and not destination.is_symlink(), 'DESTINATION_EXISTS')
    named = tensors(model, True)
    need(named, 'NO_TRAINABLE_PARAMETERS')
    temp = Path(tempfile.mkdtemp(prefix='.pending-', dir=parent))
    try:
        payload = dict(parameters={n:p.detach().clone() for n,p in named},
                       optimizer=optimizer.state_dict(), rng=rng(), training=model.training)
        statefile = temp/'state.pt'
        torch.save(payload, statefile)
        statefile.chmod(0o600)
        manifest = dict(schema=2, context=context, next_step=next_step,
                        runtime=runtime_fingerprint(model),
                        optimizer_class=type(optimizer).__module__+'.'+type(optimizer).__name__,
                        parameter_names=[n for n,p in named],
                        frozen_sha=tensor_hash(tensors(model, False)),
                        trainable_sha=tensor_hash(named), state_sha=digest(statefile))
        (temp/'manifest.json').write_text(json.dumps(manifest, sort_keys=True, allow_nan=False))
        (temp/'manifest.json').chmod(0o600)
        os.rename(temp, destination)
        return manifest
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def load(model, optimizer, source, context):
    import torch
    validate_context(context)
    source = Path(source)
    need(source.is_dir() and not source.is_symlink(), 'SOURCE')
    need(stat.S_IMODE(source.stat().st_mode) & 0o077 == 0, 'PRIVATE_SOURCE_REQUIRED')
    m = json.loads((source/'manifest.json').read_text())
    need(m.get('schema') == 2 and 'runtime' in m, 'RUNTIME_UNATTESTED_OR_UNSUPPORTED_SCHEMA')
    need(m['context'] == context, 'CONTEXT_MISMATCH')
    need(m['runtime'] == runtime_fingerprint(model), 'RUNTIME_MISMATCH')
    need(type(m['next_step']) is int and m['next_step'] >= 0, 'CURSOR')
    need(m['optimizer_class'] == type(optimizer).__module__+'.'+type(optimizer).__name__, 'OPTIMIZER_CLASS')
    named = tensors(model, True)
    need([n for n,p in named] == m['parameter_names'], 'PARAMETER_ORDER')
    need(all(p.device.type == 'cpu' for p in model.parameters()), 'CPU_ONLY')
    need(tensor_hash(tensors(model, False)) == m['frozen_sha'], 'FROZEN_BASE_MISMATCH')
    statefile = source/'state.pt'
    need(not statefile.is_symlink() and digest(statefile) == m['state_sha'], 'STATE_HASH')
    state = torch.load(statefile, map_location='cpu', weights_only=True)
    need(set(state['parameters']) == set(m['parameter_names']), 'PARAMETERS')
    for name, value in named:
        saved = state['parameters'][name]
        need(saved.shape == value.shape and saved.dtype == value.dtype and bool(torch.isfinite(saved).all()), 'PARAMETER_SHAPE_OR_VALUE')
    need(tensor_hash([(n, state['parameters'][n]) for n,p in named]) == m['trainable_sha'], 'TRAINABLE_HASH')
    before = {n:p.detach().clone() for n,p in named}
    before_opt, before_rng, before_mode = copy.deepcopy(optimizer.state_dict()), rng(), model.training
    try:
        with torch.no_grad():
            for n,p in named:
                p.copy_(state['parameters'][n])
        optimizer.load_state_dict(state['optimizer'])
        optimizer.zero_grad(set_to_none=True)
        set_rng(state['rng'])
        model.train(state['training'])
    except Exception:
        with torch.no_grad():
            for n,p in named:
                p.copy_(before[n])
        optimizer.load_state_dict(before_opt)
        set_rng(before_rng)
        model.train(before_mode)
        raise
    return m['next_step']


def selftest():
    import numpy as np
    import torch
    torch.set_num_threads(1)
    torch.manual_seed(25)
    random.seed(25)
    np.random.seed(25)
    model = torch.nn.Sequential(torch.nn.Linear(3,4), torch.nn.Dropout(.3), torch.nn.Linear(4,1))
    # A frozen base must be present and validated on the reconstructed model.
    model[0].requires_grad_(False)
    initial = copy.deepcopy(model.state_dict())
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=.001)
    context = dict(model='toy',revision='fixed',tokenizer_sha='unused',data_sha='train25',plan_sha='plan25')

    def step(network, optimizer):
        network.train()
        sample = torch.randn(2,3) + random.random() + float(np.random.random())
        optimizer.zero_grad(set_to_none=True)
        loss = network(sample).square().mean()
        loss.backward()
        optimizer.step()
        return sample, loss.detach()

    def equal(a,b):
        if torch.is_tensor(a): return torch.equal(a,b)
        if isinstance(a,dict): return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
        if isinstance(a,(tuple,list)): return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
        return a==b

    step(model,opt)
    with tempfile.TemporaryDirectory() as root:
        path = Path(root)/'checkpoint'
        save(model,opt,path,context,1)
        expected_sample, expected_loss = step(model,opt)
        expected_weights = copy.deepcopy(model.state_dict())
        expected_opt = copy.deepcopy(opt.state_dict())
        torch.manual_seed(99)
        other = torch.nn.Sequential(torch.nn.Linear(3,4), torch.nn.Dropout(.3), torch.nn.Linear(4,1))
        other.load_state_dict(initial)
        other[0].requires_grad_(False)
        otheropt = torch.optim.AdamW([p for p in other.parameters() if p.requires_grad], lr=.001)
        assert load(other,otheropt,path,context)==1
        sample, loss = step(other,otheropt)
        assert torch.equal(sample, expected_sample) and torch.equal(loss, expected_loss)
        assert equal(other.state_dict(),expected_weights) and equal(otheropt.state_dict(),expected_opt)
        reference = tensor_hash(tensors(other,True))
        for bad in (dict(context,revision='wrong'),dict(context,data_sha='different')):
            try: load(other,otheropt,path,bad)
            except ValueError: pass
            else: raise AssertionError('WRONG_CONTEXT_ACCEPTED')
            assert tensor_hash(tensors(other,True))==reference
        # Refuse an actual thread change and a recorded CPU capability mismatch
        # before mutating parameters, optimizer or random state.
        before_opt = copy.deepcopy(otheropt.state_dict())
        before_rng = rng()
        torch.set_num_threads(2)
        try:
            try: load(other,otheropt,path,context)
            except ValueError as error: assert str(error)=='RUNTIME_MISMATCH'
            else: raise AssertionError('THREAD_CHANGE_ACCEPTED')
        finally:
            torch.set_num_threads(1)
        manifestfile = path/'manifest.json'
        valid_manifest = json.loads(manifestfile.read_text())
        for legacy in (False, True):
            invalid = copy.deepcopy(valid_manifest)
            if legacy:
                invalid['schema']=1;invalid.pop('runtime')
                expected_error='RUNTIME_UNATTESTED_OR_UNSUPPORTED_SCHEMA'
            else:
                invalid['runtime']['cpu_capability']='different CPU dispatch'
                expected_error='RUNTIME_MISMATCH'
            manifestfile.write_text(json.dumps(invalid))
            try: load(other,otheropt,path,context)
            except ValueError as error: assert str(error)==expected_error
            else: raise AssertionError('UNATTESTED_RUNTIME_ACCEPTED')
            assert tensor_hash(tensors(other,True))==reference
            assert equal(otheropt.state_dict(),before_opt) and equal(rng(),before_rng)
        manifestfile.write_text(json.dumps(valid_manifest))
        statefile=path/'state.pt'
        data=bytearray(statefile.read_bytes());data[-1]^=1;statefile.write_bytes(data)
        try: load(other,otheropt,path,context)
        except ValueError: pass
        else: raise AssertionError('CORRUPTION_ACCEPTED')
        assert tensor_hash(tensors(other,True))==reference
    print(json.dumps(dict(status='RESUME25_TOY_EXACT',same_next_batch=True,same_loss=True,
                         same_updated_parameters=True,same_optimizer_state=True,
                         dropout_and_python_numpy_torch_rng_restored=True,
                         wrong_revision_and_data_rejected=True,corrupt_state_rejected=True,
                         changed_threads_and_cpu_rejected=True,legacy_unattested_state_rejected=True,
                         runtime_rejection_without_mutation=True,
                         pretrained_updates=0,private_durable_backend_connected=False)))


if __name__ == '__main__':
    selftest()
