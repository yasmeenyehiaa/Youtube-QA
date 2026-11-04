import json
import threading
from app.config import DATA_DIR

path = DATA_DIR / "videos.json"
lock = threading.Lock()


def load() -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def save(data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))


def list_videos() -> list[dict]:
    return list(load().values())


def get_video(video_id: str) -> dict | None:
    return load().get(video_id)


def put_video(record: dict) -> None:
    with lock:
        data = load()
        data[record["video_id"]] = record
        save(data)


def remove_video(video_id: str) -> None:
    with lock:
        data = load()
        data.pop(video_id, None)
        save(data)
