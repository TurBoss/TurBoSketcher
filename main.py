#!/usr/bin/python3

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Rsvg", "2.0")

from gi.repository import Gtk
from gi.repository import Rsvg

from lxml import etree
import cairosvg

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

        self.window.create_entry(self.svg_fields)

        self.window.set_svg(self.svg_pixbuf)

    def refresh_sketcher(self):
        self.svg = SvgSketch(self.svg_filename)

        self.svg_fields = self.svg.get_fields
        self.svg_pixbuf = self.svg.get_pixbuf

        self.window.set_svg(self.svg_pixbuf)

    def update_sketch(self, element_id, element_text):
        print("UPDATE")

        if isinstance(self.window.app.svg, SvgSketch):
            self.svg.set_field(element_id, element_text)
            self.svg.update_svg(self.svg_fields)
            self.refresh_sketcher()

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

    def create_entry(self, svg_fields):
        for id, data in svg_fields.items():
            label = Gtk.Label()
            label.set_text(data["label"])
            label.show_all()

            entry = Gtk.Entry()
            entry.set_text(data["text"])
            entry.set_name(id)
            entry.connect("activate", self.on_entry_activate)
            entry.show_all()

            separator = Gtk.Separator()
            separator.show_all()

            self.field_box.pack_start(label, True, True, 0)
            self.field_box.pack_start(entry, True, True, 0)
            self.field_box.pack_start(separator, True, True, 0)

    def on_entry_activate(self, entry):
        entry_id = entry.get_name()
        entry_text = entry.get_buffer().get_text()

        self.app.update_sketch(entry_id, entry_text)


class TurBoSketcherHandler:
    def __init__(self, window):
        self.window = window
        self.window.connect('delete-event', Gtk.main_quit)

    def on_menu_open_activate(self, *args, **kwargs):

        if isinstance(self.window.app.svg, SvgSketch):
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, "Aun no esta implementado ")
            dialog.format_secondary_text(
                "Aun no es posible abrir un documento con un ya abierto.\nCierre la aplicacion y  abra uno nuevo")
            dialog.run()
            dialog.destroy()
        else:
            filter_svg = Gtk.FileFilter()
            filter_svg.set_name('Sketch')
            filter_svg.add_mime_type('image/svg+xml')

            fc = Gtk.FileChooserDialog("Load Sketch", self.window, Gtk.FileChooserAction.OPEN)

            fc.add_button("_Open", Gtk.ResponseType.OK)
            fc.add_button("_Cancel", Gtk.ResponseType.CANCEL)
            fc.set_default_response(Gtk.ResponseType.OK)
            fc.set_filter(filter_svg)

            filename = fc.run()

            if filename == Gtk.ResponseType.OK:
                svg_filename = fc.get_filename()

                self.window.app.load_data(svg_filename)

            fc.destroy()

    def on_menu_save_activate(self, *args, **kwargs):
        self.window.app.svg.save()

    def on_menu_save_as_activate(self, *args, **kwargs):
        filter_svg = Gtk.FileFilter()
        filter_svg.set_name('Sketch')
        filter_svg.add_mime_type('image/svg+xml')

        fc = Gtk.FileChooserDialog("Save Sketch as", self.window, Gtk.FileChooserAction.SAVE)

        fc.add_button("_Save", Gtk.ResponseType.OK)
        fc.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        fc.set_default_response(Gtk.ResponseType.OK)
        fc.set_filter(filter_svg)

        filename = fc.run()

        if filename == Gtk.ResponseType.OK:
            svg_filename = fc.get_filename()

            self.window.app.svg.save(svg_filename)

        fc.destroy()

    def on_menu_pdf_activate(self, *args, **kwargs):
        filter_svg = Gtk.FileFilter()
        filter_svg.set_name('Sketch')
        filter_svg.add_mime_type('application/pdf')

        fc = Gtk.FileChooserDialog("Save Sketch as PDF", self.window, Gtk.FileChooserAction.SAVE)

        fc.add_button("_Save", Gtk.ResponseType.OK)
        fc.add_button("_Cancel", Gtk.ResponseType.CANCEL)
        fc.set_default_response(Gtk.ResponseType.OK)
        fc.set_filter(filter_svg)

        filename = fc.run()

        if filename == Gtk.ResponseType.OK:
            svg_filename = fc.get_filename()

            svg_data = self.window.app.svg.get_data
            cairosvg.svg2pdf(bytestring=svg_data, write_to=svg_filename)

        fc.destroy()


class SvgSketch:
    def __init__(self, svg_filename):
        self.svg_filename = None
        self.svg = None
        self.svg_file = None
        self.svg_xml = None
        self.svg_data = None

        self.fields = dict()

        self.load(svg_filename)
        self.get_elements()

    def load(self, svg_filename):
        self.svg_filename = svg_filename

        with open(self.svg_filename) as svg_file:
            self.svg_file = svg_file
            self.svg_data = svg_file.read().encode("utf-8")
            self.svg = Rsvg.Handle.new_from_data(self.svg_data)
            self.svg_xml = etree.fromstring(self.svg_data)

    def save(self, svg_filename):
        with open(svg_filename, "wb") as svg_file:
            data = etree.tostring(self.svg_xml)
            svg_file.write(data)

    def get_elements(self):

        for child in self.svg_xml.iterdescendants():

            if child.tag == "{http://www.w3.org/2000/svg}text":
                field_label = child.attrib.get("{http://www.inkscape.org/namespaces/inkscape}label", False)
                if field_label:
                    field = dict()
                    field_id = child.attrib["id"]
                    field["label"] = field_label

                    for tspan in child.iterdescendants():
                        if tspan.text is not None:
                            field_text = tspan.text
                            field["text"] = field_text
                        else:
                            for tspan_entry in tspan.iterdescendants():
                                if tspan_entry.tag == "{http://www.w3.org/2000/svg}tspan":
                                    field_text = tspan_entry.text
                                    field["text"] = field_text

                    self.fields[field_id] = field

    @property
    def get_pixbuf(self):
        return self.svg.get_pixbuf()

    @property
    def get_data(self):
        return self.svg_data

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
                                    if tspan.text is None:
                                        for tspan_entry in tspan.iterdescendants():
                                            if tspan_entry.tag == "{http://www.w3.org/2000/svg}tspan":
                                                tspan_entry.text = v["text"]
                                    else:
                                        tspan.text = v["text"]

        self.save(self.svg_filename)


def main():
    app = TurBoSketcher()
    app.run()


if __name__ == "__main__":
    main()
