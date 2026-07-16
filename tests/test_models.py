from barprep_edge.models import (
    CanvasReference,
    JobPrintOptions,
    JobStatus,
    JobStatusUpdate,
    PrintJob,
)


def test_print_job_contract() -> None:
    job = PrintJob(
        job_id="job_1",
        station_id="station_prep",
        output_id=None,
        canvas=CanvasReference(
            canvas_id="canvas_1",
            sha256="abc123",
            download_url="https://example.com/canvas/1",
            width_mm=62,
            height_mm=32,
        ),
        print=JobPrintOptions(copies=2, cut=True),
        created_at="2026-07-16T04:03:00Z",
    )

    assert job.print.copies == 2
    assert job.canvas.format == "image/png"


def test_failed_job_status() -> None:
    update = JobStatusUpdate(
        status=JobStatus.FAILED,
        error_code="printer_not_found",
        detail="Printer disconnected",
    )

    assert update.status == JobStatus.FAILED
    assert update.error_code == "printer_not_found"
