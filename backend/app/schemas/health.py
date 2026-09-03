"""
Pydantic Schemas - Health & System Status.
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="ok", description="Service health status")
    system: str = Field(default="IBPS", description="Integrated Block Planning System")
    version: str = Field(default="1.0.0", description="API version")
    data_mode: str = Field(default="synthetic", description="Indicates synthetic/demo data mode")
    description: str = Field(
        default="AI-Powered Automatic Block Planning to Maximize Asset Availability for Train Operations on Indian Railways",
        description="SIH Problem Statement 26027 Summary"
    )
    human_in_the_loop_notice: str = Field(
        default="IBPS provides AI-assisted decision support for maintenance block planning. Final approval and override remain with authorized railway personnel.",
        description="Permanent architectural positioning statement"
    )
