# -*- coding: utf-8 -*-

from Autodesk.Revit.UI import TaskDialog

from rpw import revit, db, ui, DB, UI
from pyrevit import forms
import logexporter

doc = revit.doc


#creating empty lists for the door elements and door element locations (left and right)
ldoorpts=[]
rdoorpts=[]
ldoors=[]
rdoors=[]
doors = []


#collecting all doors in the active view (except Curtain Wall Doors)
initialDoors = db.Collector(view=revit.active_view,of_category='OST_Doors').get_elements(wrapped=False)

for door in initialDoors:
    if 'Wall' in str(door.Host):
        if 'Curtain' not in door.Host.Name:
            doors.append(door)


# check doors for copyrights data
finalDoorsList, nonIpaDoorNamesList = [], []

for door in doors:
    if door.Symbol.LookupParameter('Family Copyright ©'):
        if door.Symbol.LookupParameter('Family Copyright ©').AsString() == 'Ivo Petrov Architects':
            finalDoorsList.append(door)
        else:
            nonIpaDoorNamesList.append(door.Symbol.FamilyName)
    else:
        nonIpaDoorNamesList.append(door.Symbol.FamilyName)


#filtering doors and door locations by orientation
for i in finalDoorsList:
	if round(i.FacingOrientation.X) >0 and round(i.FacingOrientation.X) <=1 and round(i.FacingOrientation.Y)<=1 and round(i.FacingOrientation.Y)>=-1:
		rdoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		rdoors.append(i)

	elif round(i.FacingOrientation.X) == 0 and round(i.FacingOrientation.Y) == 1:
		rdoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		rdoors.append(i)	

	else:
		ldoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		ldoors.append(i)

def CreateTag(element,location,tagtypename):
	reference = DB.Reference(element)
	tag = DB.IndependentTag.Create(doc, doc.ActiveView.Id, reference, False, DB.TagMode.TM_ADDBY_CATEGORY, DB.TagOrientation.Horizontal, location)
	tag.ChangeTypeId(db.Collector(of_category="OST_DoorTags", is_type=True,where=lambda x: tagtypename == x.FamilyName+"-"+x.name ).get_elements()[0].Id)


#creating tags
t=DB.Transaction(doc,'CreateTags')
t.Start()
if len(db.Collector(of_category="OST_DoorTags", is_type=True,where=lambda x: "IPA-Door Tag-Left" == x.FamilyName+"-"+x.name ).get_elements()) > 0:
	for d, dl in zip(ldoors,ldoorpts):
		CreateTag(d,dl,"IPA-Door Tag-Left")
else:
	forms.alert("Default Left Door Tag Not Found!")

if len(db.Collector(of_category="OST_DoorTags", is_type=True,where=lambda x: "IPA-Door Tag-Right" == x.FamilyName+"-"+x.name ).get_elements()) > 0:	
	for d, dl in zip(rdoors,rdoorpts):
		CreateTag(d,dl,"IPA-Door Tag-Right")
else:
	 forms.alert("Default Right Door Tag Not Found!")
t.Commit()


# Display report if any Non IPA Doors were found
if nonIpaDoorNamesList != []:
    TaskDialog.Show("Warning", "The following door families were found in the project, not being subject to IPA copyrights. Please contact the BIM team for evaluation of these families: " + str(nonIpaDoorNamesList))


# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)
