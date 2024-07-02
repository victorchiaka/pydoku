import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib, Gdk

from math import floor, sqrt


class GridFrame(Gtk.Frame):
    def __init__(self, board, solved_board, board_size, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("grid-frame")

        self.solved_board = solved_board
        self.entries = []

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)

        if board_size == 6:
            subgrid_rows, subgrid_cols = 2, 3
        else:
            subgrid_rows, subgrid_cols = floor(sqrt(board_size)), floor(
                sqrt(board_size)
            )

        for row in range(board_size):
            row_entries = []
            for column in range(board_size):
                entry = Gtk.Entry()
                if board_size == 6:
                    entry.add_css_class("six-by-six-cell")
                elif board_size == 9:
                    entry.add_css_class("nine-by-nine-cell")
                entry.set_max_width_chars(1)
                entry.set_width_chars(1)
                entry.set_alignment(0.5)
                entry_text: str = str(board[row][column])
                if entry_text == "0":
                    entry.set_text("")
                    entry.connect("changed", self.on_entry_change, row, column)
                else:
                    entry.set_text(entry_text)
                    entry.set_editable(False)
                    entry.add_css_class("filled-entry")
                grid.attach(entry, column, row, 1, 1)
                row_entries.append(entry)

                if row % subgrid_rows == 0 and row != 0:
                    entry.get_style_context().add_class("top-border")
                if column % subgrid_cols == 0 and column != 0:
                    entry.get_style_context().add_class("left-border")
                if (row + 1) % subgrid_rows == 0 and (row + 1) != board_size:
                    entry.get_style_context().add_class("bottom-border")
                if (column + 1) % subgrid_cols == 0 and (column + 1) != board_size:
                    entry.get_style_context().add_class("right-border")
            self.entries.append(row_entries)

        self.set_child(grid)

    def on_entry_change(self, _widget, row, column):
        choice = _widget.get_text()

        _widget.remove_css_class("correct-position")
        _widget.remove_css_class("filled-entry")

        if str(choice) == "":
            self.remove_highlights()
            return

        if str(self.solved_board[row][column]) == str(choice):
            _widget.add_css_class("correct-position")
            _widget.set_editable(False)
        else:
            self.highlight_similar(choice)

    def highlight_similar(self, choice) -> None:
        for row in range(len(self.solved_board)):
            for column in range(len(self.solved_board[row])):
                entry = self.get_entry_at_position(row, column)
                if entry.get_text() == choice:
                    entry.add_css_class("conflict-highlight")
                else:
                    entry.remove_css_class("conflict-highlight")

    def remove_highlights(self) -> None:
        for row in range(len(self.solved_board)):
            for column in range(len(self.solved_board[row])):
                entry = self.get_entry_at_position(row, column)
                entry.remove_css_class("conflict-highlight")

    def get_entry_at_position(self, row, column):
        return self.entries[row][column]


class SideFrame(Gtk.Frame):
    def __init__(self, timer: int, restart_callback, pause_callback) -> None:
        super().__init__()

        self.timer = timer
        self.restart_callback = restart_callback
        self.pause_callback = pause_callback
        self.seconds = self.timer % 60
        self.minutes = (self.timer // 60) % 60
        self.timer_id = None

        side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        side_box.set_hexpand(True)
        side_box.set_vexpand(True)
        side_box.set_spacing(0)
        side_box.set_homogeneous(False)

        timer_box = Gtk.Box()
        timer_box.set_hexpand(True)
        timer_box.set_vexpand(True)
        timer_box.set_halign(Gtk.Align.CENTER)
        timer_box.set_valign(Gtk.Align.CENTER)
        self.time_label = Gtk.Label(label=f"{self.minutes:02}:{self.seconds:02}")
        self.time_label.add_css_class("time-label")
        timer_box.append(self.time_label)

        action_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        action_box.set_hexpand(True)
        action_box.set_vexpand(True)
        action_box.set_halign(Gtk.Align.CENTER)
        action_box.set_valign(Gtk.Align.CENTER)
        actions = ["Pause", "Restart", "New board"]
        for action in actions:
            action_button = Gtk.Button(label=action)
            action_button.connect("clicked", self.on_sideframe_action, action)
            action_button.add_css_class("action-button")
            action_box.append(action_button)

        side_box.append(timer_box)
        side_box.append(action_box)

        self.set_child(side_box)

        self.start_timer()

    def on_sideframe_action(self, _widget, _param) -> None:
        if _param == "Restart":
            self.restart_callback()
        elif _param == "Pause":
            self.pause_callback()

    def update_timer_label(self, timer):
        self.timer = timer
        self.seconds = self.timer % 60
        self.minutes = (self.timer // 60) % 60
        self.time_label.set_text(f"{self.minutes:02}:{self.seconds:02}")

    def start_timer(self):
        if self.timer_id:
            GLib.source_remove(self.timer_id)
        self.timer_id = GLib.timeout_add_seconds(1, self.update_timer)

    def update_timer(self):
        if self.timer > 1:
            self.timer -= 1
            self.seconds = self.timer % 60
            self.minutes = (self.timer // 60) % 60
            self.time_label.set_text(f"{self.minutes:02}:{self.seconds:02}")
            return True
        self.time_label.set_text("TIME'S UP")
        self.time_label.add_css_class("time-out")
        return False
