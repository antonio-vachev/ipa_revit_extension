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

walls=[]

el_ref= revit.uidoc.Selection.PickObjects(UI.Selection.ObjectType.Element,SelectionFilter("Basic"))

for er in el_ref:
    walls.append(doc.GetElement(er.ElementId))
    
t=DB.Transaction(doc,"Wall Disallow Join")
t.Start()
for w in walls:
	DB.WallUtils.DisallowWallJoinAtEnd(w,0)
	DB.WallUtils.DisallowWallJoinAtEnd(w,1)
t.Commit()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)