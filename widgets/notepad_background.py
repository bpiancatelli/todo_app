from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window


class NotepadBackground(Widget):
    """Draws the yellow legal pad background with blue lines and red margin."""

    YELLOW = (1.0, 0.99, 0.82, 1)
    BLUE = (0.53, 0.81, 0.98, 1)
    RED = (0.90, 0.20, 0.20, 1)
    LINE_SPACING = 36
    MARGIN_X = 72

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._redraw, pos=self._redraw)

    def _redraw(self, *_):
        self.canvas.before.clear()
        with self.canvas.before:
            # Yellow background
            Color(*self.YELLOW)
            Rectangle(pos=self.pos, size=self.size)

            # Blue horizontal lines
            Color(*self.BLUE)
            y = self.top - self.LINE_SPACING * 2
            while y > self.y:
                Line(points=[self.x, y, self.right, y], width=1)
                y -= self.LINE_SPACING

            # Red vertical margin
            Color(*self.RED)
            margin_x = self.x + self.MARGIN_X
            Line(points=[margin_x, self.top, margin_x, self.y], width=1.5)
