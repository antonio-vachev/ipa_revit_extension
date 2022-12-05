# -*- coding: utf-8 -*-
# imports
import logexporter
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import TaskDialog


# get the document and the correct phase
doc = __revit__.ActiveUIDocument.Document
phase = doc.GetElement(doc.ActiveView.get_Parameter(BuiltInParameter.VIEW_PHASE).AsElementId())


# get doors from the project and define lists
allDoors = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType().ToElements()

allIPADoors, allNonIPADoors, allNonIPADoorNames= [], [], []

singleDoors, doubleDoors, doubleUnevenDoors, doubleSwingDoors, singleSwingDoors, double180PassiveDoors ,double180Doors, single180Doors = [], [], [], [], [], [], [], []
singleSlidingPocketDoors, singleSlidingDoors, doubleSlidingDoors, singleSlidingTwoPanelsDoors, singleSlidingThreePanelsEndDoors, singleSlidingThreePanelsMiddleDoors = [], [], [], [], [], []
foldingOneWayDoors, foldingTwoWayDoors, sectionalDoors, garageDoors, highSpeedDoors, fireCurtains, curtainDoors, fireSlidingDoors, revolvingDoors, unspecifiedDoors = [], [], [], [], [], [], [], [], [], []



# check doors for copyrights data
for door in allDoors:
    if door.Symbol.LookupParameter('Family Copyright ©'):
        if door.Symbol.LookupParameter('Family Copyright ©').AsString() == 'Ivo Petrov Architects':
            allIPADoors.append(door)
        else:
            allNonIPADoors.append(door)
            allNonIPADoorNames.append(door.Symbol.FamilyName)
    else:
        allNonIPADoors.append(door)
        allNonIPADoorNames.append(door.Symbol.FamilyName)
    

# Test 
for door in allIPADoors:
    doorName = door.Symbol.FamilyName
    
    if 'Single' in doorName and 'Sliding' not in doorName and '180' not in doorName and 'Swing' not in doorName and 'Curtain' not in doorName:
        singleDoors.append(door)
    elif 'Double' in doorName and 'Uneven' not in doorName and 'Passive' not in doorName and 'Swing' not in doorName and '180' not in doorName and 'Sliding' not in doorName and 'Curtain' not in doorName:
        doubleDoors.append(door)
    elif (('Double' in doorName and 'Uneven' in doorName) or ('Double' in doorName and 'Passive' in doorName)) and '180' not in doorName and 'Curtain' not in doorName:
        doubleUnevenDoors.append(door)
    elif 'Double' in doorName and 'Swing' in doorName and 'Curtain' not in doorName and '180' not in doorName:
        doubleSwingDoors.append(door)
    elif 'Single' in doorName and 'Swing' in doorName and 'Curtain' not in doorName and '180' not in doorName:
        singleSwingDoors.append(door)
    elif ('Double' in doorName and '180' in doorName and 'Passive' in doorName) or ('Double' in doorName and '180' in doorName and 'Uneven' in doorName):
        double180PassiveDoors.append(door)
    elif 'Double' in doorName and '180' in doorName and 'Passive' not in doorName:
        double180Doors.append(door)
    elif 'Single' in doorName and '180' in doorName:
        single180Doors.append(door)
    elif 'Single' in doorName and 'Sliding' in doorName and 'Pocket' in doorName:
        singleSlidingPocketDoors.append(door)
    elif 'Single' in doorName and 'Sliding' in doorName and 'Pocket' not in doorName and 'Two Panels' not in doorName and 'Three Panels' not in doorName and 'High Speed' not in doorName:
        singleSlidingDoors.append(door)
    elif 'Double' in doorName and 'Sliding' in doorName and 'High Speed' not in doorName:
        doubleSlidingDoors.append(door)
    elif 'Sliding' in doorName and 'Two Panels' in doorName:
        singleSlidingTwoPanelsDoors.append(door)
    elif 'Sliding' in doorName and 'Three Panels' in doorName and 'End Sliding' in doorName:
        singleSlidingThreePanelsEndDoors.append(door)
    elif 'Sliding' in doorName and 'Three Panels' in doorName and 'Middle Sliding' in doorName:
        singleSlidingThreePanelsMiddleDoors.append(door)
    elif 'Folding' in doorName and 'One' in doorName:
        foldingOneWayDoors.append(door)
    elif 'Folding' in doorName and 'Two' in doorName:
        foldingTwoWayDoors.append(door)
    elif 'Sectional' in doorName:
        sectionalDoors.append(door)
    elif 'Garage' in doorName:
        garageDoors.append(door)
    elif 'High Speed' in doorName:
        highSpeedDoors.append(door)
    elif 'Fire & Smoke' in doorName:
        fireCurtains.append(door)
    elif 'Curtain' in doorName and 'Fire & Smoke' not in doorName:
        curtainDoors.append(door)
    elif 'Fire Sliding' in doorName:
        fireSlidingDoors.append(door)
    elif 'Revolving' in doorName or 'Cylindrical' in doorName:
        revolvingDoors.append(door)
    else:
        unspecifiedDoors.append(door)


