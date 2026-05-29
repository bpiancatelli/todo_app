from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp


LINE_SPACING = dp(36)
MARGIN_X = dp(72)


class NotepadBackground(Widget):
    YELLOW = (1.0, 0.99, 0.82, 1)
    BLUE = (0.53, 0.81, 0.98, 1)
    RED = (0.90, 0.20, 0.20, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.YELLOW)
            Rectangle(pos=self.pos, size=self.size)

            Color(*self.BLUE)
            # Start lines from the very top so they tile perfectly downward
            y = self.top
            while y >= self.y:
                Line(points=[self.x, y, self.right, y], width=1)
                y -= LINE_SPACING

            Color(*self.RED)
            mx = self.x + MARGIN_X
            Line(points=[mx, self.top, mx, self.y], width=1.5)
