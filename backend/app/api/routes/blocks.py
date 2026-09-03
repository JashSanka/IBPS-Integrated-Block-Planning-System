"""
API Router - Corridor Block Windows & Possession Details.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.blocks import BlockItemResponse, BlockDetailResponse
from app.services.block_service import BlockService

router = APIRouter(tags=["Block Windows"])


@router.get(
    "/blocks",
    response_model=List[BlockItemResponse],
    summary="List Corridor Block Windows",
    description="Lists available track possession windows across corridors with utilization rates, scheduled tasks, and train impact.",
)
def list_blocks(
    corridor: Optional[str] = Query(None, description="Filter by corridor ID (e.g. CSTM-KYN, KYN-PUN, NDLS-GZB)"),
):
    return BlockService.get_blocks(corridor=corridor)


@router.get(
    "/blocks/{block_id}",
    response_model=BlockDetailResponse,
    summary="Block Possession Window Detail",
    description="Returns full block details including assigned tasks, crew utilization, timetabled train conflicts, freight forecasts, and safety clearance notes.",
    responses={
        404: {"description": "Block window not found"},
    },
)
def get_block_detail(block_id: str):
    detail = BlockService.get_block_detail(block_id)
    if not detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Block window '{block_id}' was not found in active dataset.",
        )
    return detail
