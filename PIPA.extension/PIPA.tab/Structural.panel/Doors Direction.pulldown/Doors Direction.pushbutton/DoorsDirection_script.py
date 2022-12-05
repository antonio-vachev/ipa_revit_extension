# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

import logexporter
from rpw import revit, db, ui, DB, UI
doc = revit.doc

phase = doc.GetElement(doc.ActiveView.get_Parameter(DB.BuiltInParameter.VIEW_PHASE).AsElementId())

single_doors = db.Collector(of_category='OST_Doors',is_not_type=True,where=lambda x: 'Single' in x.Symbol.FamilyName ).get_elements(wrapped=False)
double_doors = db.Collector(of_category='OST_Doors',is_not_type=True,where=lambda x: 'Double' in x.Symbol.FamilyName and 'Uneven' not in x.Symbol.FamilyName).get_elements(wrapped=False)
double_uneven_doors = db.Collector(of_category='OST_Doors',is_not_type=True,where=lambda x: 'Double' and 'Uneven' in x.Symbol.FamilyName ).get_elements(wrapped=False)

def SetElmOrientation(elm_list,str_left='Лява',str_right='Дясна'):
	right, left, lhr, rhr = [], [], [], []
	for i in elm_list:
		try:
			to_room = i.ToRoom[phase]
			if to_room is not None:
				if not i.FacingFlipped:
					if i.HandFlipped:
						right.append(i)
					else:
						left.append(i)
				else:
					if i.HandFlipped:
						left.append(i)
					else:
						right.append(i)
			else:
				if i.FacingFlipped:
					if i.HandFlipped:
						left.append(i)
					else:
						right.append(i)
				else:
					if i.HandFlipped:
						right.append(i)
					else:
						left.append(i)
		except:
				pass

	for door in left:
		door.LookupParameter('D Instance Swing Direction').Set(str_left)
	for door in right:
		door.LookupParameter('D Instance Swing Direction').Set(str_right)
	

t=DB.Transaction(doc,'Door Swing Direction')
t.Start()

SetElmOrientation(single_doors)
SetElmOrientation(double_uneven_doors,'Двукрила. Дясно активно крило','Двукрила. Ляво активно крило')
SetElmOrientation(double_doors,'Двукрила','Двукрила')

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)