# definition for seting the doors' orientation
def SetElmOrientation(elm_list, str_right='Дясна', str_left='Лява'):
	right, left, lhr, rhr = [], [], [], []
	for i in elm_list:
		try:
			to_room = i.ToRoom[phase]
			if to_room is not None:
				if not i.FacingFlipped:
					if i.HandFlipped:
						left.append(i)
					else:
						right.append(i)
				else:
					if i.HandFlipped:
						right.append(i)
					else:
						left.append(i)
			else:
				if i.FacingFlipped:
					if i.HandFlipped:
						right.append(i)
					else:
						left.append(i)
				else:
					if i.HandFlipped:
						left.append(i)
					else:
						right.append(i)
		except:
				pass

	for door in left:
		door.LookupParameter('D Instance Swing Direction').Set(str_left)
	for door in right:
		door.LookupParameter('D Instance Swing Direction').Set(str_right)
	

# set doors orientation
t = Transaction(doc,'Door Swing Direction')
t.Start()

SetElmOrientation(singleDoors, 'Еднокрила, дясна', 'Еднокрила, лява')
SetElmOrientation(doubleUnevenDoors,'Двукрила. Дясно активно крило', 'Двукрила. Ляво активно крило')
SetElmOrientation(doubleDoors,'Двукрила','Двукрила')
SetElmOrientation(doubleSwingDoors,'Двукрила с две летящи крила', 'Двукрила с две летящи крила')
SetElmOrientation(singleSwingDoors,'Еднокрила, дясна, с летящо крило', 'Еднокрила, лява, с летящо крило')
SetElmOrientation(double180PassiveDoors,'Двукрила с отваряне на 180 градуса. Дясно активно крило', 'Двукрила с отваряне на 180 градуса. Ляво активно крило')
SetElmOrientation(double180Doors,'Двукрила с отваряне на 180 градуса', 'Двукрила с отваряне на 180 градуса')
SetElmOrientation(single180Doors,'Еднокрила с отваряне на 180 градуса, дясна', 'Еднокрила с отваряне на 180 градуса, лява')
SetElmOrientation(singleSlidingPocketDoors,'Еднокрила, плъзгаща, дясна, с прибиране в джоб', 'Еднокрила, плъзгаща, лява, с прибиране в джоб')
SetElmOrientation(singleSlidingDoors,'Еднокрила плъзгаща, дясна', 'Еднокрила плъзгаща, лява')
SetElmOrientation(doubleSlidingDoors,'Двукрила, плъзгаща', 'Двукрила, плъзгаща')
SetElmOrientation(singleSlidingTwoPanelsDoors,'Еднокрила плъзгаща, дясна, с един фиксиран панел', 'Еднокрила плъзгаща, лява, с един фиксиран панел')
SetElmOrientation(singleSlidingThreePanelsEndDoors,'Еднокрила плъзгаща, дясна, с два фиксирани и плъзгащ се краен панел', 'Еднокрила плъзгаща, лява, с два фиксирани и плъзгащ се краен панел')
SetElmOrientation(singleSlidingThreePanelsMiddleDoors,'Еднокрила плъзгаща, дясна, с два фиксирани и плъзгащ се среден панел', 'Еднокрила плъзгаща, лява, с два фиксирани и плъзгащ се среден панел')
SetElmOrientation(foldingOneWayDoors,'Плъзгаща врата на хармоника, дясна', 'Плъзгаща врата на хармоника, лява')
SetElmOrientation(foldingTwoWayDoors,'Плъзгаща врата на хармоника, с отваряне в две посоки', 'Плъзгаща врата на хармоника, с отваряне в две посоки')
SetElmOrientation(sectionalDoors,'Секционна врата', 'Секционна врата')
SetElmOrientation(garageDoors,'Гаражна врата', 'Гаражна врата')
SetElmOrientation(highSpeedDoors,'Бързо - затваряща се врата', 'Бързо - затваряща се врата')
SetElmOrientation(fireCurtains,'Димна завеса', 'Димна завеса')
SetElmOrientation(curtainDoors,'Врата във витрина или окачена фасада', 'Врата във витрина или окачена фасада')
SetElmOrientation(fireSlidingDoors,'Противопожарна, плъзгаща врата', 'Противопожарна, плъзгаща врата')
SetElmOrientation(revolvingDoors,'Въртяща се врата', 'Въртяща се врата')
SetElmOrientation(unspecifiedDoors,'Непознат тип врата, моля обърнете се към БИМ отдела', 'Непознат тип врата, моля обърнете се към БИМ отдела')

for wrongDoor in allNonIPADoors:
    wrongDoor.LookupParameter('D Instance Swing Direction').Set('Тази врата не е от стандартната фирмена библиотека. Моля, съвржете се с БИМ отдела')

t.Commit()


# final report
report = 'The orientation of ' + str(len(allIPADoors)) + ' door families was set successfully. '

if allNonIPADoorNames != []:
    report += '\n\nThe following door families were found in the project, not being subject to IPA copyrights. Please contact the BIM team for evaluation of these families: ' + str(allNonIPADoorNames)
    
TaskDialog.Show('Report', report)
    

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)