"""A module to interact with the user."""

from __future__ import annotations

import math
from dataclasses import dataclass

# The PySide library is provided by FreeCAD and its path is platform dependent,
# so it cannot be analyzed by mypy.
# mypy: disable-error-code="import-not-found"
from PySide.QtCore import (
    QPoint,
    QPointF,
    QRect,
    QSize,
)
from PySide.QtGui import (
    QMouseEvent,
    QPainter,
    QPalette,
    QPen,
    QPixmap,
    QShowEvent,
)
from PySide.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)


class GridDialog(QDialog):
    """A dialog with togglable grid cells."""

    def __init__(
        self,
        types: list[str],
        grid_layout: list[list[bool]],
        offset: int,
        spacing: int,
    ) -> None:
        """Create the dialog object."""
        super().__init__()
        self.x = len(grid_layout)
        self.y = len(grid_layout[0])
        self.offset = offset
        self.spacing = spacing

        layout = QVBoxLayout()

        self.label = QLabel()
        self.pixmap = QPixmap(QSize(2 * offset + self.x * spacing, 2 * offset + self.y * spacing))
        layout.addWidget(self.label)

        if types:
            self.comboBox = QComboBox()
            self.comboBox.addItems(types)
            layout.addWidget(self.comboBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

        self.grid_layout = grid_layout

        self.origin_pos = QPoint(
            self.offset,
            self.offset + self.y * self.spacing,
        )

    def _to_canvas_point(self, point: QPoint) -> QPoint:
        point.setY(-point.y())
        return self.origin_pos + self.spacing * point

    def _from_mouse_pos(self, point: QPoint) -> QPointF:
        relative_pos = point - (self.origin_pos + self.label.pos())
        return QPointF(relative_pos.x(), -relative_pos.y()) / self.spacing

    def _recompute(self) -> None:
        self.pixmap.fill(self.palette().color(QPalette.Window))

        painter = QPainter(self.pixmap)
        for x in range(self.x):
            for y in range(self.y):
                if self.grid_layout[x][y]:
                    painter.fillRect(
                        QRect(
                            self._to_canvas_point(QPoint(x, y + 1)),
                            self._to_canvas_point(QPoint(x + 1, y)),
                        ),
                        self.palette().highlight(),
                    )
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(self.palette().color(QPalette.Text))
        painter.setPen(pen)
        for x in range(self.x + 1):
            for y in range(self.y + 1):
                painter.drawPoint(self._to_canvas_point(QPoint(x, y)))
        painter.end()

        self.label.setPixmap(self.pixmap)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self._is_good())

    def _is_good(self) -> bool:
        cell_count = 0
        starting_cell = None
        for x in range(self.x):
            for y in range(self.y):
                if self.grid_layout[x][y]:
                    cell_count += 1
                    starting_cell = (x, y)
        if cell_count == 0:
            return False
        assert starting_cell is not None

        visited = set()

        def dfs(x: int, y: int) -> None:
            if (
                (x, y) in visited
                or x < 0
                or y < 0
                or x >= self.x
                or y >= self.y
                or not self.grid_layout[x][y]
            ):
                return
            visited.add((x, y))
            dfs(x + 1, y)
            dfs(x - 1, y)
            dfs(x, y + 1)
            dfs(x, y - 1)

        dfs(*starting_cell)
        return cell_count == len(visited)

    def showEvent(self, event: QShowEvent) -> None:  # noqa: ARG002, D102, N802
        self._recompute()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: D102, N802
        pos = self._from_mouse_pos(event.localPos())
        x = math.floor(pos.x())
        y = math.floor(pos.y())
        if x >= 0 and x < self.x and y >= 0 and y < self.y:
            self.grid_layout[x][y] ^= True
            self._recompute()


@dataclass
class GridDialogData:
    """A result of a successful GridDialog."""

    layout: list[list[bool]]
    bin_type: str | None


def custom_bin_dialog(
    types: list[str],
    initial_layout: list[list[bool]] | None,
) -> GridDialogData | None:
    """Get a custom layout from the user.

    Returns None if the user aborted the operation.

    """
    if initial_layout is None:
        initial_layout = [[False] * 10 for _ in range(10)]
    dialog = GridDialog(types, initial_layout, 40, 50)
    if not dialog.exec():
        return None
    return GridDialogData(
        layout=dialog.grid_layout,
        bin_type=dialog.comboBox.currentText() if types else None,
    )
