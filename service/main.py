"""
Android background service — runs even when the app is closed.
Checks every minute if it's time to send the notification.
"""
import time
import os
from datetime import datetime

from plyer import notification

# p4a sets ANDROID_PRIVATE to the app's getFilesDir() — same as MDApp.user_data_dir
_storage = os.environ.get('ANDROID_PRIVATE', os.path.expanduser('~'))
STORE_PATH = os.path.join(_storage, 'tasks.json')


def _load_settings():
    """Read settings from the JsonStore file without importing Kivy."""
    import json
    try:
        with open(STORE_PATH) as f:
            data = json.load(f)
        return data.get("settings", {})
    except Exception:
        return {}


def _should_notify(settings, now):
    h = settings.get("notif_hour")
    m = settings.get("notif_minute")
    enabled = settings.get("notif_enabled", False)
    if not enabled or h is None or m is None:
        return False

    scheduled = now.replace(hour=h, minute=m, second=0, microsecond=0)
    last_str = settings.get("last_notif_at", "")
    try:
        last = datetime.fromisoformat(last_str)
    except (ValueError, TypeError):
        last = datetime.min

    return now >= scheduled and last < scheduled


def _send_notification():
    try:
        notification.notify(
            title="Todo List",
            message="As-tu bien tout coché avant de dormir ? 🌙",
            app_name="Ma Todo List",
            timeout=10,
        )
    except Exception:
        pass


def _mark_notified(now):
    """Update last_notif_at in the store file."""
    import json
    try:
        with open(STORE_PATH) as f:
            data = json.load(f)
        data.setdefault("settings", {})["last_notif_at"] = now.isoformat()
        with open(STORE_PATH, "w") as f:
            json.dump(data, f)
    except Exception:
        pass


if __name__ == "__main__":
    # On Android, python-for-android keeps this loop alive as a Service
    try:
        from android import AndroidService  # noqa: F401 — android-only
    except ImportError:
        pass

    while True:
        now = datetime.now()
        settings = _load_settings()
        if _should_notify(settings, now):
            _send_notification()
            _mark_notified(now)
        time.sleep(60)
