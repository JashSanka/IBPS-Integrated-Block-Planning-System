"""
API Router - Dataset Management & Scope Switching.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.datasets import DatasetSwitchRequest, DatasetSummaryResponse
from app.services.state_service import get_state

router = APIRouter(tags=["Datasets"])


@router.get(
    "/datasets",
    response_model=DatasetSummaryResponse,
    summary="Get Active Dataset Information",
    description="Returns metadata about the active dataset (e.g. deterministic 21-task demo fixture or 200-task scaled dataset).",
)
def get_dataset_summary():
    state = get_state()
    desc = (
        "Deterministic 21-task demo fixture engineered with 12 explicit SIH story trade-offs."
        if state.active_dataset_type == "demo_fixture"
        else "Scaled ~200-task synthetic dataset across 12 railway trunks."
    )
    critical_count = sum(1 for t in state.tasks if t.priority_band and t.priority_band.value == "CRITICAL")
    corridors = sorted(list({t.corridor_id for t in state.tasks}))
    depts = sorted(list({t.department.value for t in state.tasks}))

    return DatasetSummaryResponse(
        active_dataset=state.active_dataset_type,
        description=desc,
        task_count=len(state.tasks),
        critical_task_count=critical_count,
        block_count=len(state.blocks),
        train_count=len(state.trains),
        corridor_count=len(corridors),
        corridors=corridors,
        departments=depts,
    )


@router.post(
    "/datasets/switch",
    response_model=DatasetSummaryResponse,
    summary="Switch Active Dataset",
    description="Switches the active dataset between 'demo_fixture' (default) and 'full_dataset' (scaled).",
    responses={
        400: {"description": "Invalid dataset identifier"},
    },
)
def switch_dataset(request: DatasetSwitchRequest):
    if request.dataset_type not in ("demo_fixture", "full_dataset"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid dataset_type. Must be 'demo_fixture' or 'full_dataset'.",
        )
    state = get_state()
    state.load_dataset(request.dataset_type)
    return get_dataset_summary()
