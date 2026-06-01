"""
Android background service — started by AlarmManager at the scheduled time.
Sends the notification, reschedules for tomorrow, then stops itself.
"""
import os
import sys
from datetime import datetime

_service_dir = os.path.dirname(os.path.abspath(__file__))
_app_root = os.path.dirname(_service_dir)
if _app_root not in sys.path:
    sys.path.insert(0, _app_root)

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
    _log(f"Service started (alarm trigger). app_root={_app_root}")

    try:
        settings = _load_settings()
        enabled = settings.get("notif_enabled", False)
        notif_hour = settings.get("notif_hour", 21)
        notif_minute = settings.get("notif_minute", 0)

        _log(f"Settings: enabled={enabled}, time={notif_hour:02d}:{notif_minute:02d}")

        if enabled:
            now = datetime.now()
            _log("Sending notification...")
            from utils.notify import send_notification
            ok = send_notification(
                title="Todo List",
                message="As-tu bien tout coche avant de dormir ?",
            )
            _log(f"send_notification returned: {ok}")
            if ok:
                _mark_notified(now)

        # Reschedule for tomorrow regardless of whether notification was sent
        if enabled:
            _log(f"Rescheduling alarm for {notif_hour:02d}:{notif_minute:02d} tomorrow...")
            try:
                from jnius import autoclass
                context = autoclass('org.kivy.android.PythonService').mService
                if context is not None:
                    from utils.alarm import schedule_alarm
                    scheduled = schedule_alarm(context, notif_hour, notif_minute)
                    _log(f"Alarm rescheduled: {scheduled}")
                else:
                    _log("ERROR: PythonService.mService is None, cannot reschedule")
            except Exception as e:
                _log(f"Reschedule error: {e}")

    except Exception as e:
        _log(f"Service error: {e}")

    # Stop the service — it's a one-shot, not a loop
    try:
        from jnius import autoclass
        svc = autoclass('org.kivy.android.PythonService').mService
        if svc is not None:
            svc.stopSelf()
            _log("Service stopped itself")
    except Exception as e:
        _log(f"stopSelf error: {e}")
