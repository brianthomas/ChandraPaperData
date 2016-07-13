'''

Simple little script to take data dumped from ADS (using the 
retrieve.pl program) and use the descriptions/abstracts to create 
a model of significant terms (a dictionary) to support term 
(keyword) extraction from text.

Created on Jul 12, 2016

@author: thomas
'''

    
def createTermDictionaryFromAbstracts (jsonfile, output):
    
    import ocio.textmining.extraction as terms
    import pickle
    import json
    import codecs
    
    print ("Training using file: "+jsonfile)
    
    print (" * Parsing opendata file")
    
    import codecs

    with codecs.open(jsonfile,'r',encoding='utf-8') as f:
        chandra_data = json.load(f)

    corpus = []

    for i in range((len(chandra_data))):
        if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
             corpus.append(chandra_data[i]['response']['docs'][0]['abstract'])
        else:
            pass
    
    print (" * Creating trained model from ADS abstract field")
    trained_model = terms.UnstructuredTextTermExtractor.train(corpus)
    
    print (" * Writing pickled output to file:"+ output)
    with open(output, 'wb+') as f:
        pickle.dump(trained_model, f)
        
    print (" * Finished")


if __name__ == '__main__':
    import argparse
    ''' Run the application '''
    
    # Use nargs to specify how many arguments an option should take.
    ap = argparse.ArgumentParser(description='OpenData training Appliance -- creates term model (dictionary) from opengov json formatted data.')
    ap.add_argument('-i', '--input', type=str, help='JSON formatted file to pull from')
    ap.add_argument('-o', '--output', type=str, help='Output file to write to (in pickled form)')
   
    # parse argv
    opts = ap.parse_args()
    
    if not opts.input:
        print ("the --input <file> parameter must be specified")
        ap.print_usage()
        exit()
        
    if not opts.output:
        print ("the --output <file> parameter must be specified")
        ap.print_usage()
        exit()
    
    createTermDictionaryFromAbstracts(opts.input, opts.output)
    
    
    
