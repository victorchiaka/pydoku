import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from math import floor, sqrt


class GridFrame(Gtk.Frame):
    def __init__(self, board, board_size, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_hexpand(True)
        self.set_vexpand(True)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)

        subgrid_size: int = floor(sqrt(board_size))

        if board_size == 6:
            subgrid_rows, subgrid_cols = 2, 3
        else:
            subgrid_rows, subgrid_cols = floor(sqrt(board_size)), floor(
                sqrt(board_size)
            )

        for row in range(board_size):
            for column in range(board_size):
                entry = Gtk.Entry()
                if board_size == 6:
                    entry.add_css_class("six-by-six-cell")
                elif board_size == 9:
                    entry.add_css_class("nine-by-nine-cell")
                entry.set_max_width_chars(1)
                entry.set_width_chars(1)
                entry.set_alignment(0.5)
                grid.attach(entry, column, row, 1, 1)

                if row % subgrid_rows == 0 and row != 0:
                    entry.get_style_context().add_class("top-border")
                if column % subgrid_cols == 0 and column != 0:
                    entry.get_style_context().add_class("left-border")
                if (row + 1) % subgrid_rows == 0 and (row + 1) != board_size:
                    entry.get_style_context().add_class("bottom-border")
                if (column + 1) % subgrid_cols == 0 and (column + 1) != board_size:
                    entry.get_style_context().add_class("right-border")

        self.set_child(grid)


class SideFrame(Gtk.Frame):
    def __init__(self) -> None:
        super().__init__()

        side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        side_box.set_hexpand(True)
        side_box.set_vexpand(True)
        side_box.set_spacing(0)
        side_box.set_homogeneous(False)

        time_box = Gtk.Box()
        time_box.set_hexpand(True)
        time_box.set_vexpand(True)
        time_box.set_halign(Gtk.Align.CENTER)
        time_box.set_valign(Gtk.Align.CENTER)
        time_label = Gtk.Label(label="00:00")
        time_label.add_css_class("time-label")
        time_box.append(time_label)

        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        action_box.set_hexpand(True)
        action_box.set_vexpand(True)
        action_box.set_halign(Gtk.Align.CENTER)
        action_box.set_valign(Gtk.Align.CENTER)
        actions = ["Stop", "Restart", "Pause"]
        for action in actions:
            action_button = Gtk.Button(label=action)
            action_button.add_css_class("action-button")
            action_box.append(action_button)

        side_box.append(time_box)
        side_box.append(action_box)
        self.set_child(side_box)
