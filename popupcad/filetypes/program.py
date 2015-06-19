# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""
import sys
import PySide.QtGui as qg
import popupcad


class Program(object):

    def __init__(self, plugins, *args, **kwargs):

        args = list(args)
        if hasattr(sys, 'frozen'):
            pass
        else:
            import clear_compiled
            clear_compiled.clear_compiled()

        for item in args:
            if '--deprecated' in item:
                import popupcad_deprecated
                popupcad.deprecated = popupcad_deprecated
                sys.modules['popupcad.deprecated'] = popupcad_deprecated
                args.pop(args.index(item))

        self.app = qg.QApplication(args[0])
        self.app.setWindowIcon(popupcad.supportfiles.Icon('popupcad'))
        self.editor = popupcad.guis.editor.Editor()

        if len(args) > 1 and not '--' in args[-1]:
            self.editor.open(filename=args[-1])
        self.editor.show()
        for plugin in plugins:
            plugin.initialize(self)
