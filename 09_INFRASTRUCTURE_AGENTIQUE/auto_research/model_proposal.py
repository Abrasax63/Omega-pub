"""Validate candidate Python from an open-weight code model.

Syntactic validation is defense in depth, not a replacement for sandboxing.
"""
import ast
import hashlib
import re
import subprocess

ALLOWED_CALLS = {"range", "len", "enumerate", "zip", "list", "int", "sum", "min", "max", "bool", "abs", "reversed"}
BANNED_NODES = (ast.Import, ast.ImportFrom, ast.ClassDef, ast.AsyncFunctionDef,
                ast.Await, ast.Global, ast.Nonlocal, ast.With, ast.AsyncWith,
                ast.Try, ast.Raise, ast.Yield, ast.YieldFrom, ast.Delete,
                ast.NamedExpr, ast.Lambda)
PROMPT = """<|im_start|>system
You are a code optimization assistant. Write ONLY valid Python source code.
Do not produce markdown or explanations. Never import modules.
<|im_end|>
<|im_start|>user
Write a standalone Python function:
def q_power(rows, steps):
    ...
The input rows is a list of non-negative Python int bitmasks representing
a directed graph of N vertices. Return a list of N int bitmasks for all
walks of EXACT length steps (Boolean matrix power). When steps=0 return
identity. It must work for any N>=1 and all nonnegative steps, including
large horizons. Optimize for speed. You may use loops, lists, bit operations,
integer.bit_length(), and Python builtins range, len, enumerate, min, max.
No imports, no external calls, no helper functions, no global variables.
Only emit one complete def q_power(rows, steps): function.
<|im_end|>
<|im_start|>assistant
"""


def validate_source(source):
    if not isinstance(source, str) or len(source) > 8000:
        raise ValueError("generated source size invalid")
    root = ast.parse(source)
    if len(root.body) != 1 or not isinstance(root.body[0], ast.FunctionDef):
        raise ValueError("exactly one function expected")
    fn = root.body[0]
    if fn.name != "q_power" or len(fn.args.args) != 2 or [a.arg for a in fn.args.args] != ["rows", "steps"]:
        raise ValueError("wrong algorithm signature")
    if fn.decorator_list or fn.args.kwarg or fn.args.vararg or fn.args.defaults:
        raise ValueError("decorators/defaults not accepted")
    for node in ast.walk(root):
        if isinstance(node, BANNED_NODES):
            raise ValueError("forbidden syntax: " + type(node).__name__)
        if isinstance(node, ast.FunctionDef) and node is not fn:
            raise ValueError("nested functions forbidden")
        if isinstance(node, ast.Name) and node.id.startswith("__"):
            raise ValueError("dunder access forbidden")
        if isinstance(node, ast.Attribute):
            if node.attr != "bit_length" or not isinstance(node.value, ast.Name):
                raise ValueError("attribute access forbidden")
        if isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                if target.id not in ALLOWED_CALLS:
                    raise ValueError("call forbidden: " + target.id)
            elif not (isinstance(target, ast.Attribute) and target.attr == "bit_length"):
                raise ValueError("call forbidden")
    return source.strip() + "\n"


def extract_candidate(raw):
    """Prefer last complete function; the CLI may echo the prompt."""
    cleaned = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", raw)
    starts = list(re.finditer(r"(?m)^def q_power\s*\(", cleaned))
    for match in reversed(starts):
        candidate = cleaned[match.start():]
        for marker in (chr(96) * 3, "<|im_end|>", "[end of text]"):
            candidate = candidate.split(marker, 1)[0]
        try:
            tree = ast.parse(candidate)
            if not tree.body or not isinstance(tree.body[0], ast.FunctionDef):
                continue
            first = tree.body[0]
            candidate = "\n".join(candidate.splitlines()[:first.end_lineno]) + "\n"
            return validate_source(candidate)
        except (SyntaxError, ValueError):
            continue
    raise ValueError("model did not return a valid allowed q_power function")


def generate_with_llama(llama_cli, model_file, variant, timeout=240):
    prompt = PROMPT
    if variant == 1:
        prompt = prompt.replace("Optimize for speed.", "Optimize for speed by reducing unnecessary matrix compositions.")
    command = [str(llama_cli), "-m", str(model_file), "-p", prompt,
               "-n", "400", "-c", "2048", "-t", "4", "--temp", "0"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=timeout)
    raw = result.stdout
    output = {"variant": variant, "model_call_returncode": result.returncode,
              "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
              "raw_characters": len(raw)}
    if result.returncode:
        output["failure"] = "llama-cli returned error"
        output["stderr_tail"] = result.stderr[-300:]
        return None, output
    try:
        code = extract_candidate(raw)
        output["source_sha256"] = hashlib.sha256(code.encode()).hexdigest()
        output["source"] = code
        return code, output
    except ValueError as exc:
        output["failure"] = str(exc)
        return None, output
