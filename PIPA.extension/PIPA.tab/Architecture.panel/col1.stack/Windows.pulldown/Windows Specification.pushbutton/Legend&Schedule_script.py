# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit, DB, UI
from rpw import db
import logexporter

doc=revit.doc

schedule=db.Collector(of_class='View',where=lambda x: x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString() == "Window Schedule Type WA" ).get_first(wrapped=False)
legend = db.Collector(of_class='View',where=lambda x: x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString() == "Window Type WA" ).get_first(wrapped=False)

filter=schedule.Definition.GetFilter(0)

output = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

def unique_types(elm_list):
	unique=[]
	fam_types=[]
	for l in elm_list:
		if l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() not in unique and l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() != "WA":
			unique.append(l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString())
			fam_types.append(l.Symbol.Id)
	return zip(unique,fam_types)


def standard_type(elm_list):
	unique=[]
	fam_types=[]
	for l in elm_list:
		if l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() not in unique and l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() == "WA":
			unique.append(l.Symbol.get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString())
			fam_types.append(l.Symbol.Id)
	return zip(unique,fam_types)


t=DB.Transaction(doc,"Duplicate Schedules&Legends")
t.Start()

for ut,ft in unique_types(output):

	new_schedule=schedule.Duplicate(DB.ViewDuplicateOption.Duplicate)
	filter.SetValue(ut)
	doc.GetElement(new_schedule).Definition.SetFilter(0,filter)

	table_data=doc.GetElement(new_schedule).GetTableData() \
											.GetSectionData(DB.SectionType.Header) \
											.SetCellText(0,0,'Спецификация прозорци - Tип '+ut)

	doc.GetElement(new_schedule).Name="Window Schedule Type "+ ut

	new_legend=legend.Duplicate(DB.ViewDuplicateOption.WithDetailing)
	doc.GetElement(new_legend).Name="Window Type "+ ut

	legend_component=db.Collector(view=doc.GetElement(new_legend), of_category='OST_LegendComponents').get_first(wrapped=False) \
																										.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)

	detail_component=db.Collector(view=doc.GetElement(new_legend), of_category='OST_DetailComponents').get_first(wrapped=False)
	detail_type_name=doc.GetElement(ft).get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()
	detail_component_type=db.Collector(of_category='OST_DetailComponents',is_type=True, where=lambda x: x.FamilyName == detail_type_name ).get_first(wrapped=False)
	
	try:
		detail_component.Symbol=detail_component_type		
	except:
		pass


for ut,ft in standard_type(output):

	legend_component=db.Collector(view=legend, of_category='OST_LegendComponents').get_first(wrapped=False) \
																										.get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)

	detail_component=db.Collector(view=legend, of_category='OST_DetailComponents').get_first(wrapped=False)
	detail_type_name=doc.GetElement(ft).get_Parameter(DB.BuiltInParameter.ALL_MODEL_TYPE_COMMENTS).AsString()
	detail_component_type=db.Collector(of_category='OST_DetailComponents',is_type=True, where=lambda x: x.FamilyName == detail_type_name ).get_first(wrapped=False)
	
	try:
		detail_component.Symbol=detail_component_type		
	except:
		pass

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)