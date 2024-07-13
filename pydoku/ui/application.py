import csv, os, gi

from algorithms.generator import Generator
from algorithms.solver import Solver
from .game_frame import GridFrame, SideFrame

gi.require_version(namespace="Gtk", version="4.0")
from gi.repository import Gtk, Gio, Gdk, GLib

from ..constants import MAIN_CSS, MENU_XML, LICENSE
from ..utils import load_css


class MainApplicationWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_default_size(800, 600)
        self.set_resizable(False)
        self.connect("close-request", self.on_destroy)

    def on_destroy(self, _action):
        self.get_application().on_quit(_action, None)


class MainApplication(Gtk.Application):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, application_id="com.github.victorchiaka", **kwargs)

        load_css(css_file=MAIN_CSS)
        self.window = None
        self.timer_id = None
        self.current_difficulty = None
        self.solved_board = []
        self.initial_board = None
        self.generated_board = []
        self.current_time = None
        self.difficulty = None
        self.header_bar = Gtk.HeaderBar()

        self.stack = []
        self.current_board_state = []

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

            self.window.set_titlebar(self.header_bar)

            image = Gtk.Image.new_from_icon_name("open-menu-symbolic")
            builder = Gtk.Builder.new_from_string(MENU_XML, -1)
            menu_model = builder.get_object("menubar")
            menu = Gtk.MenuButton(menu_model=menu_model)

            menu.set_child(image)
            self.header_bar.pack_end(menu)

            grid_types = [
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
        self.initial_board = None
        self.board_size = board_size
        self.difficulty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.difficulty_box.set_halign(Gtk.Align.CENTER)
        self.difficulty_box.set_valign(Gtk.Align.CENTER)

        difficulty_label = Gtk.Label(label="Select difficulty")
        difficulty_label.add_css_class("difficulty-label")
        self.difficulty_box.append(difficulty_label)

        self.difficulties = (
            ["Medium", "Hard", "Expert"]
            if self.board_size == 16
            else ["Easy", "Medium", "Hard", "Expert"]
        )

        for self.difficulty in self.difficulties:
            button = Gtk.Button(label=self.difficulty)
            button.add_css_class("difficulty-button")
            button.connect("clicked", self.show_sudoku_gameplay_screen, self.difficulty)
            self.difficulty_box.append(button)

        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")

        self.quit_button = Gtk.Button(label="Back")
        self.quit_button.connect("clicked", self.on_back)
        self.header_bar.remove(self.quit_button)
        self.header_bar.pack_start(self.quit_button)

        self.stack.append(self.difficulty_box)
        self.window.set_child(self.difficulty_box)

    def show_sudoku_gameplay_screen(self, _widget, difficulty) -> None:
        if not self.initial_board:
            self.initial_board = Generator(
                difficulty=difficulty, size=self.board_size
            ).generate_board()
        self.current_difficulty = difficulty

        self.board_copy: list[list[int | str]] = [
            [0 for _ in range(self.board_size)] for _ in range(self.board_size)
        ]

        for row in range(self.board_size):
            for column in range(self.board_size):
                self.board_copy[row][column] = self.initial_board[row][column]

        self.solved_board: list[list[int | str]] = Solver(
            board=self.board_copy, size=self.board_size
        ).solve_board()

        game_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.window.set_child(self.game_box)

        self.timer = 300
        self.side_frame = SideFrame(
            self.timer,
            self.restart_game,
            self.pause_game,
            self.new_board,
            self.time_up,
        )
        self.side_frame.set_size_request(240, -1)

        self.grid_frame = GridFrame(
            self.initial_board, self.solved_board, self.board_size, self.side_frame
        )

        self.grid_frame.set_size_request(560, -1)
        game_box.append(self.grid_frame)

        game_box.append(self.side_frame)
        self.stack.append(game_box)
        self.window.set_child(game_box)

    def read_game_data(self):
        file_path = os.path.join(os.path.dirname(__file__), "game_data.csv")
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        game_data = {}
        try:
            with open(file_path, mode="r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    for key, value in row.items():
                        game_data[key] = (
                            eval(value)
                            if key
                            in [
                                "self.initial_board",
                                "self.current_board_state",
                                "self.solved_board",
                                "self.generated_board",
                                "self.stack",
                                "self.current_time",
                                "self.difficulty",
                                "self.header_bar",
                            ]
                            else value
                        )
            print("Game data loaded successfully:", game_data)
        except Exception as e:
            print(f"Error reading game data: {e}")

        return game_data

    def initialize_game_from_data(self, game_data):
        if not game_data:
            print("No game data to initialize.")
            return

        try:
            self.initial_board = game_data.get("initial_board")
            self.current_board_state = game_data.get("current_board_state")
            self.solved_board = game_data.get("solved_board")
            self.generated_board = game_data.get("generated_board")
            self.board_size = int(game_data.get("board_size", 9))
            self.current_difficulty = game_data.get("difficulty")
            self.timer = int(game_data.get("timer", 300))

            self.stack = game_data.get("stack", [])

            if self.stack:
                if not self.window:
                    self.window = MainApplicationWindow(
                        application=self, title="Pydoku"
                    )

                # Properly re-construct the stack of UI components
                for ui_element in self.stack:
                    if isinstance(ui_element, Gtk.Grid):
                        print("Reconstructed a Gtk.Grid")
                    elif isinstance(ui_element, Gtk.Box):
                        print("Reconstructed a Gtk.Box")
                    # Add more checks as needed to reconstruct other UI elements

                # Set the last UI element in the stack as the current child
                last_screen = self.stack[-1]
                self.window.set_child(last_screen)
                print("Game UI successfully reconstructed.")
            else:
                self.show_difficulty_type(None, self.board_size)
                print("Showing difficulty type selection.")
        except Exception as e:
            print(f"Error initializing game from data: {e}")

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

        game_data = self.read_game_data()
        self.initialize_game_from_data(game_data)

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
        self.initial_board = None
        if len(self.stack) > 1:
            self.stack.pop()
            previous_screen = self.stack[-1]
            if not self.window:
                self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.window.set_child(previous_screen)
        if len(self.stack) == 1:
            self.header_bar.remove(self.quit_button)

    def on_save(self):
        file_path = os.path.join(os.path.dirname(__file__), "game_data.csv")
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
        if hasattr(self, "grid_frame") and self.grid_frame:
            self.current_board_state = self.grid_frame.get_current_board_state()
        game_data = {
            "self.initial_board": self.initial_board,
            "self.stack": self.stack,
            "self.current_board_state": self.current_board_state,
            "self.difficulty": self.current_difficulty,
            "self.solved_board": self.solved_board,
            "self.generated_board": self.initial_board,
            "self.current_time": self.side_frame.timer if self.side_frame else None,
            "self.header_bar": self.header_bar,
        }
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            for key, value in game_data.items():
                writer.writerow([key, value])

        print(f"Game data saved to f{file_path}")

    def on_quit(self, _action, _param):
        self.on_save()
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

    def restart_game(self):
        self.show_sudoku_gameplay_screen(None, self.current_difficulty)

    def pause_game(self):
        if self.side_frame.timer_id:
            GLib.source_remove(self.side_frame.timer_id)
        self.show_pause_modal()

    def new_board(self):
        self.initial_board = None
        self.stack.pop()
        self.show_sudoku_gameplay_screen(None, self.current_difficulty)

    def resume_game(self, _widget):
        self.side_frame.start_timer()
        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")
        self.window.set_child(self.stack[-1])

    def show_pause_modal(self):
        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")

        overlay = Gtk.Overlay()
        overlay.set_halign(Gtk.Align.FILL)
        overlay.set_valign(Gtk.Align.FILL)

        background = Gtk.Box()
        allocation = self.window.get_allocation()
        background.set_size_request(allocation.width, allocation.height)
        background.get_style_context().add_class("modal-background")

        modal_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        modal_box.set_halign(Gtk.Align.CENTER)
        modal_box.set_valign(Gtk.Align.CENTER)
        modal_box.set_margin_top(100)
        modal_box.set_margin_bottom(50)
        modal_box.set_margin_start(50)
        modal_box.set_margin_end(50)
        modal_box.set_size_request(300, 200)
        modal_box.add_css_class("modal-box")

        paused_label = Gtk.Label(label="GAME PAUSED")
        paused_label.add_css_class("game-paused-label")
        modal_box.append(paused_label)

        continue_button = Gtk.Button(label="Continue")
        continue_button.set_halign(Gtk.Align.CENTER)
        continue_button.add_css_class("continue-button")
        continue_button.connect("clicked", self.resume_game)
        modal_box.append(continue_button)

        overlay.add_overlay(background)
        overlay.add_overlay(modal_box)
        self.window.set_child(overlay)

    def count_empty_entries(self, row):
        return len([entry for entry in row if entry.get_text() == ""])

    def time_up(self):
        for row in self.grid_frame.entries:
            for entry in row:
                entry.set_editable(False)
            if self.count_empty_entries(row) > 0:
                self.side_frame.time_label.set_text("You lost")
                break
            else:
                self.side_frame.time_label.set_text("You won")
                self.side_frame.time_label.add_css_class("win-message")
