def logExport(current_file):
    import clr
    import csv
    import shutil
    from datetime import datetime
    import sys
    sys.path.append('C:\Program Files (x86)\IronPython 2.7\Lib')

    clr.AddReference("RevitAPI")
    from Autodesk.Revit.DB import BasicFileInfo


    # Get current document
    log_export_doc = __revit__.ActiveUIDocument.Document
    # print(log_export_doc)

    # Get file version
    app = log_export_doc.Application

    # Get the file path
    localFilePath = log_export_doc.PathName
    # print(localFilePath)

    # time_data
    time_data_full = datetime.now()
    time_data_format = datetime.strftime(time_data_full, "%y-%m-%d %H:%M:%S")
    time_data = "20" + time_data_format
    # print(time_data)

    # user_data
    user_data = app.Username
    # print(user_data)

    # script_data
    script_data = (current_file[-1].split("_"))[0]
    #print(script_data)

    # document_data
    document_data = localFilePath
    # print(document_data)

    # time_saved_data_data
    time_saved_data = 0
    # print(time_saved_data)

    # testing_data
    testing_data = "IPA_Tab"
    # print(testing_data)

    # project_data
    project_data = (localFilePath.split("-"))[0]
    project_num = (project_data.split("\\"))[-1]
    # print(project_num)

    # consultant_data
    try:
        consultant_data = (localFilePath.split("-"))[1]
    except:
        consultant_data = "Unknown"
    # print(consultant_data)

    #log_file_name
    file_name = "20" + datetime.strftime(time_data_full, "%y%m%d-%H%M%S")
    # print(file_name)


    header = ["Data Time", "User", "Script", "Document", "Time Saved", "Testing", "Project", "Consultant"]
    data = [time_data, user_data, script_data, document_data, time_saved_data, testing_data, project_num, consultant_data]

    original = "T:/02.PRELIMINARY/_templates/DYNAMO LOG FILE DUMP/00_Template/Template_csv.csv"
    target = "T:/02.PRELIMINARY/_templates/DYNAMO LOG FILE DUMP/" + str(file_name) + "_" + str(user_data) + ".csv"

    shutil.copyfile(original, target)

    with open(target, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerow(data)
