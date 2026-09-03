"""
Synthetic adapter implementations for TMS, SMMS, TDMS, and COA.
Clearly labelled as Synthetic / Demo Data for architectural honesty.
"""

from typing import List, Optional
from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast
from app.domain.enums import Department
from app.adapters.interfaces import TMSAdapter, SMMSAdapter, TDMSAdapter, COAAdapter


class SyntheticTMSAdapter(TMSAdapter):
    """Synthetic adapter for Engineering (Track) maintenance requests."""
    def __init__(self, tasks: Optional[List[MaintenanceTask]] = None):
        self._tasks = [t for t in (tasks or []) if t.department == Department.ENGINEERING]

    def set_tasks(self, tasks: List[MaintenanceTask]) -> None:
        self._tasks = [t for t in tasks if t.department == Department.ENGINEERING]

    def get_engineering_tasks(self) -> List[MaintenanceTask]:
        return list(self._tasks)


class SyntheticSMMSAdapter(SMMSAdapter):
    """Synthetic adapter for S&T (Signalling & Telecom) maintenance requests."""
    def __init__(self, tasks: Optional[List[MaintenanceTask]] = None):
        self._tasks = [t for t in (tasks or []) if t.department == Department.S_AND_T]

    def set_tasks(self, tasks: List[MaintenanceTask]) -> None:
        self._tasks = [t for t in tasks if t.department == Department.S_AND_T]

    def get_signal_tasks(self) -> List[MaintenanceTask]:
        return list(self._tasks)


class SyntheticTDMSAdapter(TDMSAdapter):
    """Synthetic adapter for TRD (Traction Distribution / OHE) maintenance requests."""
    def __init__(self, tasks: Optional[List[MaintenanceTask]] = None):
        self._tasks = [t for t in (tasks or []) if t.department == Department.TRD]

    def set_tasks(self, tasks: List[MaintenanceTask]) -> None:
        self._tasks = [t for t in tasks if t.department == Department.TRD]

    def get_traction_tasks(self) -> List[MaintenanceTask]:
        return list(self._tasks)


class SyntheticCOAAdapter(COAAdapter):
    """Synthetic adapter for COA (Control Office Application) operational data."""
    def __init__(
        self,
        block_windows: Optional[List[BlockWindow]] = None,
        train_movements: Optional[List[TrainMovement]] = None,
        goods_forecast: Optional[List[GoodsForecast]] = None,
    ):
        self._block_windows = block_windows or []
        self._train_movements = train_movements or []
        self._goods_forecast = goods_forecast or []

    def set_data(
        self,
        block_windows: List[BlockWindow],
        train_movements: List[TrainMovement],
        goods_forecast: List[GoodsForecast],
    ) -> None:
        self._block_windows = block_windows
        self._train_movements = train_movements
        self._goods_forecast = goods_forecast

    def get_block_windows(self) -> List[BlockWindow]:
        return list(self._block_windows)

    def get_train_movements(self) -> List[TrainMovement]:
        return list(self._train_movements)

    def get_goods_forecast(self) -> List[GoodsForecast]:
        return list(self._goods_forecast)
