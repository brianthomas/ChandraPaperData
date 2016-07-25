'''

Simple little script to take data dumped from ADS (using the 
retrieve.pl program) and use the descriptions/abstracts to create 
a model of significant terms (a dictionary) to support term 
(keyword) extraction from text.

Created on Jul 12, 2016

@author: thomas
'''

# Rules for processing tokens which we may miss with ordinary
# processing engine. Rules which match will cause all whitespace
# to be changed into underscores so that the words will be picked
# up as a group 
special_token_patterns = ['\<ASTROBJ\>[\w|\s|\.|\-|\+]+\<\/ASTROBJ\>', 'NGC\s+\d+']

# the minimum number of times a term must occur in training corpus
# before its considered significant enough to include in the model
# dictionary
MIN_TERM_OCCUR = 3
    
def createTermDictionaryFromAbstracts (jsonfile, output_dict_model, output_processing_rules_model):
    
    import ocio.textmining.extraction as terms
    import pickle
    import json
    import codecs
    import re
    from gensim.parsing.preprocessing import STOPWORDS
    
    print ("Training using file: "+jsonfile)
    
    print (" * Parsing chandra abstracts file")
    
    with codecs.open(jsonfile,'r',encoding='utf-8') as f:
        chandra_data = json.load(f)

    corpus = []
    processing_rules = {}

    for i in range((len(chandra_data))):
        if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
             # grab the raw abstract
             abstract = chandra_data[i]['response']['docs'][0]['abstract']
             # process it to pull out sources, changing spaces to underscore so we make
             # sure to capture the term fully
             replacement_labels = {}
             for pattern in special_token_patterns:
                 results = re.findall(pattern, abstract)
                 if results:
                     for result in results:
                         #clean up XML-ish formatting
                         result = re.sub('\<\/?\w+\>','', result)
                         # replace spaces with underscore so we ensure tokenization
                         replacement_labels[result] = result.replace(' ','_')

                         # store the processing rule for downstream use
                         processing_rules[result] = replacement_labels[result]

             for label in replacement_labels.keys():
                 # now replace the string we find with the one we want
                 abstract = abstract.replace(label, replacement_labels[label])

             corpus.append(abstract)
        else:
            pass

    print (" * Writing processing rules model")
    with open(output_processing_rules_model, 'wb+') as f:
        pickle.dump(processing_rules, f)

    print (" * Creating trained model from ADS abstract field")
    dict_model = terms.UnstructuredTextTermExtractor.train(corpus, stop_words=STOPWORDS, 
                                                           min_term_count=MIN_TERM_OCCUR)
    
    print (" * Writing pickled output to file:"+ output_dict_model)
    with open(output_dict_model, 'wb+') as f:
        pickle.dump(dict_model, f)

    print (" * Finished")

if __name__ == '__main__':
    import argparse
    ''' Run the application '''
    
    # Use nargs to specify how many arguments an option should take.
    ap = argparse.ArgumentParser(description='OpenData training Appliance -- creates term model (dictionary) from opengov json formatted data.')
    ap.add_argument('-i', '--input', type=str, help='JSON formatted file to pull from')
    ap.add_argument('-m', '--output_dict_model', type=str, help='Output model file to write to (in pickled form)')
    ap.add_argument('-p', '--output_processing_rules_model', type=str, help='Output processing rules model file to write to (in pickled form)')
   
    # parse argv
    opts = ap.parse_args()
    
    if not opts.input:
        print ("the --input <file> parameter must be specified")
        ap.print_usage()
        exit()
        
    if not opts.output_dict_model:
        print ("the --output_dict_model <file> parameter must be specified")
        ap.print_usage()
        exit()
    
    if not opts.output_processing_rules_model:
        print ("the --output_processing_rules_model <file> parameter must be specified")
        ap.print_usage()
        exit()

    createTermDictionaryFromAbstracts(opts.input, opts.output_dict_model, opts.output_processing_rules_model)
    
    
    
