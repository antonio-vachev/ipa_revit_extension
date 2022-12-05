# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

import System
from System.Collections.Generic import *

from pyrevit import revit, DB
from pyrevit import forms
import logexporter

doc = revit.doc

elements=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_LightingFixtures).WhereElementIsElementType().ToElements()

refplanes=DB.FilteredElementCollector(doc).OfClass(DB.ReferencePlane).ToElements()

class SymbolName(forms.TemplateListItem):
    @property
    def name(self):
        return "{}-{}".format(self.FamilyName,self.LookupParameter('Type Name').AsString()) 

class RefPlaneName(forms.TemplateListItem):
    @property
    def name(self):
        return self.Name


symbols=list(map(lambda x: SymbolName(x), elements))  
symbol = forms.SelectFromList.show(symbols,
                                multiselect=False,
                                button_name='Select Item')

refs=list(map(lambda x: RefPlaneName(x), refplanes))  
refplane = forms.SelectFromList.show(refs,
                                multiselect=False,
                                button_name='Select Item')


XY=forms.ask_for_string(default="2x2",prompt="Define Array in Format Columns x Rows",title="Fixture Array")


p1 = revit.pick_point('Pick First Point')
p2 = revit.pick_point('Pick Second Point')

if p1 != None and p2 != None:
	p=DB.XYZ((p1.X+p2.X)/2,(p1.Y+p2.Y)/2,refplane.GetPlane().Origin.Z)

	points=[]

	Xcoords=[]
	Xcount=int(XY[0])
	Xstep=abs(p1.X-p2.X)/Xcount

	if p1.X<p2.X:
		xcoord=p1.X-Xstep/2
	else:
		xcoord=p2.X-Xstep/2

	for i in range(0,Xcount):
		xcoord=xcoord+Xstep
		Xcoords.append(xcoord)

	Ycoords=[]
	Ycount=int(XY[-1])
	Ystep=abs(p1.Y-p2.Y)/Ycount

	if p1.Y<p2.Y:
		ycoord=p1.Y-Ystep/2
	else:
		ycoord=p2.Y-Ystep/2

	for i in range(0,Ycount):
		ycoord=ycoord+Ystep
		Ycoords.append(ycoord)

	for x in Xcoords:
		for y in Ycoords:
			points.append(DB.XYZ(x,y,refplane.GetPlane().Origin.Z))


t=DB.Transaction(doc,"Place Lighting Fixtures")
t.Start()

if symbol != None and refplane !=None and XY !=None and p1 != None and p2 != None:
	for p in points:
		doc.Create.NewFamilyInstance(refplane.GetReference(),p,DB.XYZ(0,0,0),symbol)
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)
