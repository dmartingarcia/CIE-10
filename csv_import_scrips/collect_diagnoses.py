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
            if id is not None and codes.get(id) is None:
                information = {}

                for key in fieldnames:
                    information[key] = code_entry.get(key)

                codes[id] = information

def transform_fields(code):
    female_only = code.pop("femalesOnly") != None
    male_only = code.pop("malesOnly") != None

    if female_only:
        code["exclusiveGender"] = "F"
    elif male_only:
        code["exclusiveGender"] = "M"
    else:
        code["exclusiveGender"] = ""

    code["perinatal"] = code["perinatal"] != None
    code["pediatric"] = code["pediatric"] != None
    code["maternity"] = code["maternity"] != None
    code["adult"] = code["adult"] != None
    code["poaExempt"] = code["poaExempt"] != None
    code["noPrincipal"] = code["noPrincipal"] != None
    code["vcdp"] = code.pop("vcdp") != None


iterate_through_codes()

with open('cie10-es-diagnoses.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(codes.values())
