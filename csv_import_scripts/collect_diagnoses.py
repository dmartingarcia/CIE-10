#!/usr/bin/env python3

import grequests
import requests
import json
from string import ascii_uppercase
import csv
import time
from progressbar import progressbar

codes = {}
fieldnames = ['code', 'description', 'perinatal', 'pediatric', 'maternity', 'adult', 'femalesOnly', 'malesOnly', 'poaExempt', 'noPrincipal', 'vcdp']

min = 0
max = 10 # should be 10

def generate_cie_10_code_requests(code):
    url_prefix = "https://www.eciemaps.sanidad.gob.es/cie10mc/2024/lt/sec/"
    return [grequests.get(f"{url_prefix}{code}{number}", timeout=30.0) for number in range(min, max)]

def iterate_through_codes():
    for first_char in progressbar(ascii_uppercase, redirect_stdout=True):
        print(f"CODE: {first_char}")
        future_requests = generate_cie_10_code_requests(first_char)
        get_list_of_codes_from_response(future_requests)

def get_list_of_codes_from_response(future_requests):
    for index, response in grequests.imap_enumerated(future_requests, size=10):
        for code_entry in response.json():
            id = code_entry.get("code")
            # excluding excludes1 type
            if code_entry.get("type") == "desc" or code_entry.get("type") == "inclusionTerm":
                if codes.get(id) is None:
                    information = {}
                    for key in fieldnames:
                        information[key] = code_entry.get(key)
                    codes[id] = information
                else:
                    updated_code = codes[id]
                    updated_code["description"] = updated_code.get("description") + " | " + code_entry.get("description")
                    print(updated_code["description"])
                    codes[id] = updated_code

def transform_fields(code):
    female_only = code.pop("femalesOnly") != None
    male_only = code.pop("malesOnly") != None

    if female_only:
        code["exclusiveGender"] = "F"
    elif male_only:
        code["exclusiveGender"] = "M"
    else:
        code["exclusiveGender"] = ""

    code["perinatal"] = 1 if code["perinatal"] is not None else 0
    code["pediatric"] = 1 if code["pediatric"] is not None else 0
    code["maternity"] = 1 if code["maternity"] is not None else 0
    code["adult"] = 1 if code["adult"] is not None else 0
    code["poaExempt"] = 1 if code["poaExempt"] is not None else 0
    code["noPrincipal"] = 1 if code["noPrincipal"] is not None else 0
    code["vcdp"] = 1 if code.pop("vcdp") is not None else 0


iterate_through_codes()
for code in codes.values():
    transform_fields(code)

with open('cie10-es-diagnoses.csv', 'w', newline='') as csvfile:
    csv_field_names = list(codes.values())[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=csv_field_names)
    writer.writeheader()
    writer.writerows(codes.values())
