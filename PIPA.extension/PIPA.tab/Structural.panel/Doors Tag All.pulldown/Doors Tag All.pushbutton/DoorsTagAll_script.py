#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from rpw import revit, db, ui, DB, UI
from pyrevit import forms
import logexporter

doc = revit.doc
#creating empty lists for the door elements and door element locations (left and right)

ldoorpts=[]
rdoorpts=[]
ldoors=[]
rdoors=[]

#collecting all doors in the active view (except Curtain Wall Doors) SLOW COLLECTOR!

doors=db.Collector(view=revit.active_view,of_category='OST_Doors',where=lambda x: "Curtain" != x.Host.WallType.Kind.ToString()).get_elements(wrapped=False)

#filtering doors and door locations by orientation

for i in doors:
	if round(i.FacingOrientation.X) >0 and round(i.FacingOrientation.X) <=1 and round(i.FacingOrientation.Y)<=1 and round(i.FacingOrientation.Y)>=-1:
		ldoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		ldoors.append(i)

	elif round(i.FacingOrientation.X) == 0 and round(i.FacingOrientation.Y) == 1:
		ldoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		ldoors.append(i)	

	else:
		rdoorpts.append(i.Location.Point-i.FacingOrientation*1.2)
		rdoors.append(i)

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


# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)