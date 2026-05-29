from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp

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
                title: "Paramètres"
                elevation: 0
                md_bg_color: 0, 0, 0, 0
                specific_text_color: 0.15, 0.15, 0.15, 1
                left_action_items: [["arrow-left", lambda x: setattr(app.root, 'current', 'home')]]

            MDLabel:
                text: "Heure de réinitialisation des cases"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0.15, 0.15, 0.15, 1
                size_hint_y: None
                height: "40dp"

            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: "56dp"
                spacing: "12dp"

                MDTextField:
                    id: field_hour
                    hint_text: "Heure (0-23)"
                    mode: "rectangle"
                    input_filter: "int"
                    size_hint_x: 0.45

                MDTextField:
                    id: field_minute
                    hint_text: "Minute (0-59)"
                    mode: "rectangle"
                    input_filter: "int"
                    size_hint_x: 0.45

            MDRaisedButton:
                text: "Enregistrer"
                size_hint_x: None
                width: "180dp"
                md_bg_color: 0.2, 0.5, 0.9, 1
                on_release: root.save_settings()

            MDLabel:
                id: status_label
                text: ""
                theme_text_color: "Custom"
                text_color: 0.2, 0.6, 0.2, 1
                size_hint_y: None
                height: "32dp"

            Widget:
""")

from widgets.notepad_background import NotepadBackground  # noqa: F401 — registers widget


class SettingsScreen(MDScreen):

    def on_enter(self):
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
            hour = int(self.ids.field_hour.text or "0")
            minute = int(self.ids.field_minute.text or "0")
            hour = max(0, min(23, hour))
            minute = max(0, min(59, minute))
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
