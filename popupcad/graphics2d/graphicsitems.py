# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

class Common(object):
    z_value = 0
    isDeletable = False

    def allchildren(self):
        return self.childItems()
        
    def softdelete(self):
        if self.isDeletable:
            self.harddelete()

    def harddelete(self):
        for child in self.allchildren():
            child.setParentItem(None)
            child.harddelete()
            del child
        self.setParentItem(None)
        self.removefromscene()
        del self

    def removefromscene(self):
        try:
            self.scene().removeItem(self)
        except AttributeError:
            pass

    def constraintsystem(self):
        return self.scene().sketch.constraintsystem
        
    def sketch(self):
        return self.scene().sketch


class CommonShape(object):
    def create_selectable_edge_loop(self):
        from popupcad.geometry.line import ShapeLine
        self.selectableedges = []
        exterior = self.generic.get_exterior()
        for handle1,handle2 in zip(exterior,exterior[1:]+exterior[0:1]):
            genericline = ShapeLine(handle1,handle2)
            item = genericline.gen_interactive()
            self.selectableedges.append(item)  
    def create_selectable_edge_path(self):
        from popupcad.geometry.line import ShapeLine
        self.selectableedges = []
        exterior = self.generic.get_exterior()
        for handle1,handle2 in zip(exterior[:-1],exterior[1:]):
            genericline = ShapeLine(handle1,handle2)
            item = genericline.gen_interactive()
            self.selectableedges.append(item)  
    def create_selectable_edges(self):
        self.create_selectable_edge_loop()
    def updateshape(self):
        path = self.painterpath()
        self.setPath(path)
        self.update()

