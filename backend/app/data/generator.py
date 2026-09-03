"""
Synthetic Data Generator for IBPS.
Generates:
1. Deterministic small demo fixture (22 tasks, 7 block windows, 6 trains, 4 goods forecasts across 3 corridors)
   engineered with genuine optimization trade-offs (fragmentation, traffic opportunity cost, resource bottlenecks,
   incompatible tasks, precedence, and emergency displacement).
2. Scaled synthetic dataset (200 tasks, 40 blocks, 60 trains, 12 corridors) with fixed random seed.
"""

from datetime import datetime, timedelta
import json
import random
from typing import List, Dict, Any, Tuple

from app.domain.models import MaintenanceTask, BlockWindow, TrainMovement, GoodsForecast
from app.domain.enums import (
    Department,
    Severity,
    TaskStatus,
    TrainType,
    Direction,
    TrafficDensity,
)


def get_demo_fixture_data() -> Tuple[List[MaintenanceTask], List[BlockWindow], List[TrainMovement], List[GoodsForecast], MaintenanceTask]:
    """
    Returns hand-crafted deterministic demo fixture containing all 12 required story elements
    with genuine optimization trade-offs.
    Base reference time: 2026-09-01 00:00:00.
    """
    base_t = datetime(2026, 9, 1, 0, 0, 0)

    # -------------------------------------------------------------
    # STORY ELEMENT 4: MULTIPLE CORRIDORS
    # Corridor 1: CSTM-KYN (Mumbai Suburban / Mainline trunk)
    # Corridor 2: KYN-PUN (Ghat Section / Mixed Freight & Intercity)
    # Corridor 3: NDLS-GZB (Heavy Passenger / High Density Trunk)
    # -------------------------------------------------------------

    # =============================================================
    # BLOCK WINDOWS (Available track possession opportunities)
    # =============================================================
    block_windows = [
        # ---------------------------------------------------------
        # KYN-PUN CORRIDOR WINDOWS:
        # Window 1: Night Integrated Mega-Block (Low traffic, permits ENG + S&T + TRD, Power Block Available)
        # IBPS consolidates compatible tasks here to save block hours and avoid daytime disruption.
        # ---------------------------------------------------------
        BlockWindow(
            block_id="BLK-KP-NIGHT-01",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(hours=1, minutes=30),  # 01:30
            end_time=base_t + timedelta(hours=5, minutes=0),     # 05:00 (210 min = 3.5 hrs)
            available_capacity=4,
            resource_capacity=12,
            safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
            traffic_density=TrafficDensity.LOW,
        ),
        # Window 2: Department-specific early morning window (Baseline takes this separately)
        BlockWindow(
            block_id="BLK-KP-ENG-EARLY",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(hours=5, minutes=30),  # 05:30
            end_time=base_t + timedelta(hours=7, minutes=30),    # 07:30 (120 min = 2.0 hrs)
            available_capacity=2,
            resource_capacity=6,
            safety_constraints=["TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING],
            traffic_density=TrafficDensity.MEDIUM,
        ),
        # Window 3: Attractive-looking Daytime Block with High Traffic Disruption (Overlaps Vande Bharat!)
        BlockWindow(
            block_id="BLK-KP-DAY-PEAK",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(hours=11, minutes=0),  # 11:00
            end_time=base_t + timedelta(hours=13, minutes=30),   # 13:30 (150 min = 2.5 hrs)
            available_capacity=3,
            resource_capacity=8,
            safety_constraints=["TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T],
            traffic_density=TrafficDensity.HIGH,
        ),
        # Window 4: Day 2 Night Shadow Block (for precedence follow-up)
        BlockWindow(
            block_id="BLK-KP-NIGHT-02",
            corridor_id="KYN-PUN",
            start_time=base_t + timedelta(days=1, hours=1, minutes=30), # Day 2 01:30
            end_time=base_t + timedelta(days=1, hours=5, minutes=0),    # Day 2 05:00 (210 min = 3.5 hrs)
            available_capacity=4,
            resource_capacity=12,
            safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
            traffic_density=TrafficDensity.LOW,
        ),

        # ---------------------------------------------------------
        # CSTM-KYN CORRIDOR WINDOWS:
        # Window 5: Tight Night Window with Crew Bottleneck (Max 8 crew!)
        # ---------------------------------------------------------
        BlockWindow(
            block_id="BLK-CK-NIGHT-01",
            corridor_id="CSTM-KYN",
            start_time=base_t + timedelta(hours=1, minutes=15),  # 01:15
            end_time=base_t + timedelta(hours=4, minutes=15),    # 04:15 (180 min = 3.0 hrs)
            available_capacity=3,
            resource_capacity=8,  # Bottleneck capacity!
            safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
            traffic_density=TrafficDensity.LOW,
        ),
        # Window 6: CSTM-KYN Day 2 Night Shadow Window
        BlockWindow(
            block_id="BLK-CK-NIGHT-02",
            corridor_id="CSTM-KYN",
            start_time=base_t + timedelta(days=1, hours=1, minutes=15), # Day 2 01:15
            end_time=base_t + timedelta(days=1, hours=4, minutes=15),    # Day 2 04:15 (180 min = 3.0 hrs)
            available_capacity=3,
            resource_capacity=8,
            safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
            traffic_density=TrafficDensity.LOW,
        ),

        # ---------------------------------------------------------
        # NDLS-GZB CORRIDOR WINDOWS:
        # Window 7: Early Morning Trunk Block (Low traffic)
        # ---------------------------------------------------------
        BlockWindow(
            block_id="BLK-NG-NIGHT-01",
            corridor_id="NDLS-GZB",
            start_time=base_t + timedelta(hours=2, minutes=0),   # 02:00
            end_time=base_t + timedelta(hours=5, minutes=0),     # 05:00 (180 min = 3.0 hrs)
            available_capacity=3,
            resource_capacity=10,
            safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
            permitted_departments=[Department.ENGINEERING, Department.S_AND_T, Department.TRD],
            traffic_density=TrafficDensity.LOW,
        ),
    ]

    # =============================================================
    # TRAIN MOVEMENTS (Timetabled operations)
    # =============================================================
    train_movements = [
        # STORY ELEMENT 7: High Priority Vande Bharat overlapping BLK-KP-DAY-PEAK
        TrainMovement(
            train_id="TRN-VB-22225",
            corridor_id="KYN-PUN",
            train_type=TrainType.VANDE_BHARAT,
            direction=Direction.DOWN,
            start_time=base_t + timedelta(hours=11, minutes=30),
            end_time=base_t + timedelta(hours=12, minutes=15),
            operational_priority=1,
            disruption_penalty=900.0,
        ),
        # Morning Suburban Peak Train on KYN-PUN during BLK-KP-ENG-EARLY
        TrainMovement(
            train_id="TRN-SUB-97011",
            corridor_id="KYN-PUN",
            train_type=TrainType.PASSENGER,
            direction=Direction.UP,
            start_time=base_t + timedelta(hours=6, minutes=15),
            end_time=base_t + timedelta(hours=7, minutes=0),
            operational_priority=3,
            disruption_penalty=200.0,
        ),
        # Mainline Express on NDLS-GZB
        TrainMovement(
            train_id="TRN-RAJ-12952",
            corridor_id="NDLS-GZB",
            train_type=TrainType.RAJDHANI_EXPRESS,
            direction=Direction.UP,
            start_time=base_t + timedelta(hours=6, minutes=30),
            end_time=base_t + timedelta(hours=7, minutes=15),
            operational_priority=1,
            disruption_penalty=800.0,
        ),
        # Suburban Trains on CSTM-KYN
        TrainMovement(
            train_id="TRN-SUB-97001",
            corridor_id="CSTM-KYN",
            train_type=TrainType.PASSENGER,
            direction=Direction.UP,
            start_time=base_t + timedelta(hours=8, minutes=0),
            end_time=base_t + timedelta(hours=8, minutes=45),
            operational_priority=3,
            disruption_penalty=150.0,
        ),
    ]

    # =============================================================
    # GOODS FORECAST (Freight traffic)
    # =============================================================
    goods_forecast = [
        GoodsForecast(
            corridor_id="KYN-PUN",
            time_window="NIGHT_00_06",
            start_time=base_t + timedelta(hours=0),
            end_time=base_t + timedelta(hours=6),
            expected_goods_trains=1,
            probability=0.4,
            traffic_density=TrafficDensity.LOW,
        ),
        GoodsForecast(
            corridor_id="KYN-PUN",
            time_window="DAY_09_15",
            start_time=base_t + timedelta(hours=9),
            end_time=base_t + timedelta(hours=15),
            expected_goods_trains=7,
            probability=0.9,
            traffic_density=TrafficDensity.HIGH,
        ),
        GoodsForecast(
            corridor_id="NDLS-GZB",
            time_window="NIGHT_01_06",
            start_time=base_t + timedelta(hours=1),
            end_time=base_t + timedelta(hours=6),
            expected_goods_trains=2,
            probability=0.5,
            traffic_density=TrafficDensity.LOW,
        ),
        GoodsForecast(
            corridor_id="CSTM-KYN",
            time_window="NIGHT_01_05",
            start_time=base_t + timedelta(hours=1),
            end_time=base_t + timedelta(hours=5),
            expected_goods_trains=1,
            probability=0.3,
            traffic_density=TrafficDensity.LOW,
        ),
    ]

    # =============================================================
    # MAINTENANCE TASKS (20 Tasks + 1 Emergency Task)
    # =============================================================
    tasks = [
        # ---------------------------------------------------------
        # STORY ELEMENT 6: HIGH-PRIORITY OVERDUE SAFETY-CRITICAL DEFECT
        # Severe Rail Fracture (Criticality 96, Safety 98, Overdue 14 days)
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-ENG-001",
            department=Department.ENGINEERING,
            asset_id="TRK-KP-102",
            asset_type="RAIL_TRACK",
            corridor_id="KYN-PUN",
            location="KM 102/4-102/8",
            defect_type="SEVERE_RAIL_FRACTURE",
            severity=Severity.CRITICAL,
            criticality=96.0,
            safety_risk=98.0,
            overdue_days=14,
            estimated_duration_min=150,
            crew_required=4,
            resource_requirements=["WELDING_PLANT", "RAIL_CUTTER"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=90.0,
        ),

        # ---------------------------------------------------------
        # STORY ELEMENT 5: GENUINE CROSS-DEPARTMENT CLUBBING SET ON KYN-PUN
        # Compatible timing, corridor, safety, crew (Night block BLK-KP-NIGHT-01)
        # 1. ENG-002: Track Tamping & Alignment (ENG, crew 3)
        # 2. SNT-001: Point Machine Overhaul (S&T, crew 2)
        # 3. TRD-001: OHE Stagger Adjustment (TRD, crew 3)
        # Combined crew: 3 + 2 + 3 = 8 <= 12 capacity
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-ENG-002",
            department=Department.ENGINEERING,
            asset_id="TRK-KP-104",
            asset_type="TURNOUT",
            corridor_id="KYN-PUN",
            location="KM 104/2",
            defect_type="TURNOUT_SLACK_TAMPING",
            severity=Severity.MAJOR,
            criticality=75.0,
            safety_risk=65.0,
            overdue_days=4,
            estimated_duration_min=120,
            crew_required=3,
            resource_requirements=["TAMPING_UNIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=70.0,
        ),
        MaintenanceTask(
            task_id="TASK-SNT-001",
            department=Department.S_AND_T,
            asset_id="SIG-KP-204",
            asset_type="POINT_MACHINE",
            corridor_id="KYN-PUN",
            location="KM 104/2",
            defect_type="POINT_MACHINE_CONTACT_WEAR",
            severity=Severity.MAJOR,
            criticality=80.0,
            safety_risk=70.0,
            overdue_days=5,
            estimated_duration_min=90,
            crew_required=2,
            resource_requirements=["TESTING_TOOLKIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=70.0,
        ),
        MaintenanceTask(
            task_id="TASK-TRD-001",
            department=Department.TRD,
            asset_id="OHE-KP-304",
            asset_type="OHE_CANTILEVER",
            corridor_id="KYN-PUN",
            location="KM 104/2-104/6",
            defect_type="CANTILEVER_STAGGER_ADJUSTMENT",
            severity=Severity.MAJOR,
            criticality=70.0,
            safety_risk=60.0,
            overdue_days=3,
            estimated_duration_min=110,
            crew_required=3,
            resource_requirements=["TOWER_WAGON"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=70.0,
        ),

        # ---------------------------------------------------------
        # STORY ELEMENT 8: CREW BOTTLENECK & PRIORITY ARBITRATION
        # Corridor CSTM-KYN has BLK-CK-NIGHT-01 with max 8 crew capacity.
        # TASK-ENG-003A (Critical Ballast Screening, crew 6, prio ~90) competes with
        # TASK-ENG-003B (Routine sleeper check, crew 5, prio ~35) and
        # TASK-SNT-002 (Critical Axle Counter, crew 2, prio ~94).
        # In baseline greedy: ENG-003B takes 5 crew, leaving only 3, blocking ENG-003A (needs 6).
        # In CP-SAT: ENG-003A (6) + SNT-002 (2) = 8 exactly, maximizing critical completion!
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-ENG-003A",
            department=Department.ENGINEERING,
            asset_id="TRK-CK-012",
            asset_type="RAIL_TRACK",
            corridor_id="CSTM-KYN",
            location="KM 12/0-12/8",
            defect_type="DEEP_SCREENING_BALLAST",
            severity=Severity.CRITICAL,
            criticality=90.0,
            safety_risk=88.0,
            overdue_days=8,
            estimated_duration_min=140,
            crew_required=6,
            resource_requirements=["BCM_MACHINE"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=85.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-003B",
            department=Department.ENGINEERING,
            asset_id="TRK-CK-015",
            asset_type="RAIL_TRACK",
            corridor_id="CSTM-KYN",
            location="KM 15/1-15/6",
            defect_type="ROUTINE_SLEEPER_INSPECTION",
            severity=Severity.ROUTINE,
            criticality=30.0,
            safety_risk=25.0,
            overdue_days=0,
            estimated_duration_min=90,
            crew_required=5,
            resource_requirements=["STANDARD_TOOLS"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=40.0,
        ),
        MaintenanceTask(
            task_id="TASK-SNT-002",
            department=Department.S_AND_T,
            asset_id="SIG-CK-110",
            asset_type="AXLE_COUNTER",
            corridor_id="CSTM-KYN",
            location="KM 18/4",
            defect_type="DIGITAL_AXLE_COUNTER_RESET_DRIFT",
            severity=Severity.CRITICAL,
            criticality=94.0,
            safety_risk=92.0,
            overdue_days=9,
            estimated_duration_min=80,
            crew_required=2,
            resource_requirements=["DAC_CALIBRATOR"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=90.0,
        ),

        # ---------------------------------------------------------
        # STORY ELEMENT 9: PRECEDENCE DEPENDENCY
        # TASK-ENG-004 (Bridge Girder Rivet Tightening) requires
        # TASK-TRD-002 (OHE Power De-energization) to complete FIRST.
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-TRD-002",
            department=Department.TRD,
            asset_id="OHE-KP-501",
            asset_type="ISOLATOR_SWITCH",
            corridor_id="KYN-PUN",
            location="KM 55/1",
            defect_type="ISOLATOR_CONTACT_REFURBISHMENT",
            severity=Severity.MAJOR,
            criticality=78.0,
            safety_risk=75.0,
            overdue_days=3,
            estimated_duration_min=100,
            crew_required=3,
            resource_requirements=["DISCHARGE_RODS"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=65.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-004",
            department=Department.ENGINEERING,
            asset_id="BRG-KP-502",
            asset_type="STEEL_GIRDER_BRIDGE",
            corridor_id="KYN-PUN",
            location="KM 55/2",
            defect_type="BRIDGE_GIRDER_RIVET_TIGHTENING",
            severity=Severity.MAJOR,
            criticality=82.0,
            safety_risk=80.0,
            overdue_days=4,
            estimated_duration_min=120,
            crew_required=4,
            resource_requirements=["PNEUMATIC_RIVETER"],
            precedence=["TASK-TRD-002"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=65.0,
        ),

        # ---------------------------------------------------------
        # INCOMPATIBLE CROSS-DEPARTMENT TASKS TEST SCENARIO
        # TASK-ENG-HEAVY-009 and TASK-TRD-INCOMP-009 are mutually exclusive
        # because high-voltage OHE testing conflicts with rail crane boom operation on the same KM.
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-ENG-HEAVY-009",
            department=Department.ENGINEERING,
            asset_id="TRK-KP-990",
            asset_type="RAIL_CRANE",
            corridor_id="KYN-PUN",
            location="KM 60/0",
            defect_type="HEAVY_RAIL_CRANE_TURNOUT_INSERTION",
            severity=Severity.MAJOR,
            criticality=76.0,
            safety_risk=70.0,
            overdue_days=2,
            estimated_duration_min=120,
            crew_required=4,
            incompatible_tasks=["TASK-TRD-INCOMP-009"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=60.0,
        ),
        MaintenanceTask(
            task_id="TASK-TRD-INCOMP-009",
            department=Department.TRD,
            asset_id="OHE-KP-991",
            asset_type="OHE_LIVE_TEST",
            corridor_id="KYN-PUN",
            location="KM 60/0",
            defect_type="OHE_25KV_CHARGING_SAFETY_TEST",
            severity=Severity.MAJOR,
            criticality=74.0,
            safety_risk=72.0,
            overdue_days=2,
            estimated_duration_min=90,
            crew_required=3,
            incompatible_tasks=["TASK-ENG-HEAVY-009"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=60.0,
        ),

        # ---------------------------------------------------------
        # Additional Realistic Tasks across Departments
        # ---------------------------------------------------------
        MaintenanceTask(
            task_id="TASK-TRD-003",
            department=Department.TRD,
            asset_id="OHE-CK-405",
            asset_type="INSULATOR",
            corridor_id="CSTM-KYN",
            location="KM 22/1",
            defect_type="PORCELAIN_INSULATOR_FLASH_MARK",
            severity=Severity.MAJOR,
            criticality=70.0,
            safety_risk=65.0,
            overdue_days=2,
            estimated_duration_min=75,
            crew_required=2,
            resource_requirements=["LADDER_TROLLEY"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=80.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-005",
            department=Department.ENGINEERING,
            asset_id="TRK-NG-008",
            asset_type="RAIL_JOINT",
            corridor_id="NDLS-GZB",
            location="KM 8/5",
            defect_type="GLUED_INSULATED_JOINT_FAILURE",
            severity=Severity.CRITICAL,
            criticality=91.0,
            safety_risk=89.0,
            overdue_days=7,
            estimated_duration_min=110,
            crew_required=3,
            resource_requirements=["INSULATED_JOINT_KIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=85.0,
        ),
        MaintenanceTask(
            task_id="TASK-SNT-003",
            department=Department.S_AND_T,
            asset_id="SIG-NG-014",
            asset_type="SIGNAL_ASPECT",
            corridor_id="NDLS-GZB",
            location="KM 10/2",
            defect_type="LED_SIGNAL_LAMP_LUX_DROP",
            severity=Severity.MINOR,
            criticality=45.0,
            safety_risk=40.0,
            overdue_days=1,
            estimated_duration_min=45,
            crew_required=2,
            resource_requirements=["OPTICAL_LUXMETER"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=60.0,
        ),
        MaintenanceTask(
            task_id="TASK-TRD-004",
            department=Department.TRD,
            asset_id="OHE-NG-022",
            asset_type="DROPPER_WIRE",
            corridor_id="NDLS-GZB",
            location="KM 14/0-15/0",
            defect_type="CURRENT_CARRYING_DROPPER_REPLACEMENT",
            severity=Severity.ROUTINE,
            criticality=35.0,
            safety_risk=30.0,
            overdue_days=0,
            estimated_duration_min=60,
            crew_required=2,
            resource_requirements=["CRIMPING_TOOL"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=50.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-006",
            department=Department.ENGINEERING,
            asset_id="TRK-KP-210",
            asset_type="CURVE_TRACK",
            corridor_id="KYN-PUN",
            location="KM 88/0",
            defect_type="CURVE_WEAR_RAIL_LUBRICATION",
            severity=Severity.ROUTINE,
            criticality=30.0,
            safety_risk=25.0,
            overdue_days=0,
            estimated_duration_min=50,
            crew_required=2,
            resource_requirements=["LUBRICATOR_CART"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=40.0,
        ),
        MaintenanceTask(
            task_id="TASK-SNT-004",
            department=Department.S_AND_T,
            asset_id="SIG-KP-315",
            asset_type="TRACK_CIRCUIT",
            corridor_id="KYN-PUN",
            location="KM 92/4",
            defect_type="RELAY_CONTACT_RESISTANCE_CHECK",
            severity=Severity.MINOR,
            criticality=50.0,
            safety_risk=45.0,
            overdue_days=1,
            estimated_duration_min=60,
            crew_required=2,
            resource_requirements=["MULTIMETER"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=55.0,
        ),
        MaintenanceTask(
            task_id="TASK-TRD-005",
            department=Department.TRD,
            asset_id="OHE-KP-420",
            asset_type="TENSION_BALANCER",
            corridor_id="KYN-PUN",
            location="KM 96/1",
            defect_type="AUTO_TENSIONING_PULLEY_CLEANING",
            severity=Severity.ROUTINE,
            criticality=38.0,
            safety_risk=30.0,
            overdue_days=0,
            estimated_duration_min=55,
            crew_required=2,
            resource_requirements=["GREASING_KIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=45.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-007",
            department=Department.ENGINEERING,
            asset_id="TRK-CK-044",
            asset_type="EXPANSION_JOINT",
            corridor_id="CSTM-KYN",
            location="KM 32/8",
            defect_type="SWITCH_EXPANSION_JOINT_GAP_ADJUSTMENT",
            severity=Severity.MAJOR,
            criticality=74.0,
            safety_risk=70.0,
            overdue_days=3,
            estimated_duration_min=90,
            crew_required=3,
            resource_requirements=["SEJ_TOOLKIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=75.0,
        ),
        MaintenanceTask(
            task_id="TASK-SNT-005",
            department=Department.S_AND_T,
            asset_id="SIG-CK-220",
            asset_type="INTEGRATED_POWER_SUPPLY",
            corridor_id="CSTM-KYN",
            location="KM 35/0",
            defect_type="IPS_BATTERY_BANK_VOLTAGE_IMBALANCE",
            severity=Severity.MINOR,
            criticality=55.0,
            safety_risk=45.0,
            overdue_days=2,
            estimated_duration_min=70,
            crew_required=2,
            resource_requirements=["BATTERY_TESTER"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=65.0,
        ),
        MaintenanceTask(
            task_id="TASK-ENG-008",
            department=Department.ENGINEERING,
            asset_id="TRK-NG-030",
            asset_type="TURNOUT",
            corridor_id="NDLS-GZB",
            location="KM 19/2",
            defect_type="TONGUE_RAIL_CHIPPING_REPAIR",
            severity=Severity.MAJOR,
            criticality=77.0,
            safety_risk=72.0,
            overdue_days=4,
            estimated_duration_min=100,
            crew_required=3,
            resource_requirements=["GRINDING_MACHINE"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=2),
            traffic_criticality=75.0,
        ),
    ]

    # -------------------------------------------------------------
    # STORY ELEMENT 10: EMERGENCY-TASK SCENARIO (FOR WHAT-IF DEMO)
    # Sudden transverse rail crack requiring immediate possession on KYN-PUN
    # -------------------------------------------------------------
    emergency_task = MaintenanceTask(
        task_id="EMERGENCY-ENG-999",
        department=Department.ENGINEERING,
        asset_id="TRK-KP-118",
        asset_type="RAIL_TRACK",
        corridor_id="KYN-PUN",
        location="KM 118/6",
        defect_type="SUDDEN_TRANSVERSE_RAIL_CRACK",
        severity=Severity.CRITICAL,
        criticality=100.0,
        safety_risk=100.0,
        overdue_days=0,
        estimated_duration_min=120,
        crew_required=4,
        resource_requirements=["EMERGENCY_CLAMP_KIT", "THERMIT_WELD_GEAR"],
        earliest_start=base_t,
        deadline=base_t + timedelta(days=1),
        traffic_criticality=95.0,
    )

    return tasks, block_windows, train_movements, goods_forecast, emergency_task


def generate_full_synthetic_dataset(seed: int = 42) -> Tuple[List[MaintenanceTask], List[BlockWindow], List[TrainMovement], List[GoodsForecast]]:
    """
    Generates a deterministic ~200 task realistic synthetic dataset across 12 corridors.
    """
    random.seed(seed)
    base_t = datetime(2026, 9, 1, 0, 0, 0)

    corridors = [
        "CSTM-KYN", "KYN-PUN", "NDLS-GZB", "HWH-BWN", "MAS-AJJ",
        "SBC-JTJ", "ADI-BRC", "SEC-KZJ", "NGP-WR", "PNBE-MGS",
        "BPL-ET", "LKO-CNB"
    ]

    departments = [Department.ENGINEERING, Department.S_AND_T, Department.TRD]
    
    tasks: List[MaintenanceTask] = []
    block_windows: List[BlockWindow] = []
    train_movements: List[TrainMovement] = []
    goods_forecast: List[GoodsForecast] = []

    block_id_counter = 1
    for corr in corridors:
        for day in range(3):
            # Night window (Low density)
            block_windows.append(BlockWindow(
                block_id=f"BLK-GEN-{block_id_counter:03d}",
                corridor_id=corr,
                start_time=base_t + timedelta(days=day, hours=1),
                end_time=base_t + timedelta(days=day, hours=5),
                available_capacity=4,
                resource_capacity=12,
                safety_constraints=["POWER_BLOCK_AVAILABLE", "TRAFFIC_BLOCK_GRANTED"],
                permitted_departments=departments,
                traffic_density=TrafficDensity.LOW,
            ))
            block_id_counter += 1

            # Day window (High density)
            block_windows.append(BlockWindow(
                block_id=f"BLK-GEN-{block_id_counter:03d}",
                corridor_id=corr,
                start_time=base_t + timedelta(days=day, hours=11),
                end_time=base_t + timedelta(days=day, hours=14),
                available_capacity=2,
                resource_capacity=8,
                safety_constraints=["TRAFFIC_BLOCK_GRANTED"],
                permitted_departments=[Department.ENGINEERING, Department.S_AND_T],
                traffic_density=TrafficDensity.HIGH,
            ))
            block_id_counter += 1

    train_counter = 1
    for corr in corridors:
        for day in range(3):
            train_movements.append(TrainMovement(
                train_id=f"TRN-{train_counter:04d}",
                corridor_id=corr,
                train_type=TrainType.VANDE_BHARAT if train_counter % 2 == 0 else TrainType.RAJDHANI_EXPRESS,
                direction=Direction.DOWN if train_counter % 2 == 0 else Direction.UP,
                start_time=base_t + timedelta(days=day, hours=11, minutes=30),
                end_time=base_t + timedelta(days=day, hours=12, minutes=30),
                operational_priority=1,
                disruption_penalty=750.0,
            ))
            train_counter += 1

            train_movements.append(TrainMovement(
                train_id=f"TRN-{train_counter:04d}",
                corridor_id=corr,
                train_type=TrainType.MAIL_EXPRESS,
                direction=Direction.UP,
                start_time=base_t + timedelta(days=day, hours=7),
                end_time=base_t + timedelta(days=day, hours=8, minutes=30),
                operational_priority=2,
                disruption_penalty=200.0,
            ))
            train_counter += 1

    for corr in corridors:
        for day in range(3):
            goods_forecast.append(GoodsForecast(
                corridor_id=corr,
                time_window=f"DAY_{day}_NIGHT",
                start_time=base_t + timedelta(days=day, hours=0),
                end_time=base_t + timedelta(days=day, hours=6),
                expected_goods_trains=random.randint(1, 3),
                probability=0.7,
                traffic_density=TrafficDensity.LOW,
            ))
            goods_forecast.append(GoodsForecast(
                corridor_id=corr,
                time_window=f"DAY_{day}_PEAK",
                start_time=base_t + timedelta(days=day, hours=9),
                end_time=base_t + timedelta(days=day, hours=17),
                expected_goods_trains=random.randint(4, 9),
                probability=0.9,
                traffic_density=TrafficDensity.HIGH,
            ))

    severities = [Severity.CRITICAL] * 15 + [Severity.MAJOR] * 35 + [Severity.MINOR] * 30 + [Severity.ROUTINE] * 20

    task_types = {
        Department.ENGINEERING: [
            ("RAIL_TRACK", "RAIL_FRACTURE_REPAIR", 120, 4),
            ("TURNOUT", "POINT_CROSSING_TAMPING", 90, 3),
            ("BALLAST", "BALLAST_CLEANING", 150, 6),
            ("EXPANSION_JOINT", "SEJ_GAP_ADJUSTMENT", 80, 2),
            ("TRACK_STRUCTURE", "RAIL_RENEWAL", 140, 5),
        ],
        Department.S_AND_T: [
            ("POINT_MACHINE", "POINT_OVERHAUL", 90, 2),
            ("AXLE_COUNTER", "DAC_CALIBRATION", 60, 2),
            ("SIGNAL_POST", "ASPECT_REPLACEMENT", 45, 2),
            ("TRACK_CIRCUIT", "BONDING_INSPECTION", 60, 2),
            ("RELAY_RACK", "RELAY_CONTACT_TESTING", 75, 2),
        ],
        Department.TRD: [
            ("OHE_WIRE", "CONTACT_WIRE_ADJUSTMENT", 100, 3),
            ("INSULATOR", "INSULATOR_REPLACEMENT", 75, 2),
            ("ISOLATOR", "ISOLATOR_MAINTENANCE", 90, 3),
            ("CANTILEVER", "BRACKET_INSPECTION", 80, 2),
            ("AUTO_TENSIONER", "ATD_WEIGHT_CHECK", 60, 2),
        ],
    }

    for i in range(1, 201):
        dept = random.choice(departments)
        corr = random.choice(corridors)
        sev = random.choice(severities)
        asset_type, defect_type, dur_base, crew_base = random.choice(task_types[dept])

        if sev == Severity.CRITICAL:
            crit = random.uniform(85.0, 98.0)
            safety = random.uniform(85.0, 99.0)
            overdue = random.randint(4, 15)
        elif sev == Severity.MAJOR:
            crit = random.uniform(65.0, 84.0)
            safety = random.uniform(60.0, 80.0)
            overdue = random.randint(1, 6)
        elif sev == Severity.MINOR:
            crit = random.uniform(40.0, 64.0)
            safety = random.uniform(35.0, 55.0)
            overdue = random.randint(0, 3)
        else:
            crit = random.uniform(20.0, 39.0)
            safety = random.uniform(15.0, 30.0)
            overdue = 0

        tasks.append(MaintenanceTask(
            task_id=f"TASK-GEN-{i:04d}",
            department=dept,
            asset_id=f"AST-{corr[:3]}-{i:03d}",
            asset_type=asset_type,
            corridor_id=corr,
            location=f"KM {random.randint(10, 250)}/{random.randint(0, 9)}",
            defect_type=defect_type,
            severity=sev,
            criticality=round(crit, 1),
            safety_risk=round(safety, 1),
            overdue_days=overdue,
            estimated_duration_min=dur_base + random.choice([-15, 0, 15]),
            crew_required=crew_base,
            resource_requirements=["STANDARD_TOOLKIT"],
            earliest_start=base_t,
            deadline=base_t + timedelta(days=random.randint(2, 5)),
            traffic_criticality=round(random.uniform(40.0, 95.0), 1),
        ))

    return tasks, block_windows, train_movements, goods_forecast
