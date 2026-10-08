from typing import Literal
from pydantic import BaseModel, Field

Target=Literal['CAD','LAD','LCX','RCA']


class Contribution(BaseModel):
    feature: str
    label: str
    group: str
    unit: str
    input: int | float | str
    value: float


class Explanation(BaseModel):
    base_probability: float
    contributions: list[Contribution]
    reconstructed_probability: float
    method: str
    unit: str
    background_n: int
    note: str


class Candidate(BaseModel):
    family: str
    probability: float=Field(ge=0,le=1)


class ModelReference(BaseModel):
    artifact_file: str
    member: str
    training_n: int
    training_indices_sha256: str
    note: str


class Risk(BaseModel):
    probability: float=Field(ge=0,le=1)
    positive: bool
    threshold: float
    family: str
    calibration: str
    model_hash: str
    model_reference: ModelReference
    agreement: list[Candidate]
    agreement_spread: float
    resampling_range: list[float]
    range_models: int
    range_note: str
    confidence_note: str
    explanation: Explanation


class Representation(BaseModel):
    flag: bool
    nearest_distance: float
    reference_threshold: float
    outside_features: list[str]
    method: str


class PredictionResponse(BaseModel):
    targets: dict[Target,Risk]
    warnings: list[str]
    ood: Representation
    mode: str
    case_id: str | None
    observed: dict[Target,int] | None
    version: str
    dataset_sha256: str
    anatomy_note: str
    feature_count: int
