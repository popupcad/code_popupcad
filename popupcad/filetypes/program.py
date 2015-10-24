# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes and CONTRIBUTORS
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE for full license.
"""
import sys
import PySide.QtGui as qg
import popupcad
import logging
import traceback

class Program(object):

    def __init__(self, app,plugins, *args, **kwargs):

        args = list(args)

#        for item in args:
#            if '--deprecated' in item:
#                import popupcad_deprecated
#                popupcad.deprecated = popupcad_deprecated
#                sys.modules['popupcad.deprecated'] = popupcad_deprecated
#                args.pop(args.index(item))

        self.app = app
        icons = popupcad.guis.icons.build()
        self.app.setWindowIcon(icons['printapede'])
        self.editor = popupcad.guis.editor.Editor()

        if len(args) > 1 and not '--' in args[-1]:
            self.editor.open(filename=args[-1])
        self.editor.show()
        self.create_exception_listener()

        for plugin in plugins:
            plugin.initialize(self)

    def create_exception_listener(self):
        logging.basicConfig(filename=popupcad.error_log_filename,filemode='w',level=logging.DEBUG)
        self.excepthook_internal = sys.excepthook
        sys.excepthook = self.excepthook
        
    def excepthook(self,exctype,value,tb):
        if exctype is not SystemExit:
            message = '''{}: {}'''.format(str(exctype),str(value))
            print(message)
    
            tbmessage = traceback.format_tb(tb)
            tbmessage = '  '.join(tbmessage)
    
            logging.error(message)
            logging.debug('\n'+tbmessage)
            
            self.editor.error_log.appendText(message+'\n'+tbmessage)
            self.excepthook_internal(exctype,value,tb)
            mb = qg.QMessageBox()
            mb.setText(message)
            mb.exec_()
        
        
