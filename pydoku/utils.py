import gi

gi.require_version(namespace="Gtk", version="4.0")
from gi.repository import Gtk, Gdk


def load_css(css_file):
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(css_file)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
