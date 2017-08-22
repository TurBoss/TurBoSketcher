#!/usr/bin/python3

import copy

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Rsvg", "2.0")

from gi.repository import Gtk
from gi.repository import Rsvg

from lxml import etree

NS = {
    'svg': 'http://www.w3.org/2000/svg',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
}


class TurBoSketcher:
    def __init__(self):
        self.window = TurBoSketcherWindow(self)
        self.window.set_size_request(800, 600)
        self.window.show_all()

        self.svg = None

    def load_data(self, svg_file):
        self.svg = SvgSketch(svg_file)

        self.svg_pixbuf = self.svg.get_pixbuf
        self.svg_fields = self.svg.get_fields

        for field in self.svg_fields:
            self.window.create_entry(field)

        self.window.set_svg(self.svg_pixbuf)

    @staticmethod
    def run():
        Gtk.main()


class TurBoSketcherWindow(Gtk.Window):
    def __init__(self, app):
        Gtk.Window.__init__(self)
        self.app = app

        self.builder = Gtk.Builder()
        self.builder.add_from_file("resources/ui.glade")
        self.builder.connect_signals(TurBoSketcherHandler(self))

        self.box = self.builder.get_object("box")
        self.sketch = self.builder.get_object("sketch")
        self.field_box = self.builder.get_object("field_box")

        self.add(self.box)

    def set_svg(self, svg):
        self.sketch.set_from_pixbuf(svg)

    def create_entry(self, field):
        label = Gtk.Label()
        label.set_text(field["label"])
        label.show_all()

        entry = Gtk.Entry()
        entry.set_text(field["text"])
        entry.set_name(field["id"])
        entry.show_all()

        separator = Gtk.Separator()
        separator.show_all()

        self.field_box.pack_start(label, True, True, 0)
        self.field_box.pack_start(entry, True, True, 0)
        self.field_box.pack_start(separator, True, True, 0)


class TurBoSketcherHandler:
    def __init__(self, window):
        self.window = window
        self.window.connect('delete-event', Gtk.main_quit)

    def on_menu_open_activate(self, *args, **kwargs):
        fc = Gtk.FileChooserDialog(parent=self.window)

        fc.set_title("FileChooserDialog")
        fc.add_button("_Open", Gtk.ResponseType.OK)
        fc.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        fc.set_default_response(Gtk.ResponseType.OK)

        filename = fc.run()

        if filename == Gtk.ResponseType.OK:
            svg_filename = fc.get_filename()

            self.window.app.load_data(svg_filename)

        fc.destroy()


class SvgSketch:
    def __init__(self, svg_filename):
        self.svg = None
        self.svg_xml = None

        self.fields = list()

        self.load(svg_filename)
        self.get_elements()

    def load(self, svg_filename):
        with open(svg_filename) as svg_file:
            svg_data = svg_file.read().encode("utf-8")
            self.svg = Rsvg.Handle.new_from_data(svg_data)
            self.svg_xml = etree.fromstring(svg_data)

    def get_elements(self):

        field_id = None
        field_label = None
        field_text = None

        field = dict()

        for child in self.svg_xml.iterdescendants():
            if child.tag == "{http://www.w3.org/2000/svg}text":
                field_id = child.attrib["id"]
                field_label = child.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]

            if child.tag in ("{http://www.w3.org/2000/svg}text",
                             "{http://www.w3.org/2000/svg}tspan") and child.text and child.text.strip():

                field_text = child.text

                field["id"] = field_id
                field["label"] = field_label
                field["text"] = field_text

                self.fields.append(field)

    @property
    def get_pixbuf(self):
        return self.svg.get_pixbuf()

    @property
    def get_fields(self):
        return self.fields


def main():
    app = TurBoSketcher()
    app.run()


if __name__ == "__main__":
    main()
