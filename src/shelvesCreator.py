#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Shelves creator."""

import os
import sys
from functools import wraps

import maya.cmds as cmds


class ShelvesCreator(object):
    """Shelves creator."""
    
    ICON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')

    def __init__(self, name, python_path='', icon_path='', color=(1, 1, 1), bgcolor=(0.0,0.05,0.10,0.75)):
        """Initialize ShelfCreator.
        
        Args:
            name (str): Shelf name.
            python_path (path): Append python path before run a command. 
            icon_path (path): icon folder path.
            color (tuple): Color text.
            bgcolor (tuple): Background color text.
        """
        super(ShelfCreator, self).__init__()
        self.name = name if name else 'NoName'
        self.icon_path = icon_path
        self.color = color
        self.bgcolor = bgcolor

        self.setPythonPath(python_path)
        self._updateShelvesInfo()

    def __enter__(self):
        self.createShelf()
        self.resetShelf()
        return self

    def __exit__(self, type, value, traceback):
        return None

    def _updateShelvesInfo(self):
        """Update shelves info."""
        self.exists = cmds.shelfLayout(self.name, exists=True)
        self.buttons = cmds.shelfLayout(self.name, query=True, childArray=True) if self.exists else []
        self.layout = '%s|%s' % (cmds.shelfLayout(self.name, q=True, p=True), self.name) if self.exists else ''

    def _wrapUpdateShelves(f):
        """Wrap the '_updateShelvesInfo' function."""
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            try:
                f(self, *args, **kwargs)
            finally:
                self._updateShelvesInfo()

        return wrapper

    @_wrapUpdateShelves
    def createShelf(self):
        """Create shelf."""
        if not self.exists:
            self.layout = cmds.shelfLayout(self.name, parent='ShelfLayout')

    @_wrapUpdateShelves
    def resetShelf(self):
        """Remove all buttons from Shelf."""
        if self.exists:
            if self.buttons:
                for btn in self.buttons:
                    cmds.deleteUI(btn)  

    @_wrapUpdateShelves
    def deleteShelf(self):
        """Delete Shelf."""
        if self.exists:
            if self.buttons:
                for btn in self.buttons:
                    cmds.deleteUI(btn)   
            cmds.deleteUI(self.name)

    @_wrapUpdateShelves
    def createButton(self, command, label='', annotation='', color=None, bgcolor=None, icon=''):
        """Create Btn to current shelf.

        Args:
            command (str): Python command.
            label (str): Label name.
            annotation (str): Annotation.
            color (tuple): Color text.
            bgcolor (tuple): Background color text.
            icon (path): Button's icon.
        """
        # Get color and background color.
        if not isinstance(color, tuple):
            color = self.color

        if not isinstance(bgcolor, tuple):
            bgcolor = self.bgcolor

        # Get icons.
        img = os.path.join(self.icon_path, icon)
        IMG = os.path.join(self.ICON_PATH, icon)

        image = 'pythonFamily.png'
        if os.path.exists(img):
            image = img
        else:
            if os.path.exists(IMG):
                image = IMG

        # Create button
        cmds.shelfButton(
            c=self._python_path + command,
            iol=label,
            ann=annotation,
            olc=color,
            olb=bgcolor,
            i=image,
            stp='python',
            p=self.layout,
            fwt=1,
            )

    @_wrapUpdateShelves
    def createSeparator(self, width=24, height=35, style='single'):
        """Create Separator.
        
        Args:
            width (int): Separator width. Default to 40.
            height (int): Separator height. Default to 35.
            style (str): Either 'single' or 'shelf'. Default to 'single'.
        """
        cmds.separator(w=width, h=height, st=style, hr=False, p=self.layout)

    def setPythonPath(self, path):
        """Append python path before run a script."""
        if path:
            self._python_path = 'p_ = "%s"; import sys; sys.path.insert(0, p_) if p_ not in sys.path else None; ' % path
        else:
            self._python_path = ''

    def setIconPath(self, path):
        """Set icons folder path."""
        self.icon_path = path
            


def onMayaDroppedPythonFile(*args, **kwargs):
    """Run function when this python file is dropped into Maya."""
    with ShelvesCreator('CustomShelf', '') as shelf:

        shelf.createButton(
            command='from lighting import lightToolkit; reload(lightToolkit); lightToolkit.main();',
            label='LTK',
            annotation='Creep Light toolkit.',
            icon='icon_lightning.png')

        shelf.createButton(
            command='from lighting import lightMaker; reload(lightMaker); lightMaker.main();',
            label='MKR',
            annotation='Creep Light maker.',
            icon='icon_lightning.png')

        shelf.createSeparator()

        shelf.createButton(
            command="from animation import sceneAssembly; reload(sceneAssembly); sa = sceneAssembly.SceneAssembly(); sa.setProject(); from sceneAssembly import preRender; reload(preRender); preRender.main(); import pymel.core as pm; plug='crp_rrSubmit_Maya_2017+'; pm.loadPlugin(plug, quiet=True); pm.pluginInfo(plug, q=True, loaded=True); pm.rrSubmit();",
            label='RR',
            annotation='Submit to RR.',
            icon='icon_upload.png')
