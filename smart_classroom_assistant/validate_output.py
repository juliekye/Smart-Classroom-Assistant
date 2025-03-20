from boto3 import client as boto3_client
import json

output_bucket = "awsome-people-output"


def mapping_hsh():
    file = open('mapping', 'r').read().split('\n')
    hsh = {}
    for line in file:
        if len(line.split(':')) < 2:
            print(line)
            continue
        key, student = line.split(':')
        key = key.split('.')[0]+".csv"
        major, year = student.split(',')
        hsh[key] = {
            "major": major,
            "year": year
        }
    return hsh


def clear_output_bucket():
    global output_bucket
    s3 = boto3_client('s3')
    list_obj = s3.list_objects_v2(Bucket=output_bucket)
    hsh = {}
    try:
        for item in list_obj["Contents"]:
            key = item["Key"]
            response = s3.get_object(Bucket=output_bucket, Key=key)
            value = response['Body'].read().decode("utf-8")
            name, major, year = value.split(',')
            hsh[key] = {
                "major": major,
                "year": year,
                "name": name
            }
    except Exception as e:
        print(e)
    return hsh


input_hsh = mapping_hsh()
output_hsh = clear_output_bucket()

for key, value in output_hsh.items():
    if key not in input_hsh:
        print(key + " not in input")
    else:
        expected = input_hsh[key]
        if value["year"] != expected["year"] or value["major"] != expected["major"]:
            print("Expected: " + json.dumps(expected))
            print("Value: " + json.dumps(value))
