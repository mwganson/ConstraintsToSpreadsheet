# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2018 <TheMarkster>                                      *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License at http://www.gnu.org/licenses     *
*   for more details.                                                     *
*                                                                         *
*   For more information about the GNU Library General Public License     *
*   write to the Free Software Foundation, Inc., 59 Temple Place,         *
*   Suite 330, Boston, MA  02111-1307 USA                                 *
*                                                                         *
***************************************************************************
"""

#OS: Windows 10
#Word size of OS: 64-bit
#Word size of FreeCAD: 64-bit
#Version: 0.17.13522 (Git)
#Build type: Release
#Branch: releases/FreeCAD-0-17
#Hash: 3bb5ff4e70c0c526f2d9dd69b1004155b2f527f2
#Python version: 2.7.14
#Qt version: 4.8.7
#Coin version: 4.0.0a
#OCC version: 7.2.0
#Locale: English/UnitedStates (en_US)



"""
ConstraintsToSpreadsheet

Warning: this does modify your sketch.  You should make a backup of your document just in case something goes wrong.

This is a macro to aid setting up a spreadsheet to contain all the named constraints in one or more sketches.  If the document 
contains one or more unselected the sketches the macro will ask the user if he wishes to use all unselected sketches or if he 
wants to cancel the operation.  Those are the 2 choices: 1) use all sketches in the document; 2) cancel.

If there are sketches you do not wish to include in the processing, you will need to relabel them in the tree view, appending 
an underscore (_) to the end of the label.  Example: to tell the macro not to use Sketch005 you would relabel it to be Sketch005_ 
or any other name ending with the _.  Similarly, if there are named constraints you do not wish to be included in the processing, 
you will need to append an underscore (_) to the ends of their names, too.

If an existing spreadsheet is selected the macro will quietly use it.  If no spreadsheets are selected the macro will search for 
unselected spreadsheets in the document and offer to use the first one it finds.  If no spreadsheets are found the macro will offer 
to create a new spreadsheet for you.

Be warned: Cells A1-D200 are reset each time the macro is run, so any values contained in any of those cells will be lost.  
Place any user values you don't want the macro to delete in columns E, F, G, etc.

What the macro does: It takes all named sketch constraints (not ending in underscores) and adds the name as an alias into a spreadsheet.  
It then links the constraint to the alias in the spreadsheet, thus modifying the constraint in the process.  The *value* of the constraint is set 
in the spreadsheet (*not* the formula used to derive that value), if applicable.

In previous versions of this macro there was an ssHelper object added to the document, but this feature has been removed in order
to simplify the code and the usage of the macro.  Similarly, in previous versions there was the capability to take expressions 
from other objects and add them to the spreadsheet, but this feature has also been removed.  Sometimes less is more...


