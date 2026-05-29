from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

Builder.load_string("""
<TaskItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: "48dp"
    padding: ["80dp", "4dp", "16dp", "4dp"]
    spacing: "12dp"

    MDCheckbox:
        id: checkbox
        size_hint: None, None
        size: "32dp", "32dp"
        pos_hint: {"center_y": 0.5}
        active: root.done
        on_active: root.on_check(self, self.active)
        selected_color: 0.2, 0.5, 0.9, 1
        unselected_color: 0.4, 0.4, 0.4, 1

    MDLabel:
        id: label
        text: root.text
        font_style: "Body1"
        theme_text_color: "Custom"
        text_color: 0.15, 0.15, 0.15, 1
        pos_hint: {"center_y": 0.5}
        strikethrough: root.done
""")


class TaskItem(BoxLayout):
    text = StringProperty("")
    done = BooleanProperty(False)
    task_id = NumericProperty(0)

    def on_check(self, checkbox, value):
        self.done = value
        app = self.get_app()
        if app:
            tasks = app.get_all_tasks()
            for t in tasks:
                if t.get("id") == self.task_id:
                    t["done"] = value
                    break
            app.save_tasks(tasks)

    def get_app(self):
        from kivymd.app import MDApp
        return MDApp.get_running_app()
