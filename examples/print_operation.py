#!/usr/bin/env python

import os
import sys
from gi.repository import GLib, Gtk, Poppler


class PrintingApp:
    def __init__(self, file_uri):
        self.operation = Gtk.PrintOperation()

        self.operation.connect('begin-print', self.begin_print, None)
        self.operation.connect('draw-page', self.draw_page, None)

        self.doc = Poppler.Document.new_from_file(file_uri)

    def begin_print(self, operation, print_ctx, print_data):
        operation.set_n_pages(self.doc.get_n_pages())

    def draw_page(self, operation, print_ctx, page_num, print_data):
        cr = print_ctx.get_cairo_context()
        page = self.doc.get_page(page_num)
        page.render(cr)

    def run(self, parent=None):
        result = self.operation.run(Gtk.PrintOperationAction.PRINT_DIALOG,
                                    parent)

        if result == Gtk.PrintOperationResult.ERROR:
            message = self.operation.get_error()

            dialog = Gtk.MessageDialog(parent,
                                       0,
                                       Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE,
                                       message)

            dialog.run()
            dialog.destroy()

        Gtk.main_quit()


def main():
    if len(sys.argv) != 2:
        print("%s FILE" % sys.argv[0])
        sys.exit(1)

    file_uri = GLib.filename_to_uri(os.path.abspath(sys.argv[1]))

    main_window = Gtk.OffscreenWindow()
    app = PrintingApp(file_uri)
    GLib.idle_add(app.run, main_window)
    Gtk.main()


if __name__ == '__main__':
    main()
