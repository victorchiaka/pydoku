import gi

gi.require_version(namespace="Gtk", version="4.0")
from gi.repository import Gtk, Gio

from ..constants import MAIN_CSS, MENU_XML, LICENSE
from ..utils import load_css


class MainApplicationWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_default_size(850, 750)
        self.props.show_menubar = True


class MainApplication(Gtk.Application):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, application_id="com.github.victorchiaka", **kwargs)

        load_css(css_file=MAIN_CSS)
        self.window = None
        self.difficulties = ["Easy", "Medium", "Hard", "Expert"]

    def do_activate(self):
        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.difficulty_box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL, spacing=10
            )
            self.difficulty_box.set_halign(Gtk.Align.CENTER)
            self.difficulty_box.set_valign(Gtk.Align.CENTER)

            difficulty_label: Gtk.Label = Gtk.Label(label="Select difficulty")
            difficulty_label.add_css_class("difficulty-label")
            self.difficulty_box.append(difficulty_label)

            for difficulty in self.difficulties:
                button: Gtk.Button = Gtk.Button(label=difficulty)
                button.add_css_class("difficulty-button")
                button.connect("clicked", self.show_board_type, difficulty)
                self.difficulty_box.append(button)
            self.window.set_child(self.difficulty_box)
        self.window.present()

    def show_board_type(self, _widget, difficulty):
        print(f"Selected difficulty: {difficulty}")

        if difficulty == "Easy":
            # show just two grid types 6x6 and 9x9
            pass

        # As it is not Easy it will show all grid types
        self.grid_type_box = Gtk.Grid()
        self.grid_type_box.set_halign(Gtk.Align.CENTER)
        self.grid_type_box.set_valign(Gtk.Align.CENTER)

        grid_types: list[str] = ["6x6", "9x9", "16x16", "Custom"]
        self.grid_type_box.set_row_spacing(15)
        self.grid_type_box.set_column_spacing(15)
        self.grid_type_box.set_hexpand(True)
        self.grid_type_box.set_vexpand(True)

        for i, grid_type in enumerate(grid_types):
            button = Gtk.Button(label=grid_type)
            button.add_css_class("grid-type-button")
            self.grid_type_box.attach(button, i % 2, i // 2, 1, 1)

        if not self.window:
            self.window = MainApplicationWindow(application=self, title="Pydoku")
            self.window.set_child(self.grid_type_box)
        self.window.set_child(self.grid_type_box)

    def show_sudoku_gameplay_screen(self, board_size: int) -> None:
        pass

    def do_startup(self):
        Gtk.Application.do_startup(self)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)

        builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        self.set_menubar(builder.get_object("menubar"))

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

    def on_quit(self, _action, _param):
        self.quit()
