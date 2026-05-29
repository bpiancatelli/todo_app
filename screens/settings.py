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
                text: "Heure de réinitialisation des cases"
                font_style: "Headline"
                role: "small"
                theme_text_color: "Custom"
                text_color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: "40dp"

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "64dp"
                spacing: "12dp"

                MDTextField:
                    id: field_hour
                    hint_text: "Heure (0-23)"
                    mode: "outlined"
                    input_filter: "int"
                    size_hint_x: 0.45

                MDTextField:
                    id: field_minute
                    hint_text: "Minute (0-59)"
                    mode: "outlined"
                    input_filter: "int"
                    size_hint_x: 0.45

            MDButton:
                style: "filled"
                size_hint_x: None
                width: "180dp"
                md_bg_color: 0.2, 0.5, 0.9, 1
                on_release: root.save_settings()
                MDButtonText:
                    text: "Enregistrer"

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

    def on_enter(self):
        Clock.schedule_once(self._load_settings)

    def _load_settings(self, dt):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        settings = app.store.get("settings")
        self.ids.field_hour.text = str(settings.get("reset_hour", 0))
        self.ids.field_minute.text = str(settings.get("reset_minute", 0))
        self.ids.status_label.text = ""

    def save_settings(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        try:
            hour = max(0, min(23, int(self.ids.field_hour.text or "0")))
            minute = max(0, min(59, int(self.ids.field_minute.text or "0")))
        except ValueError:
            self.ids.status_label.text = "Valeurs invalides."
            return

        settings = app.store.get("settings")
        settings["reset_hour"] = hour
        settings["reset_minute"] = minute
        app.store.put("settings", **settings)
        self.ids.field_hour.text = str(hour)
        self.ids.field_minute.text = str(minute)
        self.ids.status_label.text = f"Sauvegardé : reset à {hour:02d}:{minute:02d}"
