"""
IBPS Domain Enums
Categorical enums for departments, severities, priority bands, train types, solver statuses.
"""

from enum import Enum


class Department(str, Enum):
    ENGINEERING = "ENGINEERING"
    S_AND_T = "S&T"
    TRD = "TRD"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    ROUTINE = "ROUTINE"


class PriorityBand(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    ROUTINE = "ROUTINE"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    UNSCHEDULED = "UNSCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TrainType(str, Enum):
    VANDE_BHARAT = "VANDE_BHARAT"
    RAJDHANI_EXPRESS = "RAJDHANI_EXPRESS"
    MAIL_EXPRESS = "MAIL_EXPRESS"
    PASSENGER = "PASSENGER"
    FREIGHT = "FREIGHT"


class Direction(str, Enum):
    UP = "UP"
    DOWN = "DOWN"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class TrafficDensity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SolverStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    TIMEOUT = "TIMEOUT"
    MODEL_INVALID = "MODEL_INVALID"
    UNKNOWN = "UNKNOWN"


class PlanHorizon(str, Enum):
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
