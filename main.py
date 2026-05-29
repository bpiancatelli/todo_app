from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from datetime import datetime, time as dtime
import os

from screens.home import HomeScreen
from screens.settings import SettingsScreen

KV = """
ScreenManager:
    HomeScreen:
        name: "home"
    SettingsScreen:
        name: "settings"
"""

DAYS_MAP = {
    0: "Lundi", 1: "Mardi", 2: "Mercredi", 3: "Jeudi",
    4: "Vendredi", 5: "Samedi", 6: "Dimanche"
}


class TodoApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.store = JsonStore("tasks.json")
        self._ensure_defaults()
        self.root = Builder.load_string(KV)
        self._schedule_reset()
        Clock.schedule_interval(self._check_reset, 60)
        return self.root

    def _ensure_defaults(self):
        if not self.store.exists("settings"):
            self.store.put("settings", reset_hour=0, reset_minute=0)
        if not self.store.exists("tasks"):
            self.store.put("tasks", items=[])

    def _schedule_reset(self):
        self._last_reset_date = self.store.get("settings").get(
            "last_reset_date", ""
        )

    def _check_reset(self, dt):
        settings = self.store.get("settings")
        reset_h = settings.get("reset_hour", 0)
        reset_m = settings.get("reset_minute", 0)
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        reset_time = dtime(reset_h, reset_m)
        last = settings.get("last_reset_date", "")

        if now.time() >= reset_time and last != today_str:
            self._do_reset(today_str)

    def _do_reset(self, today_str):
        data = self.store.get("tasks")
        items = data.get("items", [])
        for task in items:
            task["done"] = False
        self.store.put("tasks", items=items)
        settings = self.store.get("settings")
        settings["last_reset_date"] = today_str
        self.store.put("settings", **settings)
        home = self.root.get_screen("home")
        home.refresh_tasks()

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
