import os.path as osp
import cdsapi
import ast
"""
"reanalysis-era5-pressure-levels",
{
"variable": "temperature",
"pressure_level": "1000",
"product_type": "reanalysis",
"year": "2008",
"month": "01",
"day": "01",
"time": "12:00",
"format": "grib"
}, "download.grib"
"""

def cdsRequest3Strings(string_server, string_dict, string_to):
    """
    if(osp.isfile(string_to)):
        raise ValueError
    """
    request_dict = ast.literal_eval(string_dict)
    c = cdsapi.Client()
    c.retrieve(string_server,
    request_dict, string_to)

def cdsRequestJSON(string_json):
    if(not osp.isfile(string_json)):
        raise ValueError
    
    f = open(string_json,"r")
    stringList = f.readlines()
    bigstring = ' '.join([str(elem) for elem in stringList])
    #print(bigstring)
    bigstring.replace("\n","")
    startString1 = 0
    startDict = bigstring.index('{')
    endDict = bigstring.index('}')
    endString = len(bigstring)
    string1 = bigstring[0:startDict-3]
    dictString = bigstring[startDict+1:endDict]
    string2 = bigstring[endDict+3:len(bigstring)]
    
    string1 = string1[1:len(string1)-1]
    dictString = "{" + dictString + "}"
    string2 = string2[1:len(string2)-1]

    cdsRequest3Strings(string1,dictString,string2)

string_server = "reanalysis-era5-pressure-levels"
string_dict = '{"variable": "temperature","pressure_level": "1000","product_type": "reanalysis","year": "2008","month": "1","day": "1","time": "12:00","format": "grib"}'
#cdsRequest3Strings(string_server,string_dict, "download.grib")
cdsRequestJSON("test.json")
