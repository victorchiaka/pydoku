import gi

from algorithms.generator import Generator
from algorithms.solver import Solver
from .game_frame import GridFrame, SideFrame

gi.require_version(namespace="Gtk", version="4.0")
from gi.repository import Gtk, Gio, Gdk

from ..constants import MAIN_CSS, MENU_XML, LICENSE
from ..utils import load_css


class MainApplicationWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_default_size(800, 600)
        self.set_resizable(False)


class MainApplication(Gtk.Application):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, application_id="com.github.victorchiaka", **kwargs)

        load_css(css_file=MAIN_CSS)
        self.window = None

        self.stack = []

    def do_activate(self):
        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")

            grid_type_box = Gtk.Grid()
            grid_type_box.set_halign(Gtk.Align.CENTER)
            grid_type_box.set_valign(Gtk.Align.CENTER)
            grid_type_box.set_row_spacing(15)
            grid_type_box.set_column_spacing(15)
            grid_type_box.set_hexpand(True)
            grid_type_box.set_vexpand(True)

            self.header_bar = Gtk.HeaderBar()
            self.window.set_titlebar(self.header_bar)

            image = Gtk.Image.new_from_icon_name("open-menu-symbolic")
            builder = Gtk.Builder.new_from_string(MENU_XML, -1)
            menu_model = builder.get_object("menubar")
            menu = Gtk.MenuButton(menu_model=menu_model)

            menu.set_child(image)
            self.header_bar.pack_end(menu)

            grid_types: list[dict[str, str]] = [
                {"type": "6x6", "value": "6"},
                {"type": "9x9", "value": "9"},
                {"type": "16x16", "value": "16"},
            ]

            for i, grid_type in enumerate(grid_types):
                button = Gtk.Button(label=grid_type["type"])
                button.connect(
                    "clicked", self.show_difficulty_type, int(grid_type["value"])
                )
                button.add_css_class("grid-type-button")
                row = i // 3
                column = i % 3
                grid_type_box.attach(button, column, row, 1, 1)

            self.stack.clear()
            self.stack.append(grid_type_box)
            self.window.set_child(grid_type_box)

        self.window.present()

    def show_difficulty_type(self, _widget, board_size):
        self.board_size = board_size
        self.difficulty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.difficulty_box.set_halign(Gtk.Align.CENTER)
        self.difficulty_box.set_valign(Gtk.Align.CENTER)

        difficulty_label: Gtk.Label = Gtk.Label(label="Select difficulty")
        difficulty_label.add_css_class("difficulty-label")
        self.difficulty_box.append(difficulty_label)

        self.difficulties = (
            ["Medium", "Hard", "Expert"]
            if self.board_size == 16
            else ["Easy", "Medium", "Hard", "Expert"]
        )

        for difficulty in self.difficulties:
            button = Gtk.Button(label=difficulty)
            button.add_css_class("difficulty-button")
            button.connect("clicked", self.show_sudoku_gameplay_screen, difficulty)
            self.difficulty_box.append(button)

        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")

        self.quit_button = Gtk.Button(label="Back")
        self.quit_button.connect("clicked", self.on_back)
        self.header_bar.remove(self.quit_button)
        self.header_bar.pack_start(self.quit_button)

        self.stack.append(self.difficulty_box)
        self.window.set_child(self.difficulty_box)

    def show_sudoku_gameplay_screen(self, _widget, difficulty: str) -> None:
        board: list[list[int | str]] = Generator(
            difficulty=difficulty, size=self.board_size
        ).generate_board()

        board_copy: list[list[int | str]] = [
            [0 for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

        for row in range(self.board_size):
            for column in range(self.board_size):
                board_copy[row][column] = board[row][column]

        solved_board: list[list[int | str]] = Solver(
            board=board_copy, size=self.board_size
        ).solve_board()

        game_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.window.set_child(self.game_box)
        grid_frame = GridFrame(board, solved_board, self.board_size)
        game_box.append(grid_frame)

        self.timer = 300
        self.side_frame = SideFrame(timer=self.timer)

        grid_frame.set_size_request(560, -1)
        self.side_frame.set_size_request(240, -1)

        game_box.append(self.side_frame)
        self.stack.append(game_box)
        self.window.set_child(game_box)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)

        self.set_time_action = Gio.SimpleAction.new("set_time", None)
        self.set_time_action.connect("activate", self.on_set_time)
        self.add_action(self.set_time_action)

    def on_about(self, _action, _param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_program_name("Pydoku")
        about_dialog.set_version("1.0")
        about_dialog.set_copyright("© 2024 Victor Chiaka")
        about_dialog.set_comments(
            "Pydoku is a Sudoku puzzle game developed in Python using GTK."
        )
        about_dialog.set_license(LICENSE)
        about_dialog.set_website("https://github.com/victorchiaka/pydoku")
        about_dialog.set_website_label("Pydoku GitHub Repository")
        about_dialog.set_authors(["Victor Chiaka"])
        about_dialog.set_artists(["Victor Chiaka"])
        about_dialog.set_logo_icon_name("applications-games")
        about_dialog.present()

    def on_back(self, _widget):
        if len(self.stack) > 1:
            self.stack.pop()
            previous_screen = self.stack[-1]
            if not self.window:
                self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.window.set_child(previous_screen)
        if len(self.stack) == 1:
            self.header_bar.remove(self.quit_button)

    def on_quit(self, _action, _param):
        self.quit()

    def on_set_time(self, _action, _param):
        popover = Gtk.Popover()
        popover.set_position(Gtk.PositionType.BOTTOM)
        popover.set_has_arrow(True)

        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        minutes_label = Gtk.Label(label="Minutes:")
        grid.attach(minutes_label, 0, 0, 1, 1)

        minutes_adjustment = Gtk.Adjustment.new(0, 0, 20, 1, 5, 0)
        self.minutes_spin_button = Gtk.SpinButton(
            adjustment=minutes_adjustment, climb_rate=1, digits=0
        )
        grid.attach(self.minutes_spin_button, 1, 0, 1, 1)
        seconds_label = Gtk.Label(label="Seconds:")
        grid.attach(seconds_label, 0, 1, 1, 1)

        seconds_adjustment = Gtk.Adjustment.new(0, 0, 59, 1, 5, 0)
        self.seconds_spin_button = Gtk.SpinButton(
            adjustment=seconds_adjustment, climb_rate=1, digits=0
        )
        grid.attach(self.seconds_spin_button, 1, 1, 1, 1)
        adjust_button = Gtk.Button(label="Set Timer")
        adjust_button.connect("clicked", self.on_adjust_timer_clicked)
        grid.attach(adjust_button, 0, 2, 2, 1)

        popover.set_child(grid)
        popover.set_parent(self.window)

        allocation = self.header_bar.get_allocation()
        rect = Gdk.Rectangle()
        rect.x = 650
        rect.y = allocation.y + allocation.height
        popover.set_pointing_to(rect)
        popover.show()

    def on_adjust_timer_clicked(self, button):
        minutes = self.minutes_spin_button.get_value_as_int()
        seconds = self.seconds_spin_button.get_value_as_int()

        self.timer = minutes * 60 + seconds
        if hasattr(self, "side_frame") and self.side_frame:
            self.side_frame.update_timer_label(self.timer)
