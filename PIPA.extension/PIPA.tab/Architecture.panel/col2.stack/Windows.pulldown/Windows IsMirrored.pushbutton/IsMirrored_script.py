
# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, Color, OverrideGraphicSettings
import logexporter

# Set a short variable for the active document
doc = __revit__.ActiveUIDocument.Document

# Collect all windows in current document, as well as those in current view
windows_in_view = FilteredElementCollector(doc, doc.ActiveView.Id).OfCategory(BuiltInCategory.OST_Windows).WhereElementIsNotElementType().ToElements()

# Define color and graphic override settings
color = Color(255, 0, 0)
ogs = OverrideGraphicSettings().SetSurfaceBackgroundPatternColor(color).SetProjectionLineColor(color)
clearogs = OverrideGraphicSettings()

# Define and open transaction
t = Transaction(doc, 'IsMirrored check')
t.Start()
		
# Check for mirror and override graphics for windows in active view
for window in windows_in_view:
	doc.ActiveView.SetElementOverrides((window.Id), clearogs)
	if window.Mirrored == True:
			doc.ActiveView.SetElementOverrides((window.Id), ogs)

# Close transaction and end function
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)