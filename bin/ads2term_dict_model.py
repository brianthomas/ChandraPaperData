'''

Simple little script to take data dumped from ADS (using the 
retrieve.pl program) and use the descriptions/abstracts to create 
a model of significant terms (a dictionary) to support term 
(keyword) extraction from text.

Created on Jul 12, 2016

@author: thomas
'''

# the minimum number of times a term must occur in training corpus
# before its considered significant enough to include in the model
# dictionary
MIN_TERM_OCCUR = 3

# Rules for processing tokens which we may miss with ordinary
# processing engine. Rules which match will cause all whitespace
# to be changed into underscores so that the words will be picked
# up as a group 
special_token_patterns = ['\<ASTROBJ\>[\w|\s|\.|\-|\+]+\<\/ASTROBJ\>', 'NGC\s+\d+', ]

# some common formatting patterns we need to clean out
format_token_replacement_patterns = { ':': '', '-': ' ', '[': '', ']': '',  '(': '',
                                      ')': '', '\'': '', '=': '', '&': 'and', '\\': '',  
                                    } 
# some replacement patterns germane to just Chandra data
# includes some particular misspellings and duplications
chandra_token_repl_patterns = { 'H II': 'HII', 'h\s{0,1}ii': 'HII', 'balck': 'black', 
                                'intergalacic': 'intergalactic', 'submillimetre': 'submillimeter', 
                                'centre': 'center', 'agn': 'AGN', 'cd': 'CD', 'disc': 'disk'
                              }

'''
    # IF its not all uppercase, then not acronyms, so lets stem it
    if token_list[j] != token_list[j].upper():
        token_list[j] = nltk.stem.SnowballStemmer('english').stem(token_list[j])
        
    # add underscore to preserve spacing?? -- Ask Emily about this  
    keyword_new = '_'.join(token_list)
    keyword_new = keyword_new.strip('_')
    
'''
    
def createTermDictionaryFromAbstracts (jsonfile, output_dict_model, output_processing_rules_model, min_term_occur):
    
    import ocio.textmining.extraction as terms
    import pickle
    import json
    import codecs
    import re
    from gensim.parsing.preprocessing import STOPWORDS
    
    print ("Training using file: "+jsonfile+" with minimum term threshold:"+str(min_term_occur))
    
    print (" * Parsing chandra abstracts file")
    
    with codecs.open(jsonfile,'r',encoding='utf-8') as f:
        chandra_data = json.load(f)

    
    # initialize processing rules from expected patterns
    processing_rules = dict( chandra_token_repl_patterns, **format_token_replacement_patterns) 

    # process our corpus
    corpus = []
    for i in range((len(chandra_data))):
        if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
            
            # grab the raw abstract
            abstract = chandra_data[i]['response']['docs'][0]['abstract']
            
            # process it to pull out sources, changing spaces to underscore so we make
            # sure to capture the term fully
            for pattern in special_token_patterns:
                results = re.findall(pattern, abstract)
                replacement_labels = {}
                if results:
                    for result in results:
                         
                        #clean up XML-ish formatting
                        result = re.sub('\<\/?\w+\>','', result)
                         
                        # store the processing rule for downstream use
                        # replace spaces with underscore so we ensure tokenization
                        processing_rules[result] = result.replace(' ','_')
            
            
            # apply all of the processing rules now 
            for rule in processing_rules:
                abstract = abstract.replace(rule, processing_rules[rule])
                
            corpus.append(abstract)
            
        else:
            pass

    print (" * Writing processing rules model")
    with open(output_processing_rules_model, 'wb+') as f:
        pickle.dump(processing_rules, f)

    print (" * Creating trained model from ADS abstract field")
    dict_model = terms.UnstructuredTextTermExtractor.train(corpus, stop_words=STOPWORDS, stem_terms=True, 
                                                           min_term_count=min_term_occur)
    
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
    ap.add_argument('-mt', '--min_term_threshold', type=int, default=MIN_TERM_OCCUR, help='Minimum number of times term must occur in training to be included in the model dictionary ')
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

    createTermDictionaryFromAbstracts(opts.input, opts.output_dict_model, opts.output_processing_rules_model, opts.min_term_threshold)
    
    
    
