import json
import codecs
import re

filename = 'chandra_all_cat_results.json'
with codecs.open(filename,'r',encoding='utf-8') as f:
    chandra_data = json.load(f)

labels = set() 

#label_pattern = re.compile('^.*(\S*\s*\d{2-4}\s*\S*).*$')
#label_pattern = re.compile('^.*(NGC\s+\S*).*$')
#patterns = ['NGC\s+\d+'] 
patterns = ['\<ASTROBJ\>[\w|\s|\.|\-|\+]+\<\/ASTROBJ\>', 'NGC\s+\d+'] 
for i in range((len(chandra_data))):
    if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
        abstract = chandra_data[i]['response']['docs'][0]['abstract']
        #print (abstract)
        for pattern in patterns:
            #results = search(pattern, abstract) 
            #results = re.search(pattern, abstract)
            results = re.findall(pattern, abstract)
            if results:
                for result in results:
                    #clean up XML-ish formatting
                    result = re.sub('\<\/?\w+\>','', result)
                    # replace spaces with underscore so we ensure tokenization
                    labels.add(result.replace(' ','_'))
    else:
        pass

print(str(labels))

