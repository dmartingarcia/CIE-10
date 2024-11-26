#!/usr/bin/env python3

import grequests
import requests
import json
from string import ascii_uppercase
import csv
import time
from progressbar import progressbar

fieldnames = ['code', 'description', 'femalesOnly', 'malesOnly', 'timesSelected']
codes = {}


def get_t1_entries():
    types = {}
    results = requests.get("https://www.eciemaps.sanidad.gob.es/cie10pcs/2024/tab/t1").json()
    for element in results:
        print(element)
        types[element.get("t3")] = {"name": element.get("d1")}
    return types

def get_t2_entries(types):
    subtypes = {}
    for type in types:
        print(type)
        obj_type = types[type]
        results = requests.get(f"https://www.eciemaps.sanidad.gob.es/cie10pcs/2024/tab/t2/{type}").json()
        for element in results:
            print(element)
            subtypes[element.get("t3")] = {"class_name": obj_type.get("name"), "subclass_name": element.get("d1")}
    return subtypes

def get_t3_entries(types):
    subtypes = {}
    for type in types:
        print(type)
        obj_type = types[type]
        results = requests.get(f"https://www.eciemaps.sanidad.gob.es/cie10pcs/2024/tab/t3/{type}").json()
        for element in results:
            print(element)
            subtypes[element.get("t3")] = {"class_name": obj_type.get("class_name"), "subclass_name": obj_type.get("subclass_name"), "procedure": element.get("d1") }
    return subtypes

def get_procedure_subclasses(types):
    codes = {}
    print("Calculating all combinations!\n")
    
    requests = [grequests.get(f"https://www.eciemaps.sanidad.gob.es/cie10pcs/2024/lt/table/{key}") for key in types]

    for request in progressbar(grequests.imap(requests, size=10), redirect_stdout=True, max_value=len(types)):
        results = request.json()["pcsTable"][0]
        type = results["index"]
        obj_type = types.get(type)
        definition = results["axis"][-1].get("definition")

        for row in results["pcsRow"]:            
            localizations = []
            approaches = []
            devices = []
            califications = []


            for localization in row["axis"][0]["label"]:
                localizations.append({"localization": localization["value"], "code": localization['code']})

            for approach in row["axis"][1]["label"]:
                approaches.append({"approach": approach["value"], "code": approach['code']})

            for device in row["axis"][2]["label"]:
                devices.append({"device": device["value"], "code": device['code']})

            for calification in row["axis"][3]["label"]:
                califications.append({"calification": calification["value"], "code": calification['code']})

            for localization in localizations:
                for approach in approaches:
                    for device in devices:
                        for calification in califications:
                            key = f"{type}{localization['code']}{approach['code']}{device['code']}{calification['code']}"
                            codes[key] = {"class_name": obj_type.get("class_name"), "subclass_name": obj_type.get("subclass_name"), "procedure": obj_type.get("procedure"), "procedure_definition": definition, "localization": localization.get('localization'), "approach": approach.get("approach"), "device": device.get("device"), "calification": calification.get("calification"), "definition": definition}

    return codes



entries = get_t1_entries()
entries = get_t2_entries(entries)
entries = get_t3_entries(entries)
codes = get_procedure_subclasses(entries)


url_prefix = "https://www.eciemaps.sanidad.gob.es/ref/cie10pcs"
#cie10_code_requests = [grequests.get(f"{url_prefix}/{key}") for key in codes.keys()]
#for request in progressbar(grequests.imap(cie10_code_requests, size=10), max_value=len(codes)):
for code_key in progressbar(codes.keys(), max_value=len(codes)):
    request = requests.get(f"{url_prefix}/{code_key}")

    results = request.json()
    code = codes.get(results["code"])

    code["description"] = results["description"]
    code["timesSelected"] = results["timesSelected"]

    if results['femalesOnly'] != None:
        code["gender"] = "F"
    elif results['malesOnly'] != None:
        code["gender"] = "M"
    else:
        code["gender"] = ""

fieldnames = ['class_name', 'subclass_name', 'procedure', 'procedure_definition', 'localization', 'approach', 'device', 'calification', 'definition', 'description', 'timesSelected', 'gender']
with open('cie10-es-procedures.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(codes.values())

headers = {"Content-Type": "application/json"}
i = 0
epoch = int(time.time())
for entry in progressbar(codes, redirect_stdout=True):
    code = codes[entry]
    r = requests.put(f"http://localhost:9200/procedures-{epoch}/_doc/{entry}", data=json.dumps(code), headers=headers)
    i = i +1
    if r.status_code == 201:
        print(f"{entry}-{r.status_code} ---- {i}/{len(codes)}")
    else:
        print(f"ERROR: {r.status_code} - {entry}")
