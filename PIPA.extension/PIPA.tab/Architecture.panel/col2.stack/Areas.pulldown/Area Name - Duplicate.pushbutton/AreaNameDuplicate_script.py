# !/usr/bin/python
# coding=utf-8

# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementMulticategoryFilter, Transaction
import logexporter

# Define short variable for current document
doc = __revit__.ActiveUIDocument.Document

area_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Areas).WhereElementIsNotElementType()

t = Transaction(doc, "Duplicate are names")

t.Start()

for area in area_collector:
    AreaTrueName = area.LookupParameter("Name").AsString()
    if ("Склад" in AreaTrueName):
        AreaTrueName = "Склад"
    area.LookupParameter("AreaNameDuplicate").Set(AreaTrueName)

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)