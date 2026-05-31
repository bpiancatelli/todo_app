from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen

Builder.load_string("""
<SettingsScreen>:
    FloatLayout:
        NotepadBackground:
            size_hint: 1, 1
            pos: 0, 0

        ScrollView:
            size_hint: 1, 1

            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: ["80dp", "16dp", "16dp", "24dp"]
                spacing: "20dp"

                MDTopAppBar:
                    size_hint_y: None
                    height: "64dp"
                    MDTopAppBarLeadingButtonContainer:
                        MDActionTopAppBarButton:
                            icon: "arrow-left"
                            on_release: setattr(app.root, 'current', 'home')
                    MDTopAppBarTitle:
                        text: "Paramètres"

                # ── Section reset ─────────────────────────────────────
                MDLabel:
                    text: "Réinitialisation quotidienne"
                    font_style: "Headline"
                    role: "small"
                    theme_text_color: "Custom"
                    text_color: 0.15, 0.15, 0.15, 1
                    size_hint_y: None
                    height: "36dp"

                MDLabel:
                    id: reset_time_display
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
                    on_release: root.open_reset_picker()
                    MDButtonText:
                        text: "Choisir l'heure de reset"

                # ── Section notification ──────────────────────────────
                MDDivider:
                    size_hint_y: None
                    height: "1dp"

                MDLabel:
                    text: "Notification de rappel"
                    font_style: "Headline"
                    role: "small"
                    theme_text_color: "Custom"
                    text_color: 0.15, 0.15, 0.15, 1
                    size_hint_y: None
                    height: "36dp"

                BoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "36dp"
                    spacing: "12dp"

                    MDLabel:
                        text: "Activer la notification"
                        font_style: "Body"
                        role: "large"
                        theme_text_color: "Custom"
                        text_color: 0.15, 0.15, 0.15, 1

                    MDSwitch:
                        id: notif_switch
                        pos_hint: {"center_y": 0.5}
                        on_active: root.on_notif_toggle(self.active)

                MDLabel:
                    id: notif_time_display
                    text: "Heure : 21:00"
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
                    on_release: root.open_notif_picker()
                    MDButtonText:
                        text: "Choisir l'heure de rappel"

                MDLabel:
                    id: status_label
                    text: ""
                    theme_text_color: "Custom"
                    text_color: 0.2, 0.6, 0.2, 1
                    size_hint_y: None
                    height: "32dp"
""")

from widgets.notepad_background import NotepadBackground  # noqa: F401


class SettingsScreen(MDScreen):
    _reset_picker = None
    _notif_picker = None

    def on_enter(self):
        Clock.schedule_once(self._load_settings)

    def _load_settings(self, dt):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        s = app.store.get("settings")

        rh = s.get("reset_hour", 0)
        rm = s.get("reset_minute", 0)
        self.ids["reset_time_display"].text = f"Heure : {rh:02d}:{rm:02d}"

        nh = s.get("notif_hour", 21)
        nm = s.get("notif_minute", 0)
        self.ids["notif_time_display"].text = f"Heure : {nh:02d}:{nm:02d}"
        self.ids["notif_switch"].active = s.get("notif_enabled", False)
        self.ids["status_label"].text = ""

    # ── Reset time picker ─────────────────────────────────────────────

    def open_reset_picker(self):
        from kivymd.app import MDApp
        from kivymd.uix.pickers.timepicker import MDTimePickerDialVertical
        from datetime import time

        app = MDApp.get_running_app()
        s = app.store.get("settings")
        self._reset_picker = MDTimePickerDialVertical(
            time=time(s.get("reset_hour", 0), s.get("reset_minute", 0))
        )
        self._reset_picker.bind(
            on_ok=self._on_reset_ok,
            on_cancel=lambda *_: self._reset_picker.dismiss(),
        )
        self._reset_picker.open()

    def _on_reset_ok(self, picker, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        t = picker.time
        s = app.store.get("settings")
        s["reset_hour"] = t.hour
        s["reset_minute"] = t.minute
        s.pop("last_reset_at", None)
        app.store.put("settings", **s)
        self.ids["reset_time_display"].text = f"Heure : {t.hour:02d}:{t.minute:02d}"
        self.ids["status_label"].text = f"Reset sauvegardé : {t.hour:02d}:{t.minute:02d}"
        picker.dismiss()

    # ── Notification toggle & picker ──────────────────────────────────

    def on_notif_toggle(self, active):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        s = app.store.get("settings")
        s["notif_enabled"] = active
        app.store.put("settings", **s)
        if active:
            app.start_notification_service()
        self.ids["status_label"].text = (
            "Notification activée" if active else "Notification désactivée"
        )

    def open_notif_picker(self):
        from kivymd.app import MDApp
        from kivymd.uix.pickers.timepicker import MDTimePickerDialVertical
        from datetime import time

        app = MDApp.get_running_app()
        s = app.store.get("settings")
        self._notif_picker = MDTimePickerDialVertical(
            time=time(s.get("notif_hour", 21), s.get("notif_minute", 0))
        )
        self._notif_picker.bind(
            on_ok=self._on_notif_ok,
            on_cancel=lambda *_: self._notif_picker.dismiss(),
        )
        self._notif_picker.open()

    def _on_notif_ok(self, picker, *_):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        t = picker.time
        s = app.store.get("settings")
        s["notif_hour"] = t.hour
        s["notif_minute"] = t.minute
        s.pop("last_notif_at", None)
        app.store.put("settings", **s)
        self.ids["notif_time_display"].text = f"Heure : {t.hour:02d}:{t.minute:02d}"
        self.ids["status_label"].text = f"Rappel sauvegardé : {t.hour:02d}:{t.minute:02d}"
        picker.dismiss()
