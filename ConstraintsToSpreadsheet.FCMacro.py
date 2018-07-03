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

This is a macro to aid setting up a spreadsheet to contain all the named constraints in one or more sketches.  To use the macro 
Select the sketches containing the named constraints you wish to add to a spreadsheet and run the macro.  If you already have 
a spreadsheet you can select it along with the sketch(es) and the selected spreadsheet will be used.  If you do not select a 
spreadsheet along with the sketch(es) you will prompted to either have the macro create a spreadsheet for you and use it or to 
cancel the operation.

The macro parses all the selected sketches looking for named constraints (unnamed constraints are ignored).  It adds all named 
constraints to the spreadsheet using columns A, B, C, and D for the constraint name, value, type, and sketch name, respectively. 
The column B value (value of the constraint) will be assigned an alias equal to the constraint name, e.g. if the name of the 
constraint is circle1Radius, then circle1Radius becomes the alias for the cell in column B, for example, B7.  The sketch is 
also modified in that the named constraint will now reference the spreadsheet using the alias created.

Be warned: Cells A1-D200 are reset each time the macro is run, so any values contained in any of those cells will be lost.  
Place any user values you don't want the macro to delete in columns E, F, G, etc.

**ALWAYS** select **ALL** sketches you want to use with the spreadsheet when running the macro because unselected sketches 
will be de-referenced.  (If you accidentally forget to select them all, this is easily remedied by running the macro again 
with all the sketches selected.)

"""

__title__ = "ConstraintsToSpreadsheet"
__author__ = "TheMarkster"
__url__ = "https://github.com/mwganson/ConstraintsToSpreadsheet"
__Wiki__ = "https://github.com/mwganson/ConstraintsToSpreadsheet/blob/master/README.md"
__date__ = "2018.07.03" #year.month.date
__version__ = __date__

import FreeCAD
from PySide import QtCore,QtGui
import math


sketches=[]
sheet = None
window = QtGui.QApplication.activeWindow()
def setCell(sheet,cell,value):
    sheet.set(cell,str(value))



selection = FreeCADGui.Selection.getSelectionEx()
if len(selection)<1:
    raise StandardError('Select the Sketch(es) with the named constraints and the Spreadsheet to which you wish to add the named constraints.')

for sel in selection:
    if 'SketchObject' in sel.TypeName:
        sketches.append(sel.Object)
    elif 'Spreadsheet' in sel.TypeName:
        sheet = sel.Object

if not sheet:

    items=["Create new spreadsheet","Cancel"]
    item,ok = QtGui.QInputDialog.getItem(window,'No spreadsheet selected','Create new sheet?',items,0,False)
    if ok:
        if item==items[0]:
            App.activeDocument().addObject('Spreadsheet::Sheet','Spreadsheet')
            sheet = App.ActiveDocument.getObject('Spreadsheet')
        else:
            raise StandardError('user canceled')
    else:
        raise StandardError('user canceled')
    

sheet.clear('A1:D200')
setCell(sheet,'A1','Warning: A1-D200 get reset each time the macro is run.  Place any values you do not want changed in Column E and beyond.')
App.ActiveDocument.Spreadsheet.setForeground('A1:H1', (1.000000,0.000000,0.000000,1.000000)) #red text
sheet.mergeCells('A1:H1')

setCell(sheet,'A2','name')
setCell(sheet,'B2','value')
setCell(sheet,'C2','type')
setCell(sheet,'D2','sketches')

mappedSketches={}
ii=3
for sketch in sketches:
    for con in sketch.Constraints:
        if con.Name:

            setCell(sheet,'A'+str(ii),con.Name)
            if con.Type == 'Angle':
                setCell(sheet,'B'+str(ii),con.Value*180.0/math.pi)
            else:
                setCell(sheet,'B'+str(ii),con.Value)
            setCell(sheet,'C'+str(ii),con.Type)

            if con.Name in mappedSketches:
                mappedSketches[con.Name]=mappedSketches[con.Name]+','+sketch.Label
            else:
                mappedSketches[con.Name]=sketch.Label
            setCell(sheet,'D'+str(ii),mappedSketches[con.Name])

            try:
                sheet.setAlias('B'+str(ii),con.Name)
            except:
                #presume alias already exists, so clear this row
                setCell(sheet,'A'+str(ii),'')
                setCell(sheet,'B'+str(ii),'')
                setCell(sheet,'C'+str(ii),'')
                setCell(sheet,'D'+str(ii),'')
                ii -=1 




            sketch.setExpression('Constraints.'+con.Name, sheet.Name+'.'+con.Name)
            ii += 1
App.ActiveDocument.recompute()
for jj in range(3,ii):
    try:
        rowName = sheet.get('A'+str(jj))
        sheet.set('D'+str(jj),mappedSketches[rowName])        
    except:
        pass #oops
            

App.ActiveDocument.recompute()


