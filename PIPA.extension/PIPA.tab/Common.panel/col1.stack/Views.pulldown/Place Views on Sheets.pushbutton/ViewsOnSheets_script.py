# -*- coding: utf-8 -*-

#Copyright(c) 2019, Petar Penchev
# @All 1 Studio, http://all1studio.com

from pyrevit import revit, DB, UI
from pyrevit import forms
from pyrevit import script

from rpw import db

import System
from System import Array
from System.Collections.Generic import *

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('IronPython.Wpf')

import wpf 
from System import Windows
import logexporter

xamlfile = script.get_bundle_file('UI.xaml')

rаw_views = db.Collector(of_category='OST_Views',is_not_type=True).get_elements(wrapped=False)

unique=[]
dummy_phases=["00-WIP",None,"", [] , ' ']


for v in rаw_views:
    if v.LookupParameter("Phasing").AsString() not in unique and v.LookupParameter("Phasing").AsString() not in dummy_phases:
        unique.append(v.LookupParameter("Phasing").AsString())

phase = forms.SelectFromList.show(unique,
                                multiselect=False,
                                title='Select Phase',
                                button_name='Select Phase')

regular_views = db.Collector(of_category='OST_Views',is_not_type=True,where=lambda x: x.LookupParameter("Phasing").AsString() == phase \
                                                                            and "Delete" not in x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString() \
                                                                            or x.ViewType==DB.ViewType.Schedule).get_elements(wrapped=False)

shedules = db.Collector(of_class='View',is_not_type=True, where=lambda x: x.ViewType==DB.ViewType.Schedule).get_elements(wrapped=False)
legends = db.Collector(of_class='View',is_not_type=True, where=lambda x: x.ViewType==DB.ViewType.Legend).get_elements(wrapped=False)

all_views=regular_views+shedules+legends
all_views.sort(key=lambda x: x.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString())

sort_order = ["FloorPlan",
              "AreaPlan",
              "Section",
              "Elevation",
              "CeilingPlan",
              "ThreeD",
              "Legend",
              "Schedule",
              "DraftingView"
              ]

sheets  = db.Collector(of_category='OST_Sheets',is_not_type=True,where=lambda x: x.LookupParameter("Phasing").AsString() == phase \
                                                                            and "Delete" not in x.get_Parameter(DB.BuiltInParameter.SHEET_NAME).AsString()).get_elements(wrapped=False)

sheets.sort(key=lambda x: x.get_Parameter(DB.BuiltInParameter.SHEET_NUMBER).AsString())

class View_(object):
    def __init__(self,name,item,checked=False):
        self.viewname = name
        self.item = item
        self.state = checked

class Category_(object):
    def __init__(self,name,views):
        self.name = name
        self.views= views


class Sheet_(object):
    def __init__(self,name,item,categories):
        self.sheetname = name
        self.item = item
        self.categories= categories

ProjectSheets =[]
for s in sheets:
    Categories=[]

    for i in sort_order:
        cat_views=[]
        for v in all_views:
            if str(v.ViewType) == i:
                cat_views.append(View_(v.get_Parameter(DB.BuiltInParameter.VIEW_NAME).AsString(),v))
        Categories.append(Category_(i,cat_views))    

    ProjectSheets.append(Sheet_(s.get_Parameter(DB.BuiltInParameter.SHEET_NUMBER).AsString()+"\n"+s.get_Parameter(DB.BuiltInParameter.SHEET_NAME).AsString(),s,Categories)) 

class MyWindow(Windows.Window):
 
    def __init__(self):
        wpf.LoadComponent(self,xamlfile)

        self.sheet_list.ItemsSource=ProjectSheets


    def Execute(self,a,e):
        t=DB.Transaction(revit.doc,"Place Views On Sheets")
        t.Start()
        for sheet in ProjectSheets:
            for cat in sheet.categories:
                for view in cat.views:
                    try:
                        if view.state == True and view.item.ViewType!=DB.ViewType.Schedule:
                             DB.Viewport.Create(revit.doc,
                                                sheet.item.Id,
                                                view.item.Id,
                                                DB.XYZ(0, 0, 0))

                        elif view.state == True and view.item.ViewType==DB.ViewType.Schedule:
                            DB.ScheduleSheetInstance .Create(revit.doc,
                                                sheet.item.Id,
                                                view.item.Id,
                                                DB.XYZ(0, 0, 0))

                    except:
                        pass          
        t.Commit()             
        self.Close()
if phase != None:
    MyWindow().ShowDialog()

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)