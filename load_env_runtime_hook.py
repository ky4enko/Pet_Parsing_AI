# PyInstaller runtime hook: load the complete, unchanged .env before app imports.
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv

    app_dir = Path(sys.executable).resolve().parent
    candidates = [
        app_dir / ".env",
        Path(getattr(sys, "_MEIPASS", app_dir)) / ".env",
    ]

    for env_path in candidates:
        if env_path.is_file():
            load_dotenv(dotenv_path=env_path, override=True)
            break
except Exception:
    # The application still has its own explicit load_dotenv calls.
    pass
