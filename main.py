import os

# Disable SDL2 sensor subsystem — triggers Samsung HWUI race condition on startup
os.environ['SDL_HINT_ANDROID_SEPARATE_MOUSE_AND_TOUCH'] = '1'
os.environ['SDL_HINT_JOYSTICK_ALLOW_BACKGROUND_EVENTS'] = '0'
os.environ['KIVY_NO_ENV_CONFIG'] = '1'

import traceback
from kivymd.app import MDApp

KV = """
ScreenManager:
    HomeScreen:
        name: "home"
    SettingsScreen:
        name: "settings"
"""


class TodoApp(MDApp):
    def build(self):
        try:
            return self._build()
        except Exception:
            err = traceback.format_exc()
            try:
                with open(os.path.join(self.user_data_dir, "crash.log"), "w") as f:
                    f.write(err)
            except Exception:
                pass
            from kivy.uix.label import Label
            from kivy.uix.scrollview import ScrollView
            sv = ScrollView()
            lbl = Label(text=err, font_size="11sp", size_hint_y=None,
                        text_size=(800, None), halign="left")
            lbl.bind(texture_size=lambda w, s: setattr(w, "size", s))
            sv.add_widget(lbl)
            return sv

    def _build(self):
        from kivy.lang import Builder
        from kivy.clock import Clock
        from kivy.storage.jsonstore import JsonStore
        from datetime import datetime
        from screens.home import HomeScreen   # noqa: F401
        from screens.settings import SettingsScreen  # noqa: F401

        self.theme_cls.theme_style = "Light"
        self.store = JsonStore(os.path.join(self.user_data_dir, "tasks.json"))
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
        from datetime import datetime
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
        from datetime import datetime
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
        try:
            from android import AndroidService
            service = AndroidService("Todo Notification", "Surveillance des rappels")
            service.start("started")
            self._android_service = service
        except ImportError:
            pass

    # ── Data helpers ──────────────────────────────────────────────────

    def get_tasks_for_today(self):
        from datetime import datetime
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
    from kivy.core.window import Window
    Window.keyboard_anim_args = {"d": 0.2, "t": "in_out_expo"}
    TodoApp().run()
