"""
Adapter interfaces (Protocols) for Indian Railways legacy system boundaries.
These interfaces represent future live integrations with TMS, SMMS, TDMS, and COA.
"""

from typing import Protocol, List
from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast


class TMSAdapter(Protocol):
    """Track Management System (TMS) - Engineering Department Tasks."""
    def get_engineering_tasks(self) -> List[MaintenanceTask]:
        ...


class SMMSAdapter(Protocol):
    """Signalling Maintenance Management System (SMMS) - S&T Department Tasks."""
    def get_signal_tasks(self) -> List[MaintenanceTask]:
        ...


class TDMSAdapter(Protocol):
    """Traction Distribution Management System (TDMS) - TRD Department Tasks."""
    def get_traction_tasks(self) -> List[MaintenanceTask]:
        ...


class COAAdapter(Protocol):
    """Control Office Application (COA) - Operational constraints & block windows."""
    def get_block_windows(self) -> List[BlockWindow]:
        ...

    def get_train_movements(self) -> List[TrainMovement]:
        ...

    def get_goods_forecast(self) -> List[GoodsForecast]:
        ...
