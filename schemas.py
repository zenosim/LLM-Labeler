from pydantic import BaseModel, Field
from typing import List, Literal


class Criterion(BaseModel):
    name: str = Field(
        ..., description="Short name of the criterion, e.g., 'Relevance', 'Accuracy'"
    )
    description: str = Field(
        ..., description="Detailed instructions on how to evaluate this criterion."
    )


class BranchPlan(BaseModel):
    criteria: List[Criterion] = Field(
        ..., description="List of up to 5 evaluation criteria."
    )


class BranchEvaluation(BaseModel):
    criterion_name: str
    explanation: str = Field(..., description="Reasoning comparing both responses.")
    score_a: int = Field(..., ge=1, le=5, description="Score for Assistant A (1 to 5).")
    score_b: int = Field(..., ge=1, le=5, description="Score for Assistant B (1 to 5).")


class BSMResult(BaseModel):
    verdict: Literal["A", "B", "tie"]
    order_1_winner: Literal["A", "B", "tie"]
    order_2_winner: Literal["A", "B", "tie"]
    criteria: List[Criterion]
    order_1_evaluations: List[BranchEvaluation]
    order_2_evaluations: List[BranchEvaluation]
    order_1_total_a: int
    order_1_total_b: int
