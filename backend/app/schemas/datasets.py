"""
Pydantic Schemas - Dataset Management & Scope Toggling.
"""

from typing import List
from pydantic import BaseModel, Field


class DatasetSwitchRequest(BaseModel):
    """Request to switch active dataset between demo fixture and scaled synthetic dataset."""
    dataset_type: str = Field(
        default="demo_fixture",
        description="'demo_fixture' (21 tasks, 3 corridors) or 'full_dataset' (200 tasks, 12 corridors)"
    )


class DatasetSummaryResponse(BaseModel):
    """Summary of active dataset."""
    active_dataset: str
    description: str
    task_count: int
    critical_task_count: int
    block_count: int
    train_count: int
    corridor_count: int
    corridors: List[str]
    departments: List[str]
