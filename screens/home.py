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
from kivymd.uix.menu import MDDropdownMenu
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
DAYS_LABEL = {d: n for d, n in DAYS}


class HomeScreen(MDScreen):
    _dialog = None
    _day_dialog = None
    _pending_day = None
    _context_menu = None
    _edit_task_id = None

    def on_enter(self):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        app._check_reset(0)
        Clock.schedule_once(lambda dt: self.refresh_tasks(), 0.1)

    def refresh_tasks(self):
        if 'task_list' not in self.ids:
            Clock.schedule_once(lambda dt: self.refresh_tasks(), 0.1)
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        task_list = self.ids['task_list']
        task_list.clear_widgets()
        for task in app.get_tasks_for_today():
            item = TaskItem(
                text=task["text"],
                done=task.get("done", False),
                task_id=task["id"],
            )
            task_list.add_widget(item)

    # ------------------------------------------------------------------ #
    # Context menu (long press)
    # ------------------------------------------------------------------ #

    def open_task_menu(self, task_item: TaskItem):
        if self._context_menu:
            self._context_menu.dismiss()

        task_id = task_item.task_id
        items = [
            {
                "text": "Modifier",
                "leading_icon": "pencil-outline",
                "on_release": lambda: self._menu_edit(task_id),
            },
            {
                "text": "Supprimer",
                "leading_icon": "trash-can-outline",
                "on_release": lambda: self._menu_delete(task_id),
            },
            {
                "text": "Monter",
                "leading_icon": "arrow-up",
                "on_release": lambda: self._menu_move(task_id, -1),
            },
            {
                "text": "Descendre",
                "leading_icon": "arrow-down",
                "on_release": lambda: self._menu_move(task_id, +1),
            },
        ]
        self._context_menu = MDDropdownMenu(caller=task_item, items=items)
        self._context_menu.open()

    def _menu_edit(self, task_id):
        if self._context_menu:
            self._context_menu.dismiss()
        self._open_edit_dialog(task_id)

    def _menu_delete(self, task_id):
        if self._context_menu:
            self._context_menu.dismiss()
        self._confirm_delete(task_id)

    def _menu_move(self, task_id, direction):
        if self._context_menu:
            self._context_menu.dismiss()
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        idx = next((i for i, t in enumerate(tasks) if t["id"] == task_id), None)
        if idx is None:
            return
        new_idx = idx + direction
        if 0 <= new_idx < len(tasks):
            tasks.insert(new_idx, tasks.pop(idx))
            app.save_tasks(tasks)
            self.refresh_tasks()

    # ------------------------------------------------------------------ #
    # Edit dialog
    # ------------------------------------------------------------------ #

    def _open_edit_dialog(self, task_id):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return

        self._edit_task_id = task_id
        self._pending_day = task.get("day")

        self._text_field = MDTextField(
            text=task["text"],
            hint_text="Texte de la tâche...",
            mode="outlined",
            size_hint_y=None,
            height=dp(56),
        )
        day_label_text = DAYS_LABEL.get(task.get("day"), "Tous les jours")
        self._day_label = MDLabel(
            text=f"Jour : {day_label_text}",
            size_hint_y=None,
            height=dp(32),
        )
        day_btn = MDButton(style="text", on_release=self._open_day_picker)
        day_btn.add_widget(MDButtonText(text="Changer le jour"))

        content = MDDialogContentContainer(orientation="vertical", spacing=dp(8))
        content.add_widget(self._text_field)
        content.add_widget(self._day_label)
        content.add_widget(day_btn)

        btn_cancel = MDButton(style="text", on_release=self._close_dialog)
        btn_cancel.add_widget(MDButtonText(text="Annuler"))
        btn_save = MDButton(style="filled", on_release=self._save_edit)
        btn_save.add_widget(MDButtonText(text="Enregistrer"))

        self._dialog = MDDialog(
            MDDialogHeadlineText(text="Modifier la tâche"),
            content,
            MDDialogButtonContainer(btn_cancel, btn_save, spacing=dp(8)),
        )
        self._dialog.open()

    def _save_edit(self, *_):
        text = self._text_field.text.strip()
        if not text:
            return
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        for t in tasks:
            if t["id"] == self._edit_task_id:
                t["text"] = text
                t["day"] = self._pending_day
                break
        app.save_tasks(tasks)
        self._close_dialog()
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    # Delete confirmation
    # ------------------------------------------------------------------ #

    def _confirm_delete(self, task_id):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = app.get_all_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return

        btn_cancel = MDButton(style="text", on_release=self._close_dialog)
        btn_cancel.add_widget(MDButtonText(text="Annuler"))
        btn_del = MDButton(style="filled", on_release=lambda *_: self._do_delete(task_id))
        btn_del.add_widget(MDButtonText(text="Supprimer"))

        self._dialog = MDDialog(
            MDDialogHeadlineText(text="Supprimer la tâche ?"),
            MDDialogContentContainer(
                MDLabel(
                    text=f'"{task["text"]}" sera supprimée définitivement.',
                    size_hint_y=None,
                    height=dp(40),
                )
            ),
            MDDialogButtonContainer(btn_cancel, btn_del, spacing=dp(8)),
        )
        self._dialog.open()

    def _do_delete(self, task_id):
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        tasks = [t for t in app.get_all_tasks() if t["id"] != task_id]
        app.save_tasks(tasks)
        self._close_dialog()
        self.refresh_tasks()

    # ------------------------------------------------------------------ #
    # Add dialog
    # ------------------------------------------------------------------ #

    def open_add_dialog(self):
        self._pending_day = None
        self._edit_task_id = None
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
        day_btn = MDButton(style="text", on_release=self._open_day_picker)
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

    # ------------------------------------------------------------------ #
    # Day picker (shared by add + edit)
    # ------------------------------------------------------------------ #

    def _open_day_picker(self, *_):
        items_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=0)
        items_box.bind(minimum_height=items_box.setter("height"))

        for day_val, day_name in DAYS:
            item = MDListItem(
                on_release=lambda x, d=day_val, n=day_name: self._select_day(d, n),
            )
            item.add_widget(MDListItemHeadlineText(text=day_name))
            items_box.add_widget(item)

        scroll = ScrollView(size_hint=(1, None), height=dp(300))
        scroll.add_widget(items_box)

        btn_close = MDButton(style="text", on_release=lambda x: self._day_dialog.dismiss())
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

    def _close_dialog(self, *_):
        if self._dialog:
            self._dialog.dismiss()
            self._dialog = None
