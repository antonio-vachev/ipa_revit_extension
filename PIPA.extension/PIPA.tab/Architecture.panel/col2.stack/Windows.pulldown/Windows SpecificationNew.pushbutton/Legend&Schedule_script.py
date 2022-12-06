# -*- coding: utf-8 -*-

from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import *

from collections import OrderedDict 

from pyrevit import revit, DB, UI
from rpw import db

import sys
import logexporter

doc = __revit__.ActiveUIDocument.Document


# check for windows from different families with identical Type Mark parameter values
allWindows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()
allWindowFamilies, uniqueWindowFamilies, uniqueWindowFamilyNames, allWindowTypeMarks = [], [], [], []

allWindowTypes = []
for window in allWindows:
    if window.Symbol not in allWindowTypes:
        allWindowTypes.append(window.Symbol)

for windowType in allWindowTypes:
    allWindowFamilies.append(windowType.Family)

for windowFamily in allWindowFamilies:
    if windowFamily.Name not in uniqueWindowFamilyNames:
        uniqueWindowFamilyNames.append(windowFamily.Name)
        uniqueWindowFamilies.append(windowFamily)
        
for uniqueFamily in uniqueWindowFamilies:
    templist = []
    
    for id in uniqueFamily.GetFamilySymbolIds():
        templist.append(doc.GetElement(id).LookupParameter('Type Mark').AsString())
        
    templist = list(dict.fromkeys(templist))
    
    for uniqueTypeMark in templist:
        allWindowTypeMarks.append(uniqueTypeMark)
  
if len(allWindowTypeMarks) != len(dict.fromkeys(allWindowTypeMarks)):
    TaskDialog.Show("Warning", "Different windows with identical Type Marks were found in the project. Please revise them and try again. All Type Marks for elements from different families must be unique!")
    sys.exit()


# get all schedules, check if the default legend and Schedule are loaded and check if all windows have different Type Marks
schedule = db.Collector(of_class = 'View',where=lambda x: x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString() == "Window Schedule Type WA" ).get_first(wrapped=False)

if schedule == None:
    TaskDialog.Show("Warning", "Please load the default Window Schedule Type WA view and try again!")
    sys.exit()

legend = db.Collector(of_class='View',where=lambda x: x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString() == "Window Type WA" ).get_first(wrapped=False)

if legend == None:
    TaskDialog.Show("Warning", "Please load the default Window Type WA legend and try again!")
    sys.exit()


# get a collection of all the door instances, available in the project
windowInput = DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()


# check if any of the windows already have legend and schedules associated to their type. Remove them from the list if any
allWindowSchedules = db.Collector(of_class="View",where=lambda x: "Window Schedule Type" in x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString())

windowDuplicates = []

for scheduleView in allWindowSchedules:
    name = scheduleView.Name
    
    if name[-3] == " ":
        typeName = scheduleView.Name[len(scheduleView.Name) - 2:]
    elif name[-4] == " ":
        typeName = scheduleView.Name[len(scheduleView.Name) - 3:]
        
    for window in windowInput:
        if typeName == window.Symbol.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).AsString() and typeName != "WA":
            windowDuplicates.append(window)
            
uniqueNewWindows = [x for x in windowInput if x not in windowDuplicates]


# check window for copyrights data
finalWindowsList, nonIpaWindowNamesList = [], []

for window in uniqueNewWindows:
    if window.Symbol.LookupParameter('Family Copyright ©'):
        if window.Symbol.LookupParameter('Family Copyright ©').AsString() == 'Ivo Petrov Architects':
            finalWindowsList.append(window)
        else:
            nonIpaWindowNamesList.append(window.Symbol.FamilyName)
    else:
        nonIpaWindowNamesList.append(window.Symbol.FamilyName)


# create definitions for extracting the elements and family types
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
    
    
# create new schedules and legends and update WA
filter=schedule.Definition.GetFilter(0)

t=DB.Transaction(doc,"Duplicate Schedules&Legends")
t.Start()

for ut,ft in unique_types(finalWindowsList):

    new_schedule=schedule.Duplicate(DB.ViewDuplicateOption.Duplicate)
    filter.SetValue(ut)
    doc.GetElement(new_schedule).Definition.SetFilter(0,filter)
    table_data=doc.GetElement(new_schedule).GetTableData().GetSectionData(DB.SectionType.Header).SetCellText(0,0,'Спецификация прозорци - Tип '+ut)
    doc.GetElement(new_schedule).Name="Window Schedule Type "+ ut
	
    new_legend=legend.Duplicate(DB.ViewDuplicateOption.WithDetailing)
    doc.GetElement(new_legend).Name="Window Type "+ ut
    legend_component=db.Collector(view=doc.GetElement(new_legend), of_category='OST_LegendComponents')
    legend_component[0].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)
    legend_component[1].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)
    legend_component[2].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)

for ut,ft in standard_type(finalWindowsList):

    legend_component=db.Collector(view=legend, of_category='OST_LegendComponents')
    legend_component[0].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)
    legend_component[1].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)
    legend_component[2].get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)

t.Commit()


# Display reports after completion
if len(finalWindowsList) != 1:
    reportMsg = str(len(finalWindowsList) - 1) + " new Legends and schedules were created successfully! Enjoy ;)"
elif len(uniqueNewWindows) == 1:
    reportMsg = "<Window Schedule Type WA> and <Window Type WA> schedule and legend views were updated. No new Type Marks were found in the project! "

if nonIpaWindowNamesList != []:
    reportMsg += '\n\nThe following window families were found in the project, not being subject to IPA copyrights. Please contact the BIM team for evaluation of these families: ' + str(nonIpaWindowNamesList)
    
TaskDialog.Show("Report", reportMsg)


# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)