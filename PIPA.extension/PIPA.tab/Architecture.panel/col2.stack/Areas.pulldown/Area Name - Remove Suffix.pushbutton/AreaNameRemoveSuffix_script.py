# !/usr/bin/python
# coding=utf-8

# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementMulticategoryFilter, Transaction

# Import from Custom IPA Lib
import logexporter

# Import from pyRevit
from pyrevit import forms

# Define short variable for current document
doc = __revit__.ActiveUIDocument.Document

area_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Areas).WhereElementIsNotElementType()

t = Transaction(doc, "Remove suffix from Area Names")

t.Start()

for area in area_collector:
    name = area.LookupParameter("Name").AsString()
    newname = ""
    index = 0
    if len(name) >= 3 and name[-3] == " ":
        try:
            casttest = int(name[-2])
            index = len(name) - 3
            newname = name[0:index]
            area.LookupParameter("Name").Set(newname)
        except:
            pass
    elif len(name) >= 4 and name[-4] == " ":
        try:
            casttest = int(name[-3])
            index = len(name) - 4
            newname = name[0:index]
            area.LookupParameter("Name").Set(newname)
        except:
            pass
    elif len(name) >= 5 and name[-5] == " ":
        try:
            casttest = int(name[-4])
            index = len(name) - 5
            newname = name[0:index]
            area.LookupParameter("Name").Set(newname)
        except:
            pass

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)