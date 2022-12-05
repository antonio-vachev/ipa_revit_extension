
# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, Transaction, ElementMulticategoryFilter, Reference
from System.Collections.Generic import List
import logexporter

# Set a short variable for the active document
doc = __revit__.ActiveUIDocument.Document

# Filter Multiple categories
category_list = [BuiltInCategory.OST_Walls, BuiltInCategory.OST_Floors, BuiltInCategory.OST_Ceilings, BuiltInCategory.OST_Roofs]
category_filter_list = List[BuiltInCategory](category_list)
category_filter = ElementMulticategoryFilter(category_filter_list)
categories_collector = FilteredElementCollector(doc).WherePasses(category_filter).WhereElementIsNotElementType().ToElements()

t = Transaction(doc, 'Remove all paint from walls, floors, ceilings and roofs')

t.Start()

for elem in categories_collector:

	# get geometry object (solid)
	geoelem = elem.GetGeometryObjectFromReference(Reference(elem))
	
	# solid to geometry object
	geoobj = geoelem.GetEnumerator()
	
	# loop geometry object
	for obj in geoobj:
	
		# collect faces from geometry object
		for f in obj.Faces:
		
			# get each face
			doc.RemovePaint(elem.Id,f)

t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)