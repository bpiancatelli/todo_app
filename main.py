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
        return self.root

    def _ensure_defaults(self):
        if not self.store.exists("settings"):
            self.store.put("settings", reset_hour=0, reset_minute=0)
        if not self.store.exists("tasks"):
            self.store.put("tasks", items=[])

    def _check_reset(self, dt):
        settings = self.store.get("settings")
        reset_h = settings.get("reset_hour", 0)
        reset_m = settings.get("reset_minute", 0)
        now = datetime.now()

        # Datetime of the scheduled reset for today
        scheduled = now.replace(
            hour=reset_h, minute=reset_m, second=0, microsecond=0
        )

        last_str = settings.get("last_reset_at", "")
        try:
            last_reset = datetime.fromisoformat(last_str)
        except (ValueError, TypeError):
            last_reset = datetime.min

        # Reset if we've passed today's scheduled time and haven't reset since
        if now >= scheduled and last_reset < scheduled:
            self._do_reset(now)

    def _do_reset(self, now: datetime):
        data = self.store.get("tasks")
        items = data.get("items", [])
        for task in items:
            task["done"] = False
        self.store.put("tasks", items=items)

        settings = self.store.get("settings")
        settings["last_reset_at"] = now.isoformat()
        self.store.put("settings", **settings)

        # Refresh UI if home screen is active
        try:
            home = self.root.get_screen("home")
            home.refresh_tasks()
        except Exception:
            pass

    def get_tasks_for_today(self):
        weekday = datetime.now().weekday()
        data = self.store.get("tasks")
        items = data.get("items", [])
        return [
            t for t in items
            if t.get("day") is None or t.get("day") == weekday
        ]

    def save_tasks(self, items):
        self.store.put("tasks", items=items)

    def get_all_tasks(self):
        return self.store.get("tasks").get("items", [])


if __name__ == "__main__":
    Window.keyboard_anim_args = {"d": 0.2, "t": "in_out_expo"}
    TodoApp().run()
