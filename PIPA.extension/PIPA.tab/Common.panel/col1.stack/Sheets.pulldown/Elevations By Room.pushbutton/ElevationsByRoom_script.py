#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit,DB,UI,forms
from rpw import db
import math
import itertools
import string
from datetime import datetime

now = datetime.now()
doc=revit.doc

anglecorrection=math.pi


with forms.WarningBar(title='Select Rooms'):
	rooms=revit.pick_elements_by_category("Rooms")
	
	
vft=DB.FilteredElementCollector(doc).OfClass(DB.ViewFamilyType).ToElements()

class MyOption(forms.TemplateListItem):
    @property
    def name(self):
        return self.LookupParameter('Type Name').AsString()

selectlist_elev=[]


for et in vft:
	if str(et.ViewFamily) == 'Elevation':
		selectlist_elev.append(et)



ops_elev=list(map(lambda x: MyOption(x), selectlist_elev))  
res_elev = forms.SelectFromList.show(ops_elev,
                                multiselect=False,
                                title='Select Elevation View Type',
                                button_name='Select')


selectlist_fp=[]

for ft in vft:
	if str(ft.ViewFamily) == 'FloorPlan':
		selectlist_fp.append(ft)


ops_fp=list(map(lambda x: MyOption(x), selectlist_fp))  
res_fp = forms.SelectFromList.show(ops_fp,
                                multiselect=False,
                                title='Select Floor Plan View Type',
                                button_name='Select')		


def unique(items,items2,items3):
	uniqueitems=[]
	uniqueitems2=[]
	uniqueitems3=[]

	for i,i2,i3 in zip(items,items2,items3):
		if i not in uniqueitems:
			uniqueitems.append(i)
			uniqueitems2.append(i2)
			uniqueitems3.append(i3)
			
	return uniqueitems,uniqueitems2,uniqueitems3

