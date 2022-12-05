# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit, DB, UI
from pyrevit import coreutils
from pyrevit import forms
from pyrevit import script
import logexporter

from rpw import db

import System
from System import Array
from System.Collections.Generic import *

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

xamlfile = script.get_bundle_file('UI.xaml')

import wpf 
from System import Windows

def unique_types(list):
    unique=[]
    for l in list:
        if l.Symbol.Id not in unique:
            unique.append(l.Symbol.Id)
    return unique


class MyWindow(Windows.Window):

    def __init__(self):
    	wpf.LoadComponent(self,xamlfile)
       

    def Execute(self,s,a):

        self.Close()

        rowheight= int(self.RowHeight.Text) 
        descriptionwidth= int(self.DescriptionWidth.Text) 
        columnwidth= int(self.ColumnWidth.Text) 
        titleheight= int(self.TitleHeight.Text) 

        doc=revit.doc
        view = doc.ActiveView

        cat_list = List[DB.BuiltInCategory]([DB.BuiltInCategory.OST_ElectricalEquipment,
                                    DB.BuiltInCategory.OST_LightingFixtures,
                                    DB.BuiltInCategory.OST_LightingDevices , 
                                    DB.BuiltInCategory.OST_ElectricalFixtures,
                                    DB.BuiltInCategory.OST_CommunicationDevices,
                                    DB.BuiltInCategory.OST_DataDevices,
                                    DB.BuiltInCategory.OST_SecurityDevices,
                                    DB.BuiltInCategory.OST_FireAlarmDevices,
                                    DB.BuiltInCategory.OST_ConduitFitting]
                                    )
        filter = DB.ElementMulticategoryFilter(cat_list)

        elm_list = DB.FilteredElementCollector(doc).WherePasses(filter).WhereElementIsNotElementType().ToElements()

        output=[]

        for e in elm_list:
        	output.append(e)

        sort_order = {"Electrical Equipment":0,
        			  "Lighting Fixtures":1,
        			  "Lighting Devices":2,
        			  "Electrical Fixtures":3,
        			  "Communication Devices":4,
        			  "Data Devices":5,
        			  "Security Devices":6,
        			  "Fire Alarm Devices":7,
        			  "Conduit Fittings":8}

        output.sort(key=lambda x: (sort_order[str(x.Category.Name)]))

        lc=db.Collector(view=view, of_category='OST_LegendComponents').get_first(wrapped=False)

        RowHeight=rowheight/304.8
        DescriptionWidth=descriptionwidth/304.8
        ColumnWidth=columnwidth/304.8
        TitleHeight=titleheight/304.8


        #Text Left Alignment
        opt = DB.TextNoteOptions()
        opt.HorizontalAlignment=DB.HorizontalTextAlignment.Left
        opt.VerticalAlignment=DB.VerticalTextAlignment.Middle
        opt.TypeId=DB.FilteredElementCollector(doc).OfClass(DB.TextNoteType).WhereElementIsElementType().FirstElementId()

        #Text Center Alignment
        optc = DB.TextNoteOptions()
        optc.HorizontalAlignment=DB.HorizontalTextAlignment.Center
        optc.VerticalAlignment=DB.VerticalTextAlignment.Middle
        optc.TypeId=DB.FilteredElementCollector(doc).OfClass(DB.TextNoteType).WhereElementIsElementType().FirstElementId()


        #Start Group Transaction
        tg=DB.TransactionGroup(doc,"Electrical Legend")
        tg.Start()


        #Transaction for working with legend components and text notes
        t=DB.Transaction(doc,"Copy and Change Legend Component")
        t.Start()

        for i,ft in zip(range(0,len(unique_types(output))),unique_types(output)):
            offset=i*-RowHeight
            doc.GetElement(DB.ElementTransformUtils.CopyElement(doc,lc.Id,DB.XYZ(0,offset,0))[0]).get_Parameter(DB.BuiltInParameter.LEGEND_COMPONENT).Set(ft)
            if doc.GetElement(ft).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MODEL).AsString() != None:
                TextNote=DB.TextNote.Create(doc, view.Id, DB.XYZ(0+ColumnWidth/2+0.5,offset,0),doc.GetElement(ft).get_Parameter(DB.BuiltInParameter.ALL_MODEL_MODEL).AsString(), opt)
                TextNote.Width=(DescriptionWidth-400/304.8)/doc.ActiveView.Scale
        for txt,location in zip(["СИМВОЛ","ОПИСАНИЕ"],[DB.XYZ(0,(RowHeight+TitleHeight)/2,0),DB.XYZ(0+(DescriptionWidth+ColumnWidth)/2,(RowHeight+TitleHeight)/2,0)]):
            DB.TextNote.Create(doc, view.Id, location, txt, optc)

        doc.Delete(lc.Id)

        t.Commit()

        lines=[]

        #First Horizontal line for Title Row
        tp1=DB.XYZ(0-ColumnWidth/2,RowHeight/2+TitleHeight,0)
        tp2=DB.XYZ(DescriptionWidth+ColumnWidth/2,RowHeight/2+TitleHeight,0)
        lines.append(DB.Line.CreateBound(tp1,tp2))


        #Horizontal Lines for each row
        for i in range(0,len(unique_types(output))+1):
            y=i*-RowHeight+RowHeight/2
            p1=DB.XYZ(0-ColumnWidth/2,y,0)
            p2=DB.XYZ(DescriptionWidth+ColumnWidth/2,y,0)
            lines.append(DB.Line.CreateBound(p1,p2))

        #Vertical Lines
        for i in (0-ColumnWidth/2,ColumnWidth/2,DescriptionWidth+ColumnWidth/2):
            p1=DB.XYZ(i,0+RowHeight/2+TitleHeight,0)
            p2=DB.XYZ(i,len(unique_types(output))*-RowHeight+RowHeight/2,0)
            lines.append(DB.Line.CreateBound(p1,p2))

        #Transaction for creating detail lines
        t=DB.Transaction(doc,"Detail Lines Table")
        t.Start()

        for l in lines:
            doc.Create.NewDetailCurve(view,l)
        t.Commit()

        tg.Assimilate()	
    	

MyWindow().ShowDialog()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)