"""

__title__ = "ConstraintsToSpreadsheet"
__author__ = "TheMarkster"
__url__ = "https://github.com/mwganson/ConstraintsToSpreadsheet"
__Wiki__ = "https://github.com/mwganson/ConstraintsToSpreadsheet/blob/master/README.md"
__date__ = "2018.08.20" #year.month.date
__version__ = __date__

import FreeCAD
from PySide import QtCore,QtGui
import math

if not App.ActiveDocument:
    raise StandardError('No active document.\n')

sketches=[]
sheet = None
sketch=None
processObjects = False
window = QtGui.QApplication.activeWindow()
aliases=[]




def setCell(sheet,cell,value):
    #FreeCAD.Console.PrintMessage("setCell called, sheet = "+str(sheet.Name)+", cell="+str(cell)+", value = "+str(value)+"\n")
    if hasattr(value,'Value'): #strip off the 'mm' 'deg' etc
        val = value.Value
    else:
        val = value
    sheet.set(cell,str(val))

def handleConstraint(name,value,type,idx): 
    #FreeCAD.Console.PrintMessage("handleConstraint called, name = "+str(name)+", value = "+str(value)+", type = "+str(type)+", idx = "+str(idx)+"\n")
    ii = idx
    setCell(sheet,'A'+str(ii),name)
    if type == 'Angle':
        setCell(sheet,'B'+str(ii),value*180.0/math.pi)
    else:
        setCell(sheet,'B'+str(ii),value)
    setCell(sheet,'C'+str(ii),type)

    if name in mappedSketches:
        mappedSketches[name]=mappedSketches[name]+','+sketch.Label
    else:
        if sketch:
            mappedSketches[name]=sketch.Label

    setCell(sheet,'D'+str(ii),mappedSketches[name])

    try:
        sheet.setAlias('B'+str(ii),name)
        success=True
    except:
        #on exception presume alias already exists, so clear this row
        success=False
        setCell(sheet,'A'+str(ii),'')
        setCell(sheet,'B'+str(ii),'')
        setCell(sheet,'C'+str(ii),'')
        setCell(sheet,'D'+str(ii),'')
        ii -=1 
    if success:
        sketch.setExpression('Constraints.'+name, sheet.Name+'.'+name)

    ii += 1
    return ii

selection = FreeCADGui.Selection.getSelectionEx()

for sel in selection:
    if 'SketchObject' in sel.TypeName:
        sketches.append(sel.Object)
    elif 'Spreadsheet' in sel.TypeName:
        sheet = sel.Object
allSketches=[]
for obj in App.ActiveDocument.Objects:
    if 'SketchObject' in str(type(obj)):
        allSketches.append(obj)
#use only the selected sketches if one or more are selected, else ask to use all sketches in document

if len(sketches) != len(allSketches):
    sketches=allSketches
    items=("Use all sketches (except those with labels ending in underscores (_))", "Cancel")
    item,ok = QtGui.QInputDialog.getItem(window,'Found unselected sketches','Use all sketches?',items,0,False)
    if not ok:
        raise StandardError('User canceled.')
    elif item==items[1]:
        raise StandardError('User canceled.')

if not sheet:
    for obj in App.ActiveDocument.Objects:
        if 'Spreadsheet' in str(type(obj)):
            sheet = obj
            break
    if sheet:
        items=["Create new spreadsheet","Use "+sheet.Label,"Cancel"]
    else:
        items=["Create new spreadsheet", "Cancel"]
    item,ok = QtGui.QInputDialog.getItem(window,'No spreadsheet selected','Create new sheet?',items,0,False)
    if ok:
        if item==items[0]:
            App.activeDocument().addObject('Spreadsheet::Sheet','Spreadsheet')
            sheet = App.ActiveDocument.ActiveObject
        elif item==items[1] and sheet:
            pass #use the sheet already found
        elif item==items[1] and not sheet:
            raise StandardError('user canceled')
    else:
        raise StandardError('user canceled')
    
sheet.clear('A1:D200')
setCell(sheet,'A1','Auto-generated aliases by macro ConstraintsToSpreadsheet, content in columns A-D *will be clobbered* each time the macro is run!')
sheet.setForeground('A1:H1', (1.000000,0.000000,0.000000,1.000000)) #red text
sheet.mergeCells('A1:H1')

setCell(sheet,'A2','name')
setCell(sheet,'B2','value')
setCell(sheet,'C2','type')
setCell(sheet,'D2','sketch')

mappedSketches={}
ii=3
for sketch in sketches:
    if sketch.Label[-1:]=='_': #skip sketches with labels ending in underscore
        continue
    for con in sketch.Constraints:
        if con.Name:
            if con.Name[-1:]=='_':
                continue #ignore constraint names ending with underscore
            ii=handleConstraint(con.Name,con.Value,con.Type,ii)

for jj in range(3,ii):
    try:
        App.ActiveDocument.recompute()
        rowName = sheet.get('A'+str(jj))
        sheet.set('D'+str(jj),mappedSketches[rowName])        
    except:
        FreeCAD.Console.PrintError('Exception adding column D sketch name\n')
            

App.ActiveDocument.recompute()
#FreeCAD.Console.PrintMessage('Done\n')
pass

