#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit, DB, UI,forms
import logexporter

doc=revit.doc

rooms=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()

phases=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Phases).ToElements()

params=["Floor Finish EN",
		"Wall Finish EN",
		"Ceiling Finish EN",
		"Name EN",
		"Required Overpressure",
		"Required Air Exchange Rate",
		"Fire Hazard Class",
		"Fire Hazard Category",
		"Secured Evacuation Path"
		]

BuiltInParams=[DB.BuiltInParameter.ROOM_FINISH_FLOOR,
		DB.BuiltInParameter.ROOM_FINISH_WALL,
		DB.BuiltInParameter.ROOM_FINISH_CEILING,
		DB.BuiltInParameter.ROOM_DEPARTMENT,
		DB.BuiltInParameter.ROOM_UPPER_OFFSET,
		]


class ElmName(forms.TemplateListItem):
    @property
    def name(self):
        return self.Name

def SetRoomParameters(elm,params,source_room):
	for param in params:
		if source_room.LookupParameter(param) != None and source_room.LookupParameter(param).StorageType == DB.StorageType.String and source_room.LookupParameter(param).HasValue == True:
			elm.LookupParameter(param).Set(source_room.LookupParameter(param).AsString())
		elif source_room.LookupParameter(param) != None and source_room.LookupParameter(param).StorageType == DB.StorageType.Integer and source_room.LookupParameter(param).HasValue == True:
			elm.LookupParameter(param).Set(source_room.LookupParameter(param).AsInteger())

def SetRoomBuiltInParameters(elm,params,source_room):
	for param in params:
		if source_room.get_Parameter(param) != None and source_room.get_Parameter(param).StorageType == DB.StorageType.String and source_room.get_Parameter(param).HasValue == True:
			elm.get_Parameter(param).Set(source_room.get_Parameter(param).AsString())
		elif source_room.get_Parameter(param) != None and source_room.get_Parameter(param).StorageType == DB.StorageType.Integer and source_room.get_Parameter(param).HasValue == True:
			elm.get_Parameter(param).Set(source_room.get_Parameter(param).AsInteger())
		elif source_room.get_Parameter(param) != None and source_room.get_Parameter(param).StorageType == DB.StorageType.Double and source_room.get_Parameter(param).HasValue == True:
			elm.get_Parameter(param).Set(source_room.get_Parameter(param).AsDouble())

opts=list(map(lambda x: ElmName(x), phases))  

phase = forms.SelectFromList.show(opts,
								title='Select Phase To Transfer From',
                                multiselect=False,
                                button_name='Transfer from Phase')

with revit.Transaction("Transfer Rooms"):
	if phase != None:
		phase_element=doc.GetElement(doc.ActiveView.get_Parameter(DB.BuiltInParameter.VIEW_PHASE).AsElementId())
		for r in rooms:
			if r.Area > 0 and r.get_Parameter(DB.BuiltInParameter.ROOM_PHASE).AsValueString() == phase.Name:
				if doc.GetRoomAtPoint(r.Location.Point,phase_element) == None:

					#Create new room
					newr=doc.Create.NewRoom(r.Level,DB.UV(r.Location.Point.X,r.Location.Point.Y)) 
					#Create new room tag
					doc.Create.NewRoomTag(DB.LinkElementId(newr.Id),DB.UV(r.Location.Point.X,r.Location.Point.Y),doc.ActiveView.Id)
					
					#Set new room built-in parameter values
					newr.Name = r.get_Parameter(DB.BuiltInParameter.ROOM_NAME).AsString()
					newr.Number= r.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString()
					SetRoomBuiltInParameters(newr,BuiltInParams,r)

					#Set new room user-defined parameters
					SetRoomParameters(newr,params,r)
					
# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)