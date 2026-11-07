"""Boundary objects and schema checks. Avoid using reference answers at inference time."""
from dataclasses import dataclass
from typing import Any
import hashlib
import json

STRATEGIES = frozenset({"target_check", "unit_check", "step_check", "relation_check"})
ERROR_STATUSES = frozenset({"identified", "possible", "none", "uncertain"})

class ContractError(ValueError):
    pass


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Case:
    case_id: str
    question: str
    student_solution: str

    def __post_init__(self):
        for field, n in (("case_id", 128), ("question", 12000), ("student_solution", 12000)):
            text = getattr(self, field)
            if not isinstance(text, str) or not text.strip() or len(text) > n:
                raise ContractError(f"Invalid {field}")
        if any(c in self.case_id for c in "\r\n\\/"):
            raise ContractError("Unsafe case_id")

    def inference_dict(self) -> dict:
        return {"case_id": self.case_id, "question": self.question, "student_solution": self.student_solution}

    @property
    def input_hash(self):
        return fingerprint(self.inference_dict())


@dataclass(frozen=True)
class Diagnosis:
    error_status: str
    evidence_quote: str
    diagnosis: str
    strategy: str
    arithmetic_expression: str

    @classmethod
    def parse(cls, payload: dict):
        if not isinstance(payload, dict):
            raise ContractError("Diagnosis not a JSON object")
        allowed = {"error_status", "evidence_quote", "diagnosis", "strategy", "arithmetic_expression"}
        if not allowed.issubset(payload):
            raise ContractError("Diagnosis missing fields: " + repr(allowed - set(payload)))
        for key in allowed:
            if not isinstance(payload[key], str) or len(payload[key]) > 3000:
                raise ContractError("Bad diagnosis field: " + key)
        status = payload["error_status"].lower().strip()
        strategy = payload["strategy"].lower().strip()
        if status not in ERROR_STATUSES or strategy not in STRATEGIES:
            raise ContractError("Unsupported diagnosis enum")
        return cls(status, payload["evidence_quote"].strip(), payload["diagnosis"].strip(), strategy,
                   payload["arithmetic_expression"].strip())

    def as_dict(self):
        return vars(self).copy()


@dataclass(frozen=True)
class Feedback:
    teacher_draft: str
    scaffold_question: str

    @classmethod
    def parse(cls, payload: dict):
        if not isinstance(payload, dict):
            raise ContractError("Feedback not a JSON object")
        for key in ("teacher_draft", "scaffold_question"):
            if not isinstance(payload.get(key), str) or not payload[key].strip() or len(payload[key]) > 2000:
                raise ContractError("Bad feedback field: " + key)
        return cls(payload["teacher_draft"].strip(), payload["scaffold_question"].strip())

    def as_dict(self):
        return vars(self).copy()
