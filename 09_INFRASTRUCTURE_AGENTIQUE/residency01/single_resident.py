"""Resource-aware, single-resident local model governor (experimental).

A model may be loaded only if: its GGUF bytes match an authorized pinned SHA;
a completed real SCALE01 report confirms its weight size and measured peak RSS;
the reported peak plus explicit safety reserve fits within the configured budget.
Never silently downgrade, never share KV state across models, never expose server
outside loopback. This governs memory residency, not scientific answer validity.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import time
import urllib.error
import urllib.request

EXPECTED_ENGINE="5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
AUTHORIZED={
    "0p5b":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b":"626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}


class AdmissionRefused(RuntimeError): pass
class RuntimeUncertain(RuntimeError): pass


@dataclass(frozen=True)
class ModelProfile:
    label: str
    model_path: Path
    sha256_expected: str
    weight_bytes: int
    observed_peak_rss_kib: int
    engine_sha: str
    source_status: str

    @classmethod
    def from_scale_report(cls, report:dict, model_path:Path):
        if not isinstance(report,dict) or report.get("status")!="FINISHED":
            raise AdmissionRefused("MEASURED_MODEL_REPORT_REQUIRED")
        label=report.get("model_label")
        if label not in AUTHORIZED:
            raise AdmissionRefused("UNAPPROVED_MODEL_LABEL")
        if report.get("engine_sha")!=EXPECTED_ENGINE:
            raise AdmissionRefused("ENGINE_REVISION_MISMATCH")
        if report.get("model_expected_sha256")!=AUTHORIZED[label]:
            raise AdmissionRefused("MODEL_REVISION_MISMATCH")
        summary=report.get("summary")
        if not isinstance(summary,dict) or summary.get("quality_status")!="LOCAL_TEXT_AND_SOURCE_GATE_PARITY":
            raise AdmissionRefused("SCIENTIFIC_READER_PARITY_NOT_VERIFIED")
        modes=summary.get("by_mode")
        if not isinstance(modes,dict):
            raise AdmissionRefused("MISSING_PHYSICAL_MEMORY_MEASUREMENT")
        try:
            peaks=[modes[mode]["server_peak_rss_kib_max"] for mode in ("off","on")]
        except (KeyError,TypeError):
            raise AdmissionRefused("MISSING_PHYSICAL_MEMORY_MEASUREMENT")
        if any(type(n) is not int or n<=0 for n in peaks):
            raise AdmissionRefused("INVALID_PHYSICAL_MEMORY_MEASUREMENT")
        size=report.get("model_weight_file_bytes")
        if type(size) is not int or size<=0:
            raise AdmissionRefused("INVALID_GGUF_SIZE")
        return cls(label,Path(model_path),AUTHORIZED[label],size,max(peaks),EXPECTED_ENGINE,
                   "SCALE01_LOCAL_READER18_PARITY_ONLY")


def check_model_file(profile:ModelProfile):
    if profile.sha256_expected!=AUTHORIZED.get(profile.label) or profile.engine_sha!=EXPECTED_ENGINE:
        raise AdmissionRefused("UNPINNED_WEIGHT_OR_ENGINE")
    path=profile.model_path
    if not path.is_file() or path.is_symlink():
        raise AdmissionRefused("MODEL_FILE_NOT_REGULAR_OR_ABSENT")
    if path.stat().st_size!=profile.weight_bytes:
        raise AdmissionRefused("MODEL_WEIGHT_SIZE_CHANGED")
    digest=sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            digest.update(chunk)
    if digest.hexdigest()!=profile.sha256_expected:
        raise AdmissionRefused("GGUF_SHA256_MISMATCH")


class SingleResidentGovernor:
    def __init__(self,backend,*,budget_kib:int,reserve_kib:int=524288):
        if type(budget_kib) is not int or type(reserve_kib) is not int or budget_kib<=reserve_kib or reserve_kib<1:
            raise ValueError("explicit budget > positive reserve required")
        self.backend=backend
        self.budget_kib=budget_kib
        self.reserve_kib=reserve_kib
        self.current:ModelProfile|None=None
        self.blocked=False
        self.switches=0

    def activate(self,profile:ModelProfile):
        if self.blocked:
            raise RuntimeUncertain("PREVIOUS_SERVER_STOP_OR_HEALTH_STATE_UNCERTAIN")
        if not isinstance(profile,ModelProfile):
            raise TypeError("ModelProfile required")
        if profile.observed_peak_rss_kib+self.reserve_kib>self.budget_kib:
            raise AdmissionRefused("INSUFFICIENT_MEASURED_MEMORY_HEADROOM")
        if self.current==profile:
            if not self.backend.healthy():
                self.blocked=True
                raise RuntimeUncertain("ACTIVE_SERVER_UNHEALTHY")
            return "REUSED_SAME_RESIDENT_MODEL"
        # Verify the intended new model *before* evicting the current one.
        check_model_file(profile)
        if self.current is not None:
            try:
                self.backend.stop()
            except Exception as exc:
                self.blocked=True
                raise RuntimeUncertain("CANNOT_CONFIRM_PREVIOUS_MODEL_UNLOADED") from exc
            self.current=None
        try:
            self.backend.start(profile)
            if not self.backend.healthy():
                raise RuntimeError("MODEL_SERVER_NOT_HEALTHY")
            peak=self.backend.peak_rss_kib()
            if type(peak) is not int or peak+self.reserve_kib>self.budget_kib:
                raise RuntimeError("OBSERVED_PROCESS_EXCEEDS_MEMORY_BUDGET")
        except Exception:
            try:
                self.backend.stop()
            except Exception:
                self.blocked=True
            raise
        self.current=profile
        self.switches+=1
        return "NEW_LOCAL_MODEL_RESIDENT"

    def release(self):
        if self.blocked:
            raise RuntimeUncertain("UNSAFE_TO_ASSUME_SERVER_RELEASE")
        if self.current is not None:
            try:
                self.backend.stop()
            except Exception as exc:
                self.blocked=True
                raise RuntimeUncertain("SERVER_TERMINATION_UNCONFIRMED") from exc
        self.current=None


class LocalLlamaBackend:
    """Functional localhost llama-server adapter; starts only pinned local GGUF.

    Requires a separately audited pinned llama-server binary. The server binary's
    true commit identity is NOT established by the manifest string alone.
    """
    def __init__(self,server_binary:Path,port=8129):
        if type(port) is not int or not 1024<=port<=65535:
            raise ValueError("unsafe port")
        self.server_binary=Path(server_binary)
        self.port=port
        self.process=None

    def start(self,profile):
        if self.process is not None:
            raise RuntimeError("SECOND_RESIDENT_MODEL_NOT_ALLOWED")
        if not self.server_binary.is_file():
            raise RuntimeError("LLAMA_SERVER_BINARY_MISSING")
        self.process=subprocess.Popen([
            str(self.server_binary),"-m",str(profile.model_path),"-c","4096","-t","4",
            "--parallel","1","--host","127.0.0.1","--port",str(self.port)
        ],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(90):
            if self.process.poll() is not None:
                raise RuntimeError("MODEL_SERVER_EXITED_EARLY")
            if self.healthy():
                return
            time.sleep(1)
        raise RuntimeError("MODEL_SERVER_START_TIMEOUT")

    def healthy(self):
        if self.process is None or self.process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{self.port}/health",timeout=2) as r:
                return json.loads(r.read(2048)).get("status")=="ok"
        except (urllib.error.URLError,TimeoutError,ValueError,KeyError):
            return False

    def peak_rss_kib(self):
        if self.process is None or self.process.poll() is not None:
            raise RuntimeError("MODEL_PROCESS_NOT_ALIVE")
        txt=Path(f"/proc/{self.process.pid}/status").read_text(encoding="utf8")
        match=re.search(r"(?m)^VmHWM:\s*(\d+)\s+kB$",txt)
        if match is None:
            raise RuntimeError("NO_LINUX_VMHWM")
        return int(match.group(1))

    def stop(self):
        p=self.process
        if p is None:return
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=15)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=15)
        self.process=None
