
import rpw
import Autodesk
from rpw import revit, db, ui, DB, UI
from pyrevit import forms

from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory
import logexporter

doc = revit.doc

#creating empty lists for the door elements and door element locations (left and right)

lwindowpts=[]
rwindowpts=[]
lwindows=[]
rwindows=[]

if len(db.Collector(of_category="OST_WindowTags", is_type=True,where=lambda x: "IPA-Window Tag-Right" == x.FamilyName+"-"+x.name ).get_elements()) == 0:
    forms.alert("Default Right Window Tag Not Found!")
    exit()

elif len(db.Collector(of_category="OST_WindowTags", is_type=True,where=lambda x: "IPA-Window Tag-Left" == x.FamilyName+"-"+x.name ).get_elements()) == 0:
    forms.alert("Default Left Window Tag Not Found!")
    exit()
    
elif len(db.Collector(of_category="OST_WindowTags", is_type=True,where=lambda x: "IPA-Window Tag Size Only-Left" == x.FamilyName+"-"+x.name ).get_elements()) == 0:
    forms.alert("Default Left Schematic Window Tag Not Found!")
    exit()
    
elif len(db.Collector(of_category="OST_WindowTags", is_type=True,where=lambda x: "IPA-Window Tag Size Only-Right" == x.FamilyName+"-"+x.name ).get_elements()) == 0:
    forms.alert("Default Right Schematic Window Tag Not Found!")
    exit()
    
windowtags = db.Collector(of_category="OST_WindowTags", is_type = True)
windowtagslist = []
windowtagsnames = []

for tagType in windowtags:
    if tagType.FamilyName == "IPA-Window Tag Size Only" or tagType.FamilyName == "IPA-Window Tag":
        if tagType.FamilyName not in windowtagsnames:
            windowtagslist.append(tagType)
            windowtagsnames.append(tagType.FamilyName)
            
taginput = forms.CommandSwitchWindow.show(
    ["IPA-Window Tag", "IPA-Window Tag Size Only"],
     message="Choose a tag type to use:"
	)
    
if taginput == windowtagsnames[0]:
    tagType = windowtagslist[0]
else:
    tagType = windowtagslist[1]

#collecting all windows in the active view (except Curtain Wall windows) SLOW COLLECTOR!

windows=db.Collector(view=revit.active_view,of_category='OST_Windows',where=lambda x: "Curtain" != x.Host.WallType.Kind.ToString()).get_elements(wrapped=False)

#filtering windows and door locations by orientation

for i in windows:
	if round(i.FacingOrientation.X) >0 and round(i.FacingOrientation.X) <=1 and round(i.FacingOrientation.Y)<=1 and round(i.FacingOrientation.Y)>=-1:
		lwindowpts.append(i.Location.Point+i.FacingOrientation*2.7)
		lwindows.append(i)

	elif round(i.FacingOrientation.X) == 0 and round(i.FacingOrientation.Y) == 1:
		lwindowpts.append(i.Location.Point+i.FacingOrientation*2.7)
		lwindows.append(i)		 

	else:
		rwindowpts.append(i.Location.Point+i.FacingOrientation*2.7)
		rwindows.append(i)

def CreateTag(element, location, Ttype, orientation):
	doc=revit.doc
	view=revit.active_view
	reference = DB.Reference(element)
	tagFinalType = db.Collector(of_category="OST_WindowTags", is_type=True,where=lambda x: Ttype.FamilyName + "-" + orientation == x.FamilyName+"-"+x.name ).get_elements()[0].Id
	tag = DB.IndependentTag.Create(doc, view.Id, reference, False, DB.TagMode.TM_ADDBY_CATEGORY, DB.TagOrientation.Horizontal, location)
	tag.ChangeTypeId(tagFinalType)
    

#creating tags

t=DB.Transaction(doc,'CreateTags')
t.Start()

for d, dl in zip(lwindows,lwindowpts):
	CreateTag(d, dl, tagType, "Right")

for d, dl in zip(rwindows,rwindowpts):
	CreateTag(d, dl, tagType, "Left")

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)