from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
import uuid

from widgets.notepad_background import NotepadBackground  # noqa: F401 — registers widget for KV
from widgets.task_item import TaskItem  # noqa: F401

Builder.load_string("""
<HomeScreen>:
    FloatLayout:
        NotepadBackground:
            size_hint: 1, 1
            pos: 0, 0

        BoxLayout:
            orientation: "vertical"
            size_hint: 1, 1

            MDTopAppBar:
                title: "Ma Todo List"
                elevation: 0
                md_bg_color: 0, 0, 0, 0
                specific_text_color: 0.15, 0.15, 0.15, 1
                right_action_items: [["cog-outline", lambda x: app.root.current.__setattr__('dummy', '') or setattr(app.root, 'current', 'settings')]]

            ScrollView:
                id: scroll
                do_scroll_x: False

                BoxLayout:
                    id: task_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, "8dp", 0, "80dp"]

        MDFloatingActionButton:
            icon: "plus"
            pos_hint: {"right": 0.96, "y": 0.04}
            md_bg_color: 0.2, 0.5, 0.9, 1
            on_release: root.open_add_dialog()
""")

DAYS = [
    (None, "Tous les jours"),
    (0, "Lundi"), (1, "Mardi"), (2, "Mercredi"), (3, "Jeudi"),
    (4, "Vendredi"), (5, "Samedi"), (6, "Dimanche"),
]


class HomeScreen(MDScreen):
    dialog = None
    day_dialog = None
    _pending_day = None

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.refresh_tasks())

    def refresh_tasks(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        task_list = self.ids.task_list
        task_list.clear_widgets()
        for task in app.get_tasks_for_today():
            item = TaskItem(
                text=task["text"],
                done=task.get("done", False),
                task_id=task["id"],
            )
            task_list.add_widget(item)

    def open_add_dialog(self):
        self._pending_day = None
        self._text_field = MDTextField(
            hint_text="Nouvelle tâche...",
            mode="rectangle",
        )
        self._day_label = MDLabel(
            text="Jour : Tous les jours",
            theme_text_color="Secondary",
            size_hint_y=None,
            height=dp(32),
        )
        day_btn = MDFlatButton(
            text="Choisir un jour",
            on_release=self._open_day_picker,
        )
        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(140),
            spacing=dp(8),
            padding=[dp(8), dp(8)],
        )
        content.add_widget(self._text_field)
        content.add_widget(self._day_label)
        content.add_widget(day_btn)

        self.dialog = MDDialog(
            title="Ajouter une tâche",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Annuler", on_release=self._close_dialog),
                MDRaisedButton(text="Ajouter", on_release=self._add_task),
            ],
        )
        self.dialog.open()

    def _open_day_picker(self, *_):
        from kivymd.uix.list import MDList, OneLineListItem
        items = MDList()
        for day_val, day_name in DAYS:
            item = OneLineListItem(
                text=day_name,
                on_release=lambda x, d=day_val, n=day_name: self._select_day(d, n),
            )
            items.add_widget(item)

        scroll = ScrollView(size_hint=(1, None), height=dp(300))
        scroll.add_widget(items)

        self.day_dialog = MDDialog(
            title="Choisir un jour",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(text="Fermer", on_release=lambda x: self.day_dialog.dismiss()),
            ],
        )
        self.day_dialog.open()

    def _select_day(self, day_val, day_name):
        self._pending_day = day_val
        self._day_label.text = f"Jour : {day_name}"
        if self.day_dialog:
            self.day_dialog.dismiss()

    def _add_task(self, *_):
        text = self._text_field.text.strip()
        if not text:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        new_id = int(uuid.uuid4().int % 1_000_000)
        tasks.append({
            "id": new_id,
            "text": text,
            "done": False,
            "day": self._pending_day,
        })
        app.save_tasks(tasks)
        self._close_dialog()
        self.refresh_tasks()

    def _close_dialog(self, *_):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = None
