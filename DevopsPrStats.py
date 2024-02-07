# Azure Devops pull request parser.  To extract PR JSON from Azure Devops you need 
# the Devops CLI and do a command like this:
# az repos pr list --repo=MeasureLink-MCS --status=completed --top=1000 > c:\temp\CompletedPrs.json
# Note this api can never return more than 1000 records.  Version 2.0 would need to use 
# the DevOps REST api and make multiple continuation requests to get all the data...
import json
import re
import sys
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta

_filePath = ""
_dateFilter = ""
_userFilter = ""

def Main():
    ProcessArgs()
    
    _startingDateTime = pytz.timezone('US/Eastern').localize(datetime.strptime(_dateFilter, "%Y-%m-%d"))
    _endingDateTime = _startingDateTime + relativedelta(years=1)

    with open(_filePath) as jsonFile:
        parsedJson = json.load(jsonFile)

        prTotal = len(parsedJson)

        if _userFilter == "" and _dateFilter == "":
            print(f"There are {prTotal} pull requests in the JSON file")
            return
        
        if prTotal == 0:
            print("The file contains no pull requests.")
            return
        
        dateTotal = 0
        prCount = 0

        for prDict in parsedJson:
            if _dateFilter != "":
                createDateStr = str(prDict["creationDate"])
                # parse date in universal date time formate
                createDate = datetime.strptime(createDateStr, "%Y-%m-%dT%H:%M:%S.%f%z")

                if not createDate >= _startingDateTime and createDate < _endingDateTime:
                    continue
                else:
                    dateTotal = dateTotal + 1
            if _userFilter != "":
                createdByDict = prDict["createdBy"]
                createdByUser = str(createdByDict["uniqueName"])
                if not re.search(_userFilter, createdByUser, re.IGNORECASE):
                    continue
            prCount = prCount + 1
        
        totalCount = dateTotal if _userFilter != "" else prTotal
        print(f"There were {prCount} matching pull requests out of {totalCount} total ({(prCount / totalCount * 100.0):.2f}%)")

def ProcessArgs():
    argc = len(sys.argv)

    if argc == 1:
        ShowUsage("Filename required")

    global _filePath
    _filePath = sys.argv[1]

    if argc > 2:
        for index in range(2, argc):
            param = sys.argv[index]
            
            if param.startswith("--help"):
                ShowUsage("")

            if param.startswith("--user"):
                global _userFilter 
                _userFilter = ExtractParam(param)
                continue

            if param.startswith("--date"):
                global _dateFilter
                _dateFilter = ExtractParam(param)
                continue
   

def ExtractParam(param: str) -> str:
    splitArr = param.split("=")
    if len(splitArr) != 2:
        ShowUsage()
    
    return splitArr[1].replace("\"", "").replace("'", "")

def ShowUsage(error: str):   
    raise SystemExit(f"{error} {sys.argv[0]} filename [--user=user] [--date=YYYY-MM-DD]\r\nUser can be partial, as can the date")

Main()