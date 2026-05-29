from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import datetime

from screens.home import HomeScreen
from screens.settings import SettingsScreen

KV = """
ScreenManager:
    HomeScreen:
        name: "home"
    SettingsScreen:
        name: "settings"
"""


class TodoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.store = JsonStore("tasks.json")
        self._ensure_defaults()
        self.root = Builder.load_string(KV)
        Clock.schedule_interval(self._check_reset, 30)
        Clock.schedule_interval(self._check_notification, 30)
        return self.root

    def _ensure_defaults(self):
        if not self.store.exists("settings"):
            self.store.put(
                "settings",
                reset_hour=0, reset_minute=0,
                notif_enabled=False, notif_hour=21, notif_minute=0,
            )
        if not self.store.exists("tasks"):
            self.store.put("tasks", items=[])

    # ── Reset ─────────────────────────────────────────────────────────

    def _check_reset(self, dt):
        s = self.store.get("settings")
        now = datetime.now()
        scheduled = now.replace(
            hour=s.get("reset_hour", 0),
            minute=s.get("reset_minute", 0),
            second=0, microsecond=0,
        )
        last_str = s.get("last_reset_at", "")
        try:
            last = datetime.fromisoformat(last_str)
        except (ValueError, TypeError):
            last = datetime.min

        if now >= scheduled and last < scheduled:
            self._do_reset(now)

    def _do_reset(self, now):
        data = self.store.get("tasks")
        items = data.get("items", [])
        for task in items:
            task["done"] = False
        self.store.put("tasks", items=items)

        s = self.store.get("settings")
        s["last_reset_at"] = now.isoformat()
        self.store.put("settings", **s)

        try:
            self.root.get_screen("home").refresh_tasks()
        except Exception:
            pass

    # ── Notification ──────────────────────────────────────────────────

    def _check_notification(self, dt):
        s = self.store.get("settings")
        if not s.get("notif_enabled", False):
            return

        now = datetime.now()
        scheduled = now.replace(
            hour=s.get("notif_hour", 21),
            minute=s.get("notif_minute", 0),
            second=0, microsecond=0,
        )
        last_str = s.get("last_notif_at", "")
        try:
            last = datetime.fromisoformat(last_str)
        except (ValueError, TypeError):
            last = datetime.min

        if now >= scheduled and last < scheduled:
            self._send_notification(now)

    def _send_notification(self, now):
        try:
            from plyer import notification
            notification.notify(
                title="Todo List",
                message="As-tu bien tout coché avant de dormir ? 🌙",
                app_name="Ma Todo List",
                timeout=10,
            )
        except Exception:
            pass

        s = self.store.get("settings")
        s["last_notif_at"] = now.isoformat()
        self.store.put("settings", **s)

    def start_notification_service(self):
        """Start Android background service for notifications when app is closed."""
        try:
            from android import AndroidService
            service = AndroidService("Todo Notification", "Surveillance des rappels")
            service.start("started")
            self._android_service = service
        except ImportError:
            pass  # Not on Android — Clock-based check handles it

    # ── Data helpers ──────────────────────────────────────────────────

    def get_tasks_for_today(self):
        weekday = datetime.now().weekday()
        data = self.store.get("tasks")
        return [
            t for t in data.get("items", [])
            if t.get("day") is None or t.get("day") == weekday
        ]

    def save_tasks(self, items):
        self.store.put("tasks", items=items)

    def get_all_tasks(self):
        return self.store.get("tasks").get("items", [])


if __name__ == "__main__":
    Window.keyboard_anim_args = {"d": 0.2, "t": "in_out_expo"}
    TodoApp().run()
