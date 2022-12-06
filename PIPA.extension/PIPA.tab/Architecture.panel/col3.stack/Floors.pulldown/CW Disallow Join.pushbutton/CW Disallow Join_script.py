#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit, DB, UI
import logexporter

doc=revit.doc

#Defining Selection Filter class

class SelectionFilter(UI.Selection.ISelectionFilter):
	def __init__(self, nom_type):
		self.nom_type = nom_type
	def AllowElement(self, e):		
		if e.WallType.Kind.ToString() == self.nom_type:
			return True
		else:
			return False
	def AllowReference(self, ref, point):
		return true

#User selection filtered for curtain walls only
allwalls=[]
cwalls=[]

el_ref=[]

try:
	el_ref= revit.uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element,SelectionFilter("Curtain"))
except:
	pass

if len(el_ref)>0:
	for er in el_ref:
		cwalls.append(er.ElementId)
		allwalls.append(doc.GetElement(er.ElementId))

	panels=DB.FilteredElementCollector(doc).OfCategory(DB.BuiltInCategory.OST_CurtainWallPanels).OfClass(DB.Wall).ToElements()

	for p in panels:
		if p.StackedWallOwnerId in cwalls:
			allwalls.append(p)


t=DB.Transaction(doc,"Disallow Join")
t.Start()

if len(el_ref)>0:
	for w in allwalls:
		DB.WallUtils.DisallowWallJoinAtEnd(w,0)
		DB.WallUtils.DisallowWallJoinAtEnd(w,1)
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)


