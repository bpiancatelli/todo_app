"""
Android background service — runs even when the app is closed.
Checks every 30s if it's time to send the notification.
"""
import os
import sys
import time
from datetime import datetime

# Build app root from __file__ — reliable regardless of env vars
_service_dir = os.path.dirname(os.path.abspath(__file__))
_app_root = os.path.dirname(_service_dir)
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

# ANDROID_PRIVATE = getFilesDir() = same path as MDApp.user_data_dir
_storage = os.environ.get('ANDROID_PRIVATE', os.path.expanduser('~'))
STORE_PATH = os.path.join(_storage, 'tasks.json')
SERVICE_LOG = os.path.join(_storage, 'service.log')


def _log(msg):
    try:
        with open(SERVICE_LOG, 'a') as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except Exception:
        pass


def _load_settings():
    import json
    try:
        with open(STORE_PATH) as f:
            data = json.load(f)
        return data.get("settings", {})
    except Exception as e:
        _log(f"load_settings error: {e}")
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


def _mark_notified(now):
    import json
    try:
        with open(STORE_PATH) as f:
            data = json.load(f)
        data.setdefault("settings", {})["last_notif_at"] = now.isoformat()
        with open(STORE_PATH, "w") as f:
            json.dump(data, f)
    except Exception as e:
        _log(f"mark_notified error: {e}")


if __name__ == "__main__":
    _log(f"Service started. app_root={_app_root}, store={STORE_PATH}")

    while True:
        try:
            now = datetime.now()
            settings = _load_settings()
            if _should_notify(settings, now):
                _log("Sending notification...")
                from utils.notify import send_notification
                ok = send_notification(
                    title="Todo List",
                    message="As-tu bien tout coche avant de dormir ?",
                )
                _log(f"send_notification returned: {ok}")
                if ok:
                    _mark_notified(now)
        except Exception as e:
            _log(f"Loop error: {e}")
        time.sleep(30)
