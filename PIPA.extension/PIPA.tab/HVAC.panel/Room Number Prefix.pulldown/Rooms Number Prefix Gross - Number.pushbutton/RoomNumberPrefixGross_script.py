# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

import rpw
import System
from System.Collections.Generic import *

from pyrevit import revit, DB
from pyrevit import forms
from rpw import db
import logexporter

doc = revit.doc

areas=db.Collector(of_category='OST_Areas',where=lambda x: x.get_Parameter(DB.BuiltInParameter.AREA_TYPE).AsValueString() == "Gross Building Area").get_elements(wrapped=False) 

allrooms=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Rooms).ToElements()

rooms=[]

for r in allrooms:
	if r.Area > 0:
		rooms.append(r)

def IsRoomInArea(area,room):

	def RoomLocationTransform(room):
		return DB.Line.CreateBound(room.Location.Point,DB.XYZ(room.Location.Point.X+1000,room.Location.Point.Y,room.Location.Point.Z))

	def AreaBoundary(area):
		opt=DB.SpatialElementBoundaryOptions()
		curveloop=[]
		for sengments in area.GetBoundarySegments(opt):
			for s in sengments:
				curveloop.append(s.GetCurve())
		return curveloop

	result=[]
	for ab in AreaBoundary(area):
		result.append(ab.Intersect(RoomLocationTransform(room)))

	if result.count(DB.SetComparisonResult.Overlap) % 2==0:
		return False
	else:
		return True

t=DB.Transaction(doc,"Rooms Department")
t.Start()

for room in rooms:
	if room.Level.Id == doc.ActiveView.GenLevel.Id:
		for area in areas:
			if IsRoomInArea(area,room) == True:
				room.get_Parameter(DB.BuiltInParameter.ROOM_DEPARTMENT).Set(area.LookupParameter("Number").AsString())
				if room.get_Parameter(DB.BuiltInParameter.ROOM_DEPARTMENT).AsString() not in room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString():
					room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).Set(area.LookupParameter("Number").AsString()+"-"+room.get_Parameter(DB.BuiltInParameter.ROOM_NUMBER).AsString())
				else:
					pass

			
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)