#!/usr/bin/env python3

import grequests
import requests
import json
from string import ascii_uppercase
import csv
import date

codes = {}
fieldnames = ["indx", "area", "description", "codes", "code1", "code2", "code3", "code4", "code5", "code6"]
min = 0
max = 10 # should be 10
FIRST_LETTER = ["0","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
def generate_cie_10_code_requests:
    url_prefix = "https://www.eciemaps.sanidad.gob.es/cie10mc/2024/ia/drugsByLetter/"
    return [grequests.get(f"{url_prefix}{code}{number}") for number in FIRST_LETTER]

def iterate_through_codes():
    future_requests = generate_cie_10_code_requests(first_char)
    get_list_of_codes_from_response(future_requests)
            
def get_list_of_codes_from_response(future_requests):
    for index, response in grequests.imap_enumerated(future_requests, size=10):
        for code_entry in response.json():
            id = code_entry.get("code")
            finalNode = code_entry.get("finalNode")
            if finalNode:
                print(f"id: {id}")
                information = {}

                for key in fieldnames:
                    information[key] = code_entry.get(key)

                codes[id] = information
        

iterate_through_codes()

with open('cie10-es.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(codes.values())

headers = {"Content-Type": "application/json"}
i = 0
epoch = int(time.time())
for entry in codes:
    code = codes[entry]
    r = requests.put(f"http://localhost:9200/chemicals-{epoch}/_doc/{entry}", data=json.dumps(code), headers=headers)
    i = i +1
    if r.status_code == 201:
        print(f"{entry}-{r.status_code} ---- {i}/{len(codes)}")
    else:
        print(f"ERROR: {r.status_code} - {entry}")



#si no es final node, buscar childrens https://www.eciemaps.sanidad.gob.es/cie10mc/2024/ia/children/84666
