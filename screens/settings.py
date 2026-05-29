from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen

Builder.load_string("""
<SettingsScreen>:
    FloatLayout:
        NotepadBackground:
            size_hint: 1, 1
            pos: 0, 0

        BoxLayout:
            orientation: "vertical"
            size_hint: 1, 1
            padding: ["80dp", "16dp", "16dp", "16dp"]
            spacing: "16dp"

            MDTopAppBar:
                MDTopAppBarLeadingButtonContainer:
                    MDActionTopAppBarButton:
                        icon: "arrow-left"
                        on_release: setattr(app.root, 'current', 'home')
                MDTopAppBarTitle:
                    text: "Paramètres"

            MDLabel:
                text: "Réinitialisation quotidienne des cases"
                font_style: "Headline"
                role: "small"
                theme_text_color: "Custom"
                text_color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: "40dp"

            MDLabel:
                id: time_display
                text: "Heure : 00:00"
                font_style: "Body"
                role: "large"
                theme_text_color: "Custom"
                text_color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: "36dp"

            MDButton:
                style: "tonal"
                size_hint_x: None
                width: "220dp"
                on_release: root.open_time_picker()
                MDButtonText:
                    text: "Choisir l'heure de reset"

            MDLabel:
                id: status_label
                text: ""
                theme_text_color: "Custom"
                text_color: 0.2, 0.6, 0.2, 1
                size_hint_y: None
                height: "32dp"

            Widget:
""")

from widgets.notepad_background import NotepadBackground  # noqa: F401


class SettingsScreen(MDScreen):
    _time_picker = None

    def on_enter(self):
        Clock.schedule_once(self._load_settings)

    def _load_settings(self, dt):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        settings = app.store.get("settings")
        h = settings.get("reset_hour", 0)
        m = settings.get("reset_minute", 0)
        self.ids.time_display.text = f"Heure : {h:02d}:{m:02d}"
        self.ids.status_label.text = ""

    def open_time_picker(self):
        from kivymd.app import MDApp
        from kivymd.uix.pickers.timepicker import MDTimePickerDialVertical
        from datetime import time

        app = MDApp.get_running_app()
        settings = app.store.get("settings")
        h = settings.get("reset_hour", 0)
        m = settings.get("reset_minute", 0)

        self._time_picker = MDTimePickerDialVertical(time=time(h, m))
        self._time_picker.bind(
            on_ok=self._on_time_ok,
            on_cancel=lambda *_: self._time_picker.dismiss(),
        )
        self._time_picker.open()

    def _on_time_ok(self, picker, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        t = picker.time
        settings = app.store.get("settings")
        settings["reset_hour"] = t.hour
        settings["reset_minute"] = t.minute
        # Clear last_reset_at so the new time can trigger tonight
        settings.pop("last_reset_at", None)
        app.store.put("settings", **settings)
        self.ids.time_display.text = f"Heure : {t.hour:02d}:{t.minute:02d}"
        self.ids.status_label.text = f"Sauvegardé : reset à {t.hour:02d}:{t.minute:02d}"
        picker.dismiss()