def CurveLoop(room):
	elev_crops=[]
	elevations=[]
	crop=[]
	rawcrop=[]
	location_pts=[]
	angles=[]	
	curves=[]
	curveloop=[]

	rheight=room.LookupParameter("Unbounded Height").AsDouble()

	for boundarysegments in room.GetBoundarySegments(DB.SpatialElementBoundaryOptions()):
		for boundarysegment in boundarysegments:
			if doc.GetElement(boundarysegment.ElementId).Category.Name != "<Room Separation>":
				rawcrop.append(boundarysegment.GetCurve()) 


	crop_fp=[]

	for boundarysegments in room.GetBoundarySegments(DB.SpatialElementBoundaryOptions()):
		for boundarysegment in boundarysegments:
			crop_fp.append(boundarysegment.GetCurve()) 

	fp_loop=DB.CurveLoop.CreateViaOffset(DB.CurveLoop.Create(crop_fp),1,DB.XYZ(0,0,1))

	t=DB.Transaction(doc,"Floor Plan By Room")
	t.Start()

	NewFloorPLan=DB.ViewPlan.Create(doc,res_fp.Id,room.LevelId)
	NewFloorPLan.CropBoxActive=True
	NewFloorPLan.GetCropRegionShapeManager().SetCropShape(fp_loop)
	NewFloorPLan.DisplayStyle = DB.DisplayStyle.FlatColors
	NewFloorPLan.DetailLevel = DB.ViewDetailLevel.Fine
	NewFloorPLan.Scale = 50

	NewFloorPLan.LookupParameter("IPA View Group").Set("07 - Building Finishes")
	NewFloorPLan.LookupParameter("IPA View Sub Group").Set("100")
	NewFloorPLan.LookupParameter("Phasing").Set(doc.ActiveView.LookupParameter("Phasing").AsString())

	active_view_name=doc.ActiveView.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString()

	try:
		NewFloorPLan.Name=active_view_name[0:6]+"FF"+active_view_name[8:]+"-"+room.LookupParameter('Number').AsString()
	except:
		NewFloorPLan.Name=active_view_name[0:6]+"FF"+active_view_name[8:]+"-"+room.LookupParameter('Number').AsString()+"_"+now.strftime("%Y-%m-%d_%H_%M_%S")

	t.Commit()

	rawcrop = list(filter(lambda x: DB.UnitUtils.ConvertFromInternalUnits(x.Length,DB.DisplayUnitType.DUT_CENTIMETERS) >50 and x.GetType() != DB.Arc,rawcrop))		

	for k,g in itertools.groupby(rawcrop,lambda x: round(math.atan2(x.GetEndPoint(0).Y-x.GetEndPoint(1).Y,x.GetEndPoint(0).X-x.GetEndPoint(1).X)-math.pi/2,4)):
		crop.append(max(g,key=lambda x: x.Length))
		
	for c in crop:
		p=c.GetEndPoint(0)+1*DB.XYZ.BasisZ.CrossProduct(c.Direction)
		q=c.GetEndPoint(1)+1*DB.XYZ.BasisZ.CrossProduct(c.Direction)
		curveloop.append(DB.Line.CreateBound(p,q))
		

	for curve in curveloop:

		location_pts.append(curve.Evaluate(0.5,True))
		curves.append(curve)
		start_pt=curve.GetEndPoint(0)
		end_pt=curve.GetEndPoint(1)
		
		angles.append(math.atan2(start_pt.Y-end_pt.Y,start_pt.X-end_pt.X)-anglecorrection)
		

	for c in crop:
		sp=c.GetEndPoint(0)
		ep=c.GetEndPoint(1)

		elev_crop=DB.CurveLoop()
		elev_crop.Append(DB.Line.CreateBound(sp,ep))
		elev_crop.Append(DB.Line.CreateBound(ep,DB.XYZ(ep.X,ep.Y,ep.Z+rheight)))
		elev_crop.Append(DB.Line.CreateBound(DB.XYZ(ep.X,ep.Y,ep.Z+rheight),DB.XYZ(sp.X,sp.Y,sp.Z+rheight)))
		elev_crop.Append(DB.Line.CreateBound(DB.XYZ(sp.X,sp.Y,sp.Z+rheight),sp))

		elev_crops.append(elev_crop)

	results = unique(angles,location_pts,elev_crops)	
		
	t=DB.Transaction(doc,"Elevation By Room")
	t.Start()

	for location_pt,angle,crop in zip(results[1],results[0],results[2]):

		marker=DB.ElevationMarker.CreateElevationMarker(doc,res_elev.Id,location_pt,20)
		elevation=marker.CreateElevation(doc,doc.ActiveView.Id,0)
		newlist=results[1][::-1]

		if 170 < abs(round(math.degrees(angle))) < 190 :
			DB.ElementTransformUtils.RotateElement(doc,marker.Id,DB.Line.CreateBound(location_pt,location_pt+DB.XYZ.BasisZ),angle/2)
			DB.ElementTransformUtils.RotateElement(doc,marker.Id,DB.Line.CreateBound(location_pt,location_pt+DB.XYZ.BasisZ),angle/2)
			
		else:
			DB.ElementTransformUtils.RotateElement(doc,marker.Id,DB.Line.CreateBound(location_pt,location_pt+DB.XYZ.BasisZ),angle)
			
		elevation.CropBoxActive=True
		try:
			elevation.GetCropRegionShapeManager().SetCropShape(crop)

			outline=db.Collector(view=elevation, of_category='OST_Viewers').get_first(wrapped=False)
			settings=DB.OverrideGraphicSettings()
			settings.SetProjectionLineWeight(6)

			elevation.SetElementOverrides(outline.Id,settings)
			active_view_name=doc.ActiveView.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString()
			elevation.Name=active_view_name[0:6]+"IE"+active_view_name[8:]+"-"+room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()+"-"+string.letters[newlist.index(location_pt)].upper()
			elevation.Scale = 50

			elevation.LookupParameter("IPA View Group").Set("07 - Building Finishes")
			elevation.LookupParameter("IPA View Sub Group").Set("200")
			elevation.LookupParameter("Phasing").Set(doc.ActiveView.LookupParameter("Phasing").AsString())

			elevations.append(elevation)

		except:
			pass	
		
	t.Commit()

	return elevations

tg=DB.TransactionGroup(doc,"Elevations By Room")
tg.Start()
if res_elev != None and res_fp != None:
	result = map(lambda x: CurveLoop(x),rooms)
tg.Assimilate()



