"""
Data loader module for IBPS fixtures and generated synthetic datasets.
Handles JSON serialization/deserialization to preserve reproducibility.
"""

from datetime import datetime
import json
import os
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional

from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast
from app.data.generator import get_demo_fixture_data, generate_full_synthetic_dataset

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
FIXTURE_PATH = DATA_DIR / "fixtures" / "demo_fixture.json"
GENERATED_PATH = DATA_DIR / "generated" / "full_dataset.json"


def serialize_model_list(models: List[Any]) -> List[Dict[str, Any]]:
    return [m.model_dump(mode="json") for m in models]


def export_demo_fixture() -> None:
    """Exports demo fixture to data/fixtures/demo_fixture.json."""
    os.makedirs(FIXTURE_PATH.parent, exist_ok=True)
    tasks, blocks, trains, goods, emergency = get_demo_fixture_data()

    payload = {
        "metadata": {
            "name": "IBPS SIH-26027 Deterministic Demo Fixture",
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "description": "Deterministic 20-40 task fixture with 12 explicit demo story scenarios.",
        },
        "tasks": serialize_model_list(tasks),
        "block_windows": serialize_model_list(blocks),
        "train_movements": serialize_model_list(trains),
        "goods_forecast": serialize_model_list(goods),
        "emergency_task": emergency.model_dump(mode="json"),
    }

    with open(FIXTURE_PATH, "w") as f:
        json.dump(payload, f, indent=2)


def export_full_dataset() -> None:
    """Exports scaled 200-task synthetic dataset to data/generated/full_dataset.json."""
    os.makedirs(GENERATED_PATH.parent, exist_ok=True)
    tasks, blocks, trains, goods = generate_full_synthetic_dataset(seed=42)

    payload = {
        "metadata": {
            "name": "IBPS SIH-26027 Scaled Synthetic Dataset",
            "version": "1.0",
            "task_count": len(tasks),
            "block_count": len(blocks),
            "seed": 42,
        },
        "tasks": serialize_model_list(tasks),
        "block_windows": serialize_model_list(blocks),
        "train_movements": serialize_model_list(trains),
        "goods_forecast": serialize_model_list(goods),
    }

    with open(GENERATED_PATH, "w") as f:
        json.dump(payload, f, indent=2)


def load_demo_fixture() -> Tuple[List[MaintenanceTask], List[BlockWindow], List[TrainMovement], List[GoodsForecast], MaintenanceTask]:
    """Loads demo fixture from disk, generating if missing."""
    if not FIXTURE_PATH.exists():
        export_demo_fixture()

    with open(FIXTURE_PATH, "r") as f:
        data = json.load(f)

    tasks = [MaintenanceTask.model_validate(t) for t in data["tasks"]]
    blocks = [BlockWindow.model_validate(b) for b in data["block_windows"]]
    trains = [TrainMovement.model_validate(tr) for tr in data["train_movements"]]
    goods = [GoodsForecast.model_validate(g) for g in data["goods_forecast"]]
    emergency = MaintenanceTask.model_validate(data["emergency_task"])

    return tasks, blocks, trains, goods, emergency


def load_full_dataset() -> Tuple[List[MaintenanceTask], List[BlockWindow], List[TrainMovement], List[GoodsForecast]]:
    """Loads full synthetic dataset from disk, generating if missing."""
    if not GENERATED_PATH.exists():
        export_full_dataset()

    with open(GENERATED_PATH, "r") as f:
        data = json.load(f)

    tasks = [MaintenanceTask.model_validate(t) for t in data["tasks"]]
    blocks = [BlockWindow.model_validate(b) for b in data["block_windows"]]
    trains = [TrainMovement.model_validate(tr) for tr in data["train_movements"]]
    goods = [GoodsForecast.model_validate(g) for g in data["goods_forecast"]]

    return tasks, blocks, trains, goods
