from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    CLAIMED = "claimed"
    DOWNLOADING = "downloading"
    PRINTING = "printing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class MediaInfo(BaseModel):
    label: str
    description: str


class OutputStatus(BaseModel):
    output_id: str
    type: str = "label-printer"
    driver: str
    manufacturer: str
    model: str
    connection: str
    ready: bool
    media: MediaInfo | None = None
    detail: str = ""


class RegistrationRequest(BaseModel):
    device_id: str
    device_public_name: str
    runtime_version: str
    os_version: str
    capabilities: list[str]


class RegistrationResponse(BaseModel):
    registration_id: str
    pairing_code: str = Field(min_length=4, max_length=4)
    expires_at: str
    poll_after_seconds: int = Field(ge=1, le=60)


class JobPrintOptions(BaseModel):
    copies: int = Field(default=1, ge=1, le=25)
    cut: bool = True


class CanvasReference(BaseModel):
    canvas_id: str
    format: str = "image/png"
    sha256: str
    download_url: str
    width_mm: int
    height_mm: int
    dpi: int = 300


class PrintJob(BaseModel):
    job_id: str
    station_id: str
    output_id: str | None = None
    canvas: CanvasReference
    print: JobPrintOptions
    created_at: str


class JobStatusUpdate(BaseModel):
    status: JobStatus
    attempt: int = Field(default=1, ge=1)
    output_id: str | None = None
    error_code: str | None = None
    detail: str = ""
    completed_at: str | None = None
