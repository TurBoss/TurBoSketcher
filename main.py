#!/usr/bin/python3

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
        self.svg_pixbuf = None
        self.svg_fields = None
        self.svg_filename = None

    def load_data(self, svg_file):

        self.svg_filename = svg_file

        self.svg = SvgSketch(svg_file)

        self.svg_pixbuf = self.svg.get_pixbuf
        self.svg_fields = self.svg.get_fields

        for id, data in self.svg_fields.items():
            self.window.create_entry(id, data)

        self.window.set_svg(self.svg_pixbuf)

    def refresh_sketcher(self):

        self.svg = SvgSketch(self.svg_filename)

        self.svg_pixbuf = self.svg.get_pixbuf
        self.window.set_svg(self.svg_pixbuf)

    def text_changed(self, entry):
        entry_id = entry.get_name()
        entry_buffer = entry.get_buffer()
        entry_text = entry_buffer.get_text()
        self.svg.set_field(entry_id, entry_text)

    @staticmethod
    def run():
        Gtk.main()


class TurBoSketcherWindow(Gtk.Window):
    def __init__(self, app):
        Gtk.Window.__init__(self)
        self.app = app

        self.set_title("TurboSketcher")

        self.builder = Gtk.Builder()
        self.builder.add_from_file("resources/ui.glade")
        self.builder.connect_signals(TurBoSketcherHandler(self))

        self.box = self.builder.get_object("box")
        self.sketch = self.builder.get_object("sketch")
        self.field_box = self.builder.get_object("field_box")

        self.add(self.box)

    def set_svg(self, svg):
        self.sketch.clear()
        self.sketch.set_from_pixbuf(svg)

    def create_entry(self, id, data):
        label = Gtk.Label()
        label.set_text(data["label"])
        label.show_all()

        entry = Gtk.Entry()
        entry.set_text(data["text"])
        entry.set_name(id)
        entry.connect("changed", self.app.text_changed)
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

        filter_svg = Gtk.FileFilter()
        filter_svg.set_name('Sketch')
        filter_svg.add_mime_type('image/svg+xml')

        fc = Gtk.FileChooserDialog(parent=self.window)

        fc.set_title("Load Sketch")
        fc.add_button("_Open", Gtk.ResponseType.OK)
        fc.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        fc.set_default_response(Gtk.ResponseType.OK)
        fc.set_filter(filter_svg)

        filename = fc.run()

        if filename == Gtk.ResponseType.OK:
            svg_filename = fc.get_filename()

            self.window.app.load_data(svg_filename)

        fc.destroy()

    def on_redraw_button_clicked(self, *args, **kwargs):
        if isinstance(self.window.app.svg, SvgSketch):
            self.window.app.svg.update_svg(self.window.app.svg_fields)
            self.window.app.refresh_sketcher()


class SvgSketch:
    def __init__(self, svg_filename):
        self.svg_filename = None
        self.svg = None
        self.svg_xml = None

        self.fields = dict()

        self.load(svg_filename)
        self.get_elements()

    def load(self, svg_filename):
        self.svg_filename = svg_filename

        with open(self.svg_filename) as svg_file:
            svg_data = svg_file.read().encode("utf-8")
            self.svg = Rsvg.Handle.new_from_data(svg_data)
            self.svg_xml = etree.fromstring(svg_data)

    def save(self, svg_filename):

        with open(svg_filename, "wb") as svg_file:
            data = etree.tostring(self.svg_xml)
            svg_file.write(data)

    def get_elements(self):

        for child in self.svg_xml.iterdescendants():

            field = dict()

            if child.tag == "{http://www.w3.org/2000/svg}text":
                field_id = child.attrib["id"]
                field_label = child.attrib["{http://www.inkscape.org/namespaces/inkscape}label"]
                field["label"] = field_label
                for tspan in child.iterdescendants():
                    for tspan_entry in tspan.iterdescendants():
                        if tspan_entry.tag == "{http://www.w3.org/2000/svg}tspan":
                            field_text = tspan_entry.text
                            field["text"] = field_text

                self.fields[field_id] = field

    @property
    def get_pixbuf(self):
        return self.svg.get_pixbuf()

    @property
    def get_fields(self):
        return self.fields

    def set_field(self, element_id, text):
        self.fields[element_id]['text'] = text

    def update_svg(self, fields):
        for k, v in fields.items():
            for child in self.svg_xml:
                if child.tag == "{http://www.w3.org/2000/svg}g":
                    for text_element in child:
                        if text_element.tag == "{http://www.w3.org/2000/svg}text":
                            if text_element.attrib["id"] == k:
                                for tspan in text_element.iterdescendants():
                                    for tspan_entry in tspan.iterdescendants():
                                        if tspan_entry.tag == "{http://www.w3.org/2000/svg}tspan":
                                            tspan_entry.text = v["text"]

        self.save(self.svg_filename)


def main():
    app = TurBoSketcher()
    app.run()


if __name__ == "__main__":
    main()
