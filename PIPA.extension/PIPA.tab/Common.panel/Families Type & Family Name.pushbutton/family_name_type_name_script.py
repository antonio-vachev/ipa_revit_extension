
# Import from Autodesk API
from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementMulticategoryFilter, Transaction
from System.Collections.Generic import List
import logexporter

# Define short variable for current document
doc = __revit__.ActiveUIDocument.Document

# Filter multiple categories, reffering to non system families
category_list = [BuiltInCategory.OST_PlumbingFixtures, BuiltInCategory.OST_Furniture, BuiltInCategory.OST_Windows, BuiltInCategory.OST_Doors]
filter_list = List[BuiltInCategory](category_list)
filter = ElementMulticategoryFilter(filter_list)
category_collector = FilteredElementCollector(doc).WherePasses(filter).WhereElementIsNotElementType().ToElements()

# Filter Multiple categories, reffering to system families
system_list = [BuiltInCategory.OST_Walls, BuiltInCategory.OST_Ceilings, BuiltInCategory.OST_Floors, BuiltInCategory.OST_Roofs, BuiltInCategory.OST_Walls, BuiltInCategory.OST_RvtLinks]
system_filter_list = List[BuiltInCategory](system_list)
system_filter = ElementMulticategoryFilter(system_filter_list)
system_collector = FilteredElementCollector(doc).WherePasses(system_filter).WhereElementIsNotElementType().ToElements()

# Filter Revit Links
links_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_RvtLinks).WhereElementIsNotElementType().ToElements()

# Define and open transaction
t = Transaction(doc, "Update Family/Type Name")

t.Start()

# Starting with non system families
for i in category_collector:

	# Set duplicate for the TypeName
	TypeName = i.Name
	TypeNameDuplicate = i.LookupParameter('TypeNameDuplicate')
	if TypeNameDuplicate:
		TypeNameDuplicate.Set(TypeName)

	# Set duplicate for the FamilyName
	type_id = i.GetTypeId()
	element_type = doc.GetElement(type_id)
	family = element_type.Family
	name = family.Name
	FamilyNameDuplicate = i.LookupParameter('FamilyNameDuplicate')
	if FamilyNameDuplicate:
		FamilyNameDuplicate.Set(name)
		
# Duplicates for the system families
for s in system_collector:
	SystemTypeName = s.Name
	TypeNameDuplicate = s.LookupParameter('TypeNameDuplicate')
	if TypeNameDuplicate:
		TypeNameDuplicate.Set(SystemTypeName)
        
# Duplicates for linked files
for link in links_collector:
	link_filename = link.Name.split(' : ')[0]
	LinkFileName = link.LookupParameter('LinkFileName')
	if LinkFileName:
		LinkFileName.Set(link_filename)
	
	link_name = link.Name.split(' : ')[1]
	LinkName = link.LookupParameter('LinkName')
	if LinkName:
		LinkName.Set(link_name)
	
	link_site = link.Name.split(' : ')[2]
	LinkSite = link.LookupParameter('LinkSite')
	if LinkSite:
		LinkSite.Set(link_site)

# Close transaction
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)