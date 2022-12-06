#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

import clr

from rpw import db
from pyrevit import DB,UI, revit,forms
import math

import System
from System.Collections.Generic import List
import logexporter

doc = revit.doc

cwalls=[]

assembly_sets=[]
assembly_list=[]

#Defining Selection Filter class

class SelectionFilter(UI.Selection.ISelectionFilter):
	def __init__(self, nom_type):
		self.nom_type = nom_type
	def AllowElement(self, e):		
		if e.WallType.Kind.ToString() == self.nom_type:
			return True
		else:
			return False
	def AllowReference(self, ref, point):
		return true

#User selection filtered for curtain walls only

selected_option = forms.CommandSwitchWindow.show(
    ['Assembly per Wall', 'Assembly from All Walls'],
     message='Select Assembly Creation Option:'
	)


tg=DB.TransactionGroup(doc,"Assembly Creation")
tg.Start()

el_ref=[]

try:
	el_ref = revit.uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element,SelectionFilter("Curtain"))
except:
	pass

if len(el_ref) > 0:
		[cwalls.append(doc.GetElement(er.ElementId)) for er in el_ref]

if selected_option == 'Assembly per Wall' and len(cwalls)>0:
	for cw in cwalls:
		assembly_set=List[DB.ElementId]() 

		for i in cw.CurtainGrid.GetPanelIds():
			if doc.GetElement(i).Category.Name == "Doors" or doc.GetElement(i).Category.Name == "Windows":
				assembly_set.Add(i)
			else:
				if doc.GetElement(i).FindHostPanel().IntegerValue != -1:
					assembly_set.Add(doc.GetElement(i).FindHostPanel())
				else:
					if doc.GetElement(i).get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() >0:
						assembly_set.Add(i)

		for i in cw.CurtainGrid.GetMullionIds():
			assembly_set.Add(i)
	
		t=DB.Transaction(doc,'Create Assemblies')
		t.Start()
		assembly_list.append(DB.AssemblyInstance.Create(doc,assembly_set,doc.GetElement(assembly_set[0]).Category.Id))
		t.Commit()

if selected_option == 'Assembly from All Walls' and len(cwalls)>0:

	assembly_set=List[DB.ElementId]() 
	for cw in cwalls:

		for i in cw.CurtainGrid.GetPanelIds():
			if doc.GetElement(i).Category.Name == "Doors" or doc.GetElement(i).Category.Name == "Windows":
				assembly_set.Add(i)
			else:
				if doc.GetElement(i).FindHostPanel().IntegerValue != -1:
					assembly_set.Add(doc.GetElement(i).FindHostPanel())
				else:
					if doc.GetElement(i).get_Parameter(DB.BuiltInParameter.HOST_AREA_COMPUTED).AsDouble() >0:
						assembly_set.Add(i)

		for i in cw.CurtainGrid.GetMullionIds():
			assembly_set.Add(i)

	t=DB.Transaction(doc,'Create Assemblies')
	t.Start()
	assembly_list.append(DB.AssemblyInstance.Create(doc,assembly_set,doc.GetElement(assembly_set[0]).Category.Id))
	t.Commit()

	for cw in cwalls:
		if cw.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() != max(cw.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble() for cw in cwalls):
			cwalls.remove(cw)

#Filter walls by orientation and set proper TransformRotation rotation angle
#Rotating the Assemblies
#Creating Asseblies Front View

def HideElmsInView(view,elemnt_ids):
	Eids=List[DB.ElementId]()
	[Eids.Add(i) for i in elemnt_ids]
	view.HideElements(Eids)

for cw,a in zip(cwalls,assembly_list):

	if cw.Orientation.X>=-1 and cw.Orientation.X<0 and cw.Orientation.Y>=-1 and cw.Orientation.Y<1:
		if cw.Flipped == False:
			angle=cw.Orientation.AngleTo(a.GetTransform().BasisY)
		else:
			angle=-cw.Orientation.Negate().AngleTo(a.GetTransform().BasisY)

		origin=a.GetTransform()
		TransformRotation=origin.CreateRotationAtPoint(DB.XYZ(0,0,1),angle,origin.Origin)

		t=DB.Transaction(doc,"Rotate Assemblies")
		t.Start()
		a.SetTransform(TransformRotation)
		t.Commit()

		t=DB.Transaction(doc,'Create Assembly Views')
		t.Start()

		ElevationFront=DB.AssemblyViewUtils.CreateDetailSection(doc,a.Id,DB.AssemblyDetailViewOrientation.ElevationFront)
		ElevationFront.DetailLevel = DB.ViewDetailLevel.Fine
		ElevationFront.Scale = 50
		
		HorizontalDetail=DB.AssemblyViewUtils.CreateDetailSection(doc,a.Id,DB.AssemblyDetailViewOrientation.HorizontalDetail)
		HorizontalDetail.DetailLevel = DB.ViewDetailLevel.Fine
		HorizontalDetail.Scale = 50	

		
		elevation_front=db.Collector(view=ElevationFront, of_category='OST_Viewers').get_element_ids()
		horizontal_detail=db.Collector(view=HorizontalDetail, of_category='OST_Viewers').get_element_ids()
		
		HideElmsInView(ElevationFront,elevation_front)
		HideElmsInView(HorizontalDetail,horizontal_detail)
		
		t.Commit()

	else:

		if cw.Flipped == False:
			angle=360*math.pi/180-cw.Orientation.AngleTo(a.GetTransform().BasisY)
		else:
			angle=360*math.pi/180-cw.Orientation.Negate().AngleTo(a.GetTransform().BasisY)
		origin=a.GetTransform()
		TransformRotation=origin.CreateRotationAtPoint(DB.XYZ(0,0,1),angle,origin.Origin)

		t=DB.Transaction(doc,"Rotate Assemblies")
		t.Start()
		a.SetTransform(TransformRotation)
		t.Commit()

		t=DB.Transaction(doc,'Create Assembly Views')
		t.Start()

		ElevationFront=DB.AssemblyViewUtils.CreateDetailSection(doc,a.Id,DB.AssemblyDetailViewOrientation.ElevationFront)
		ElevationFront.DetailLevel = DB.ViewDetailLevel.Fine
		ElevationFront.Scale = 50

		HorizontalDetail=DB.AssemblyViewUtils.CreateDetailSection(doc,a.Id,DB.AssemblyDetailViewOrientation.HorizontalDetail)
		HorizontalDetail.DetailLevel = DB.ViewDetailLevel.Fine
		HorizontalDetail.Scale = 50	

		elevation_front=db.Collector(view=ElevationFront, of_category='OST_Viewers').get_element_ids()
		horizontal_detail=db.Collector(view=HorizontalDetail, of_category='OST_Viewers').get_element_ids()
	
		HideElmsInView(ElevationFront,elevation_front)
		HideElmsInView(HorizontalDetail,horizontal_detail)
		

		t.Commit()
		
tg.Assimilate()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)