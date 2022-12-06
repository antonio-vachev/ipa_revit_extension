# !/usr/bin/env python
#  -*- coding: utf-8 -*- 

import os

from pyrevit import forms
from pyrevit.revit import ErrorSwallower

from Autodesk.Revit.DB import * 
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Events import *


"""
# define dialog actions
def on_dialog_open(sender, event):
    #dialMessage = event.TaskDialogShowingEventArgs.Message
    try:
        if event.DialogId == 'Dialog_Revit_DocWarnDialog':
            #event.OverrideResult(1001)
            print('DocWarn')
            #print(dialMessage)
        else:
            print(event.DialogId)
            #print(dialMessage)
    except Exception as e:
        print(e)
"""


# select folder of files to be updated
directoryContents = []
filesFolder = forms.pick_folder(title = 'File Folder')

for element in os.listdir(filesFolder):
    if ".rvt" in (os.path.join(filesFolder, element)):
        directoryContents.append(os.path.join(filesFolder, element))


# define worksharing save as options
workSaveAsOptions = WorksharingSaveAsOptions()
workSaveAsOptions.SaveAsCentral = True
    
# define save as options for worksharing models
saveAsOptionsWorksharing = SaveAsOptions()
saveAsOptionsWorksharing.MaximumBackups = 10
saveAsOptionsWorksharing.OverwriteExistingFile = True
saveAsOptionsWorksharing.SetWorksharingOptions(workSaveAsOptions)
    
# define save as options for non - workshared models
saveAsOptions = SaveAsOptions()
saveAsOptions.MaximumBackups = 10
saveAsOptions.OverwriteExistingFile = True

# define relinquish options
relinquishOptions = RelinquishOptions(False)
relinquishOptions.StandardWorksets = True
relinquishOptions.ViewWorksets = True
relinquishOptions.FamilyWorksets = True
relinquishOptions.UserWorksets = True
relinquishOptions.CheckedOutElements = True

# define synchronize options
syncOptions = SynchronizeWithCentralOptions()
syncOptions.SetRelinquishOptions(relinquishOptions)
syncOptions.Compact = True
syncOptions.SaveLocalBefore = True
syncOptions.SaveLocalAfter = True

tOptions = TransactWithCentralOptions()

for revitModel in directoryContents:

    revitModelPath = ModelPathUtils.ConvertUserVisiblePathToModelPath(revitModel)
    
    # define open options so that Revit automatically closes all worksets and detaches the file as central upon opening
    openОptions = OpenOptions()
    openОptions.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
    openConfig = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
    openОptions.SetOpenWorksetsConfiguration(openConfig)
    """
    # call the application and subscribe to an event
    uiApp = UIApplication(__revit__.Application)
    uiApp.DialogBoxShowing += on_dialog_open
    """
    # open Revit document
    revitDocument = __revit__.Application.OpenDocumentFile(revitModelPath, openОptions)
    
    # save and close Revit document
    if revitDocument.IsWorkshared:
        revitDocument.SaveAs(revitModel, saveAsOptionsWorksharing)
        revitDocument.SynchronizeWithCentral(tOptions, syncOptions)
    else:
        revitDocument.SaveAs(revitModel, saveAsOptions)
    """
    # unsibscribe to an event
    uiApp.DialogBoxShowing -= on_dialog_open
    """
    
    revitDocument.Close(True)