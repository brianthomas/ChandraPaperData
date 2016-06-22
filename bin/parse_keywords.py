import json
import codecs

filename = "data/chandra_all_cat_results.json"
#filename = "test.json"
with codecs.open(filename,'r',encoding='utf-8') as f:
    chandra_data = json.load(f)

#keywords = chandra_data[0]["keyword"]
print (str(chandra_data[0]['response']['docs']))
#print(keywords)

print ("Finished")
