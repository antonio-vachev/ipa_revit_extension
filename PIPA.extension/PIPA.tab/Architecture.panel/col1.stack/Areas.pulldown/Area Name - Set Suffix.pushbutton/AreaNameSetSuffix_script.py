# !/usr/bin/python
# coding=utf-8

# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementMulticategoryFilter, Transaction

# Import from pyRevit
from pyrevit import forms

# Define short variable for current document
doc = __revit__.ActiveUIDocument.Document

area_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Areas).WhereElementIsNotElementType()

t = Transaction(doc, "Set suffix for Area Names")
i = 0

t.Start()

for area in area_collector:
    numb = area.LookupParameter("Number").AsString()
    name = area.LookupParameter("Name").AsString()
    newName = ""
    index = 0
    length = 0
    if len(numb) >= 3 and numb[-3] == "-":
        index = len(numb) - 2
        length = len(numb)
        newName = name + " " + numb[index:length]
        area.LookupParameter("Name").Set(newName)
    elif len(numb) >= 4 and numb[-4] == "-":
        index = len(numb) - 3
        length = len(numb)
        newName = name + " " + numb[index:length]
        area.LookupParameter("Name").Set(newName)
    elif len(numb) >= 5 and numb[-5] == "-":
        index = len(numb) - 4
        length = len(numb)
        newName = name + " " + numb[index:length]
        area.LookupParameter("Name").Set(newName)
    else:
        i += 1

t.Commit()

if (i != 0):
    forms.alert("The program detected <" + str(i) + "> Areas, whose Number does not match the required format. Please, check your Areas. If needed, press the 'Area Name - Remove Suffix' button, fix Area Numbers and try again.")