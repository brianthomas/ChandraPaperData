import json
import codecs
import re

filename = 'chandra_all_cat_results.json'
with codecs.open(filename,'r',encoding='utf-8') as f:
    chandra_data = json.load(f)

labels = set() 

label_pattern = re.compile('^.*(\<.*\>).*$')
for i in range((len(chandra_data))):
    if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
        abstract = chandra_data[i]['response']['docs'][0]['abstract']
        #print (abstract)
        results = label_pattern.search(abstract) 
        if results and results.group(1):
            #print ('GROUP1: '+str(results.group(1)))
            cnt = 0
            for item in re.split ('<', abstract):
                if cnt == 0:
                    cnt = 1
                else:
                    item = re.sub (">.*", "", item)
                    item = item.replace('/', '')
                    if not re.search ('href', item):
                        labels.add(item)
    else:
        pass

print(str(labels))
