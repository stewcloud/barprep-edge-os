import uvicorn

from .config import settings
from .state import ensure_identity


def main() -> None:
    ensure_identity()
    uvicorn.run(
        "barprep_edge.web.app:app",
        host=settings.bind,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
