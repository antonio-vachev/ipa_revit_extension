
# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, Color, OverrideGraphicSettings
from pyrevit import forms
import logexporter

# Set a short variable for the active document
doc = __revit__.ActiveUIDocument.Document

# Collect all windows in current document, as well as those in current view
rooms_in_view = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

length = forms.ask_for_string(
	    default="2",
	    prompt='Enter the number of symbols to remain at the end of the string',
	    title='Number of Symbols'
	    )

x = int(length)

# Define and open transaction
t = Transaction(doc, 'Clean Rooms Prefixes')
t.Start()
		
# Check for mirror and override graphics for windows in active view
for room in rooms_in_view:
    newnumb = room.Number[-x:]
    room.Number = newnumb

# Close transaction and end function
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)