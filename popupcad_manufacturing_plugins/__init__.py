# -*- coding: utf-8 -*-
"""
Written by Daniel M. Aukes.
Email: danaukes<at>seas.harvard.edu.
Please see LICENSE.txt for full license.
"""

from . import manufacturing
from . import algorithms

#import external modules
import PySide
import numpy
import shapely

def initialize(program):
    from popupcad.supportfiles import Icon

    scrap = []
    scrap.append(
        {
            'text': 'Sheet',
            'kwargs': {
                'icon': Icon('outersheet'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.outersheet3.OuterSheet3)}})
    scrap.append(
        {
            'text': '&Web',
            'kwargs': {
                'icon': Icon('outerweb'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.autoweb4.AutoWeb4)}})
    scrap.append(
        {
            'text': 'Scrap',
            'kwargs': {
                'icon': Icon('scrap'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.scrapoperation2.ScrapOperation2)}})

    supportactions = []
    supportactions.append(
        {
            'text': 'S&upport',
            'kwargs': {
                'icon': Icon('autosupport'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.supportcandidate4.SupportCandidate4)}})
    supportactions.append(
        {
            'text': 'Custom Support',
            'kwargs': {
                'icon': Icon('customsupport'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.customsupport4.CustomSupport4)}})

    other = []
    other.append(
        {
            'text': 'Keep-out',
            'kwargs': {
                'icon': Icon('firstpass'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.keepout3.KeepOut3)}})
#    other.append({'text':'Cuts','kwargs':{'icon':Icon('firstpass'),'triggered':lambda:program.editor.newoperation(manufacturing.cutop2.CutOperation2)}})
    other.append(
        {
            'text': 'Identify Rigid Bodies',
            'kwargs': {
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.identifyrigidbodies2.IdentifyRigidBodies2)}})

    manufacturingactions = []
    manufacturingactions.append(
        {'text': 'Scrap', 'submenu': scrap, 'kwargs': {'icon': Icon('scrap')}})
    manufacturingactions.append({'text': 'Supports',
                                 'submenu': supportactions,
                                 'kwargs': {'icon': Icon('outerweb')}})
#        manufacturingactions.append({'text':'Tool Clearance','kwargs':{'triggered':lambda:program.editor.newoperation(ToolClearance2)}})
    manufacturingactions.append(
        {
            'text': 'Removability',
            'kwargs': {
                'icon': Icon('removability'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.removability2.Removability2)}})
    manufacturingactions.append(
        {
            'text': 'Identify Bodies',
            'kwargs': {
                'icon': Icon('identifybodies'),
                'triggered': lambda: program.editor.newoperation(
                    manufacturing.identifybodies2.IdentifyBodies2)}})
    manufacturingactions.append(
        {'text': 'Misc', 'submenu': other, 'kwargs': {'icon': Icon('dotdotdot')}})

    program.editor.toolbar_manufacturing, program.editor.menu_manufacturing = program.editor.addToolbarMenu(
        manufacturingactions, name='Manufacturing')
