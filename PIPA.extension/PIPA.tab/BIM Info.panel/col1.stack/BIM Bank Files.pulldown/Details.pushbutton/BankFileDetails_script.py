# !/usr/bin/env python
#  -*- coding: utf-8 -*- 

import os
import logexporter
from pyrevit import forms
from pyrevit.revit import ErrorSwallower

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Events import *

# select folder of files to be updated
directoryContents = r"IPA-DATA-BANK-DETAILS-Central.rvt"
filesFolder = r"B:\\01. IPA REVIT-CAD TEMPLATES\\20. BANK FILES\\"

tOptions = TransactWithCentralOptions()
revitModelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(os.path.join(filesFolder, directoryContents))

# define open options so that Revit automatically closes all worksets and detaches the file as central upon opening
openOptions = OpenOptions()
openOptions.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
# openConfig = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
# openOptions.SetOpenWorksetsConfiguration(openConfig)

# open Revit document
revitDocument = __revit__.OpenAndActivateDocument(revitModelPath, openOptions, True)

# Export log file
current_file = __file__.split("\\")
logexporter.logExport(current_file)