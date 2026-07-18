from pydantic import BaseModel, Field
from typing import Literal, List

class TestCase(BaseModel):
    title: str
    description: str
    steps: List[str] = Field(min_length=1)
    expected_result: str
    risk_level: Literal["low", "medium", "high", "critical"]
    priority: Literal["low", "medium", "high"]
    requirement_reference: str

class GenerationResult(BaseModel):
    test_cases: List[TestCase] = Field(min_length=3, max_length=5)
