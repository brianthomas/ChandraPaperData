'''

Simple little script to take data dumped from ADS (using the 
retrieve.pl program) and use the descriptions/abstracts to create 
a model of significant terms (a dictionary) to support term 
(keyword) extraction from text.

Created on Jul 12, 2016

@author: thomas
'''

import logging
logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
#logging.getLogger('ocio').setLevel(logging.DEBUG)
#logging.getLogger('ocio.textmining').setLevel(logging.DEBUG)
#logging.getLogger('ocio.textmining.extraction').setLevel(logging.DEBUG)
logging.getLogger('gensim').setLevel(logging.WARN)

# Rules for processing tokens which we may miss with ordinary
# processing engine. Rules which match will cause all whitespace
# to be changed into underscores so that the words will be picked
# up as a group 
special_token_patterns = ['\<ASTROBJ\>[\w|\s|\.|\-|\+]+\<\/ASTROBJ\>', 'NGC\s+\d+']

# the mininmum times we need a feature to occur
# before accepting it into our featureset
MIN_TERM_OCCUR = 1

def createTermDictionaryFromAbstracts (input, output, input_dict_model, input_processing_rules_model):
    
    from ocio.textmining.extraction import UnstructuredTextTermExtractor
    import pickle
    import json
    import codecs
    
    LOG.info(" * Parsing chandra abstracts file")
    with codecs.open(input,'r',encoding='utf-8') as f:
        chandra_data = json.load(f)

    corpus = []
    for i in range((len(chandra_data))):
        if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
             # grab the raw abstract
             abstract = chandra_data[i]['response']['docs'][0]['abstract']
             corpus.append(abstract)
        else:
            pass
    LOG.info("   Got "+str(len(corpus))+" abstracts to process")

    LOG.info(" * Loading dict and processing rules models")
    with open(input_dict_model, 'rb+') as f:
        dict_model = pickle.load (f)
    
    with open(input_processing_rules_model, 'rb+') as f:
        processing_rules = pickle.load (f)
        
    # our term extractor
    term_extractor = UnstructuredTextTermExtractor(dict_model)
    
    LOG.info(" * Extracting terms by abstract ")
    abstract_terms = []
    count = 0
    import time
    for abstract in corpus:
        start_time = time.time()
        for rule in processing_rules.keys():
            abstract = abstract.replace (rule, processing_rules[rule])
        LOG.debug("ABSTRACT:"+str(abstract))
        
        terms = set(term_extractor.find_terms([abstract], highest_colocation=5, 
                                              min_term_count=MIN_TERM_OCCUR, preserve_case=True))
        LOG.debug("TERMS: "+str(terms))
        abstract_terms.append(terms)
        count = count + 1
        end_time = time.time()
        LOG.info("did abstract:"+str(count)+" in "+str(end_time-start_time)+" sec") 
    
    LOG.info(" * Writing pickled output to file:"+ output)
    with open(output, 'wb+') as f:
        pickle.dump(abstract_terms, f)

    LOG.info(" * Finished")

if __name__ == '__main__':
    import argparse
    ''' Run the application '''
    
    # Use nargs to specify how many arguments an option should take.
    ap = argparse.ArgumentParser(description='OpenData training Appliance -- creates term model (dictionary) from opengov json formatted data.')
    ap.add_argument('-i', '--input', type=str, help='Input abstracts file in JSON')
    ap.add_argument('-o', '--output', type=str, help='File to write pickled output list of terms extracted')
    ap.add_argument('-m', '--input_dict_model', type=str, help='Input model file to write to (in pickled form)')
    ap.add_argument('-p', '--input_processing_rules_model', type=str, help='Input processing rules model file to write to (in pickled form)')
   
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
        
    if not opts.input_dict_model:
        print ("the --input_dict_model <file> parameter must be specified")
        ap.print_usage()
        exit()
    
    if not opts.input_processing_rules_model:
        print ("the --input_processing_rules_model <file> parameter must be specified")
        ap.print_usage()
        exit()

    createTermDictionaryFromAbstracts(opts.input, opts.output, opts.input_dict_model, opts.input_processing_rules_model)
    
    
    
