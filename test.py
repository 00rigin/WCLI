import json

file_path = "./log.json"

with open(file_path, "r") as json_file:
    json_data = json.load(json_file)
    #print(json_data)
    print("")
    #print(json_data)
    print(json_data['f_cluster'])
