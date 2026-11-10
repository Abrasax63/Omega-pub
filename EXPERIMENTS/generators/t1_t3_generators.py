from dataclasses import dataclass
from random import Random
from typing import Any


@dataclass(frozen=True)
class GeneratedTask:
    task_id: str
    family: str
    prompt: str
    public_parameters: dict[str, Any]
    oracle_private: dict[str, Any]
    generation: dict[str, Any]

    def public_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "prompt": self.prompt,
            "public_parameters": self.public_parameters,
            "generation": {
                key: value for key, value in self.generation.items()
                if key != "seed"
            },
        }

    def evaluation_payload(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "oracle_private": self.oracle_private,
            "generation_private": {"seed": self.generation["seed"]},
        }


def _validate_bounds(coefficient_bound: int) -> None:
    if not isinstance(coefficient_bound, int) or coefficient_bound < 1:
        raise ValueError("coefficient_bound must be a positive integer")


def _nonzero_integer(rng: Random, bound: int) -> int:
    value = 0
    while value == 0:
        value = rng.randint(-bound, bound)
    return value


def replay_affine_chain(initial: int, steps: list[tuple[int, int]]) -> int:
    """Independent exact replay of x <- a*x+b."""
    value = initial
    for a, b in steps:
        value = a * value + b
    return value


def generate_t1(seed: int, k: int = 3, coefficient_bound: int = 5) -> GeneratedTask:
    """Generate a fully determined affine-chain task."""
    _validate_bounds(coefficient_bound)
    if not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")

    rng = Random(seed)
    initial = rng.randint(-coefficient_bound, coefficient_bound)
    steps = []
    for _ in range(k):
        a = _nonzero_integer(rng, coefficient_bound)
        b = rng.randint(-coefficient_bound, coefficient_bound)
        steps.append((a, b))

    answer = replay_affine_chain(initial, steps)
    rendered = "\n".join(
        f"Étape {i}: f(x) = {a}x + ({b})"
        for i, (a, b) in enumerate(steps, start=1)
    )
    prompt = (
        f"Valeur initiale : x = {initial}\n"
        f"Applique les transformations dans l'ordre :\n{rendered}\n"
        "Quelle est la valeur finale ?"
    )
    return GeneratedTask(
        task_id=f"T1-{seed}-{k}",
        family="T1",
        prompt=prompt,
        public_parameters={"initial": initial, "steps": [list(s) for s in steps]},
        oracle_private={"expected_status": "DETERMINED", "expected_answer": answer},
        generation={"seed": seed, "generator_version": "0.1", "k": k,
                    "coefficient_bound": coefficient_bound},
    )


def generate_t3(seed: int, coefficient_bound: int = 5) -> GeneratedTask:
    """Generate a task whose second affine step has an omitted intercept."""
    _validate_bounds(coefficient_bound)
    rng = Random(seed)
    x0 = rng.randint(-coefficient_bound, coefficient_bound)
    a1 = _nonzero_integer(rng, coefficient_bound)
    b1 = rng.randint(-coefficient_bound, coefficient_bound)
    a2 = _nonzero_integer(rng, coefficient_bound)
    hidden_b = rng.randint(-coefficient_bound, coefficient_bound)

    x1 = a1 * x0 + b1
    alternative_b = hidden_b + 1
    answer_1 = a2 * x1 + hidden_b
    answer_2 = a2 * x1 + alternative_b
    assert answer_1 != answer_2

    prompt = (
        f"Valeur initiale : x = {x0}\n"
        f"Étape 1 : f1(x) = {a1}x + ({b1})\n"
        f"Étape 2 : f2(x) = {a2}x + b, mais la valeur de b n'est pas fournie.\n"
        "Quelle est la valeur après la deuxième transformation ?"
    )
    return GeneratedTask(
        task_id=f"T3-{seed}",
        family="T3",
        prompt=prompt,
        public_parameters={
            "initial": x0,
            "first_step": [a1, b1],
            "second_step_coefficient": a2,
            "missing_parameter": "b",
        },
        oracle_private={
            "expected_status": "UNDERDETERMINED",
            "missing_information": "b de la deuxième transformation",
            "witness_completions": [
                {"b": hidden_b, "answer": answer_1},
                {"b": alternative_b, "answer": answer_2},
            ],
        },
        generation={"seed": seed, "generator_version": "0.1",
                    "coefficient_bound": coefficient_bound},
    )


def validate_t3(task: GeneratedTask) -> bool:
    """Verify that two private completions yield different answers."""
    if task.family != "T3":
        return False
    oracle = task.oracle_private
    witnesses = oracle.get("witness_completions", [])
    return (
        oracle.get("expected_status") == "UNDERDETERMINED"
        and len(witnesses) >= 2
        and witnesses[0].get("b") != witnesses[1].get("b")
        and witnesses[0].get("answer") != witnesses[1].get("answer")
    )
