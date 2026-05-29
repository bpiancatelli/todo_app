from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import (
    MDDialog, MDDialogHeadlineText,
    MDDialogContentContainer, MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText
import uuid

from widgets.notepad_background import NotepadBackground  # noqa: F401
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
                MDTopAppBarLeadingButtonContainer:
                MDTopAppBarTitle:
                    text: "Ma Todo List"
                MDTopAppBarTrailingButtonContainer:
                    MDActionTopAppBarButton:
                        icon: "cog-outline"
                        on_release: setattr(app.root, 'current', 'settings')

            ScrollView:
                id: scroll
                do_scroll_x: False

                BoxLayout:
                    id: task_list
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: [0, "8dp", 0, "80dp"]

        MDFabButton:
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
    _dialog = None
    _day_dialog = None
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
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
        )
        self._day_label = MDLabel(
            text="Jour : Tous les jours",
            size_hint_y=None,
            height=dp(32),
        )
        day_btn = MDButton(
            style="text",
            on_release=self._open_day_picker,
        )
        day_btn.add_widget(MDButtonText(text="Choisir un jour"))

        content = MDDialogContentContainer(orientation="vertical", spacing=dp(8))
        content.add_widget(self._text_field)
        content.add_widget(self._day_label)
        content.add_widget(day_btn)

        btn_cancel = MDButton(style="text", on_release=self._close_dialog)
        btn_cancel.add_widget(MDButtonText(text="Annuler"))
        btn_add = MDButton(style="filled", on_release=self._add_task)
        btn_add.add_widget(MDButtonText(text="Ajouter"))

        self._dialog = MDDialog(
            MDDialogHeadlineText(text="Ajouter une tâche"),
            content,
            MDDialogButtonContainer(btn_cancel, btn_add, spacing=dp(8)),
        )
        self._dialog.open()

    def _open_day_picker(self, *_):
        items_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=0,
        )
        items_box.bind(minimum_height=items_box.setter("height"))

        for day_val, day_name in DAYS:
            item = MDListItem(
                on_release=lambda x, d=day_val, n=day_name: self._select_day(d, n),
            )
            item.add_widget(MDListItemHeadlineText(text=day_name))
            items_box.add_widget(item)

        scroll = ScrollView(size_hint=(1, None), height=dp(300))
        scroll.add_widget(items_box)

        btn_close = MDButton(
            style="text",
            on_release=lambda x: self._day_dialog.dismiss(),
        )
        btn_close.add_widget(MDButtonText(text="Fermer"))

        self._day_dialog = MDDialog(
            MDDialogHeadlineText(text="Choisir un jour"),
            MDDialogContentContainer(scroll),
            MDDialogButtonContainer(btn_close),
        )
        self._day_dialog.open()

    def _select_day(self, day_val, day_name):
        self._pending_day = day_val
        self._day_label.text = f"Jour : {day_name}"
        if self._day_dialog:
            self._day_dialog.dismiss()

    def _add_task(self, *_):
        text = self._text_field.text.strip()
        if not text:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        new_id = int(uuid.uuid4().int % 1_000_000)
        tasks.append({"id": new_id, "text": text, "done": False, "day": self._pending_day})
        app.save_tasks(tasks)
        self._close_dialog()
        self.refresh_tasks()

    def _close_dialog(self, *_):
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None
