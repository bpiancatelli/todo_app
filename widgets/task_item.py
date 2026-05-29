from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

# LINE_SPACING from background = 36dp; tasks must match so text sits on lines
Builder.load_string("""
<TaskItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: "36dp"
    padding: ["76dp", "2dp", "16dp", "2dp"]
    spacing: "8dp"

    MDCheckbox:
        id: checkbox
        size_hint: None, None
        size: "28dp", "28dp"
        pos_hint: {"center_y": 0.5}
        active: root.done
        on_active: root.on_check(self, self.active)
        color_active: 0.2, 0.5, 0.9, 1
        color_inactive: 0.4, 0.4, 0.4, 1

    MDLabel:
        id: label
        text: root.text
        font_style: "Body"
        role: "medium"
        theme_text_color: "Custom"
        text_color: 0.10, 0.10, 0.10, 1
        pos_hint: {"center_y": 0.5}
        strikethrough: root.done
        shorten: True
        shorten_from: "right"
""")


class TaskItem(BoxLayout):
    text = StringProperty("")
    done = BooleanProperty(False)
    task_id = NumericProperty(0)

    def on_check(self, checkbox, value):
        self.done = value
        app = self._get_app()
        if app:
            tasks = app.get_all_tasks()
            for t in tasks:
                if t.get("id") == self.task_id:
                    t["done"] = value
                    break
            app.save_tasks(tasks)

    def _get_app(self):
        from kivymd.app import MDApp
        return MDApp.get_running_app()
