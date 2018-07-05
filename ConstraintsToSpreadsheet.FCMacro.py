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
__date__ = "2018.07.05" #year.month.date
__version__ = __date__

import FreeCAD
from PySide import QtCore,QtGui
import math

sketches=[]
sheet = None
window = QtGui.QApplication.activeWindow()
aliases=[]

class SSHelper:
    def __init__(self, obj):
        obj.Proxy = self

   
    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''

        if 'Hidden_' in str(prop):
            alias = str(prop)[7:]
            setattr(fp,alias,float(getattr(fp,str(prop))))
            return
        #FreeCAD.Console.PrintMessage("Change property: " + str(prop) + "\n")
        if hasattr(sheet,str(prop)):
            if str(prop)=='ExpressionEngine' or str(prop) == 'Label':
                return
            if str(sheet.get(str(prop)))==str(getattr(fp,str(prop))):
                FreeCAD.Console.PrintMessage('Sheet property already set: '+str(prop)+'='+str(getattr(fp,str(prop)))+'\n')
                return
            try:
                FreeCAD.Console.PrintMessage('Setting Sheet property: '+str(prop)+' to: '+str(getattr(fp,str(prop)))+'\n')
                setattr(sheet,str(prop),float(getattr(fp,str(prop))))
                sheet.set(str(prop),str(getattr(fp,str(prop))))
                setCell(sheet,str(prop),getattr(fp,str(prop)))
            except:
                FreeCAD.Console.PrintMessage("exception converting to float: "+str(prop)+"\n")

 
    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        pass
        #FreeCAD.Console.PrintMessage("Recompute Python SSHelper feature\n")


def addSpreadsheet(sheet):
    if hasattr(ssHelper,"Spreadsheet"):
        setattr(ssHelper,"Spreadsheet",sheet)
        return
    ssHelper.addProperty("App::PropertyLink","Spreadsheet","Base","Linked spreadsheet").Spreadsheet=sheet
    ssHelper.setEditorMode("Spreadsheet",1)#readonly
def addAlias(alias,tip,value):
    ssHelper.addProperty("App::PropertyFloat",str(alias),"Aliases",tip)
    setattr(ssHelper,alias,value)
    aliases.append(alias)
    addHiddenAlias(alias,tip,value)

def addHiddenAlias(alias,tip,value):
    ssHelper.addProperty("App::PropertyFloat","Hidden_"+str(alias),"HiddenAliases (acting as spreadsheet observers)",tip)
    setattr(ssHelper,alias,value)
    ssHelper.setExpression('Hidden_'+str(alias), sheet.Label+'.'+alias)
    aliases.append(alias)
    ssHelper.setEditorMode('Hidden_'+str(alias),2)#hidden and readonly

def removeAlias(alias):
    ssHelper.removeProperty(alias)

def removeAllAliases():
    for prop in ssHelper.PropertiesList:
        if prop == 'ExpressionEngine' or prop == 'Label' or prop == 'Proxy' or prop == 'Spreadsheet':
            continue
        removeAlias(prop)

if not hasattr(App.ActiveDocument,"SSHelper"):
    ssHelper=FreeCAD.ActiveDocument.addObject("App::FeaturePython","SSHelper")
    SSHelper(ssHelper)
else:
    App.ActiveDocument.removeObject("SSHelper")
    ssHelper=App.ActiveDocument.addObject("App::FeaturePython","SSHelper")
    SSHelper(ssHelper)
    removeAllAliases()
    

#addAlias("someAlias","this is some kind of alias", float(3.1415926535))
#addAlias("some_other_alias","this is some other alias",float(3.14))
#removeAlias("someAlias")



def setCell(sheet,cell,value):
    sheet.set(cell,str(value))



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
if len(allSketches)>len(sketches):
    items=["Process all sketches in the document, even unselected ones", "Only process selected sketches."]
    item,ok = QtGui.QInputDialog.getItem(window,'Unselected sketches in document','Process unselected sketches?',items,0,False)
    if ok:
        if item==items[0]:
            sketches = allSketches
        else:
            raise StandardError('user canceled')
    else:
        raise StandardError('user canceled')
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
            sheet = App.ActiveDocument.getObject('Spreadsheet')
        elif item==items[1] and sheet:
            pass #use the sheet found
        elif item==items[1] and not sheet:
            raise StandardError('user canceled')
    else:
        raise StandardError('user canceled')
    
addSpreadsheet(sheet)
sheet.clear('A1:D200')
removeAllAliases()
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
            if con.Name[-1:]=='_':
                continue #ignore constraint names beginning with single underscore
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
                addAlias(con.Name,con.Name,float(con.Value))


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


