"""
Pytest configuration and shared fixtures for IBPS testing.
"""

import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.generator import get_demo_fixture_data
from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast


@pytest.fixture
def demo_fixture():
    """Provides the standard 12-element deterministic demo fixture."""
    tasks, blocks, trains, goods, emergency = get_demo_fixture_data()
    return {
        "tasks": tasks,
        "blocks": blocks,
        "trains": trains,
        "goods": goods,
        "emergency_task": emergency,
    }
