import json

with open('./chandra_all_cat_results.json', 'r') as f:
    print (str(f))
    chandra_data = json.load(f)

keywords = chandra_data["keyword"]
print(keywords)
