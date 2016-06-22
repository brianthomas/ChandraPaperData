import json
import codecs

filename = 'chandra_all_cat_results.json'
with codecs.open(filename,'r',encoding='utf-8') as f:
    chandra_data = json.load(f)

keywords = []

for i in range((len(chandra_data))):
    if chandra_data[i]['response']['docs'] != [] and 'keyword' in chandra_data[i]['response']['docs'][0]:
        keywords.append(chandra_data[i]['response']['docs'][0]['keyword'])
    else:
        pass

print(keywords)
