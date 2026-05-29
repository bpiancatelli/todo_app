from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

LONG_PRESS_DELAY = 0.45  # seconds

Builder.load_string("""
<TaskItem>:
    orientation: "horizontal"
    size_hint_y: None
    height: "36dp"
    padding: ["76dp", "2dp", "16dp", "2dp"]
    spacing: "8dp"

    canvas.before:
        Color:
            rgba: (0.85, 0.92, 1, 1) if root.highlighted else (0, 0, 0, 0)
        Rectangle:
            pos: self.pos
            size: self.size

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
    highlighted = BooleanProperty(False)

    _long_press_event = None
    _touch_moved = False

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

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._touch_moved = False
            self._long_press_event = Clock.schedule_once(
                self._trigger_long_press, LONG_PRESS_DELAY
            )
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self._long_press_event:
            self._touch_moved = True
            self._long_press_event.cancel()
            self._long_press_event = None
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if self._long_press_event:
            self._long_press_event.cancel()
            self._long_press_event = None
        self.highlighted = False
        return super().on_touch_up(touch)

    def _trigger_long_press(self, dt):
        if not self._touch_moved:
            self.highlighted = True
            screen = self._get_home_screen()
            if screen:
                screen.open_task_menu(self)

    def _get_app(self):
        from kivymd.app import MDApp
        return MDApp.get_running_app()

    def _get_home_screen(self):
        app = self._get_app()
        if app and app.root:
            try:
                return app.root.get_screen("home")
            except Exception:
                return None
