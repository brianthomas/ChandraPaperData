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

'''
    # add underscore to preserve spacing?? -- Ask Emily about this  
    keyword_new = '_'.join(token_list)
    keyword_new = keyword_new.strip('_')
'''

import ocio.textmining.extraction as ote
import logging
logging.basicConfig(level=logging.DEBUG)

class EnglishStemmer (ote.StemmingTool):
    
    def stem_tokens(self, token_list):
        from nltk.stem import SnowballStemmer

        stemmer = SnowballStemmer('english')

        for i in range(len(token_list)):
            # IF its not an acronym, lets stem it
            if token_list[i] != token_list[i].upper():
                token_list[i] = stemmer.stem(token_list[i])
         
        return token_list

    def __init__(self): pass
    
class AbstractTextProcessor (ote.ProcessTextTool):
    
    # Rules for processing tokens which we may miss with ordinary
    # processing engine. Rules which match will cause all whitespace
    # to be changed into underscores so that the words will be picked
    # up as a group 
    _Special_Token_Patterns = ['\<ASTROBJ\>[\w|\s|\.|\-|\+]+\<\/ASTROBJ\>', 'NGC\s+\d+', ]
    
    # some common formatting patterns we need to clean out
    _Format_Token_Replacement_Patterns = { ':': '', '-': ' ', '[': '', ']': '',  '(': '',
                                          ')': '', '\'': '', '=': '', '&': 'and', '\\': '',
                                          '<ASTROBJ>' : '', '</ASTROBJ>' : '', 
                                          '<SUP>' : '', '</SUP>' : '', 
                                          '~' : '',
                                        } 
    
    # some replacement patterns germane to just Chandra data
    # includes some particular misspellings and duplications
    _Chandra_Token_Repl_Patterns = { 'H II': 'HII', 'h\s{0,1}ii': 'HII', 'balck': 'black', 
                                    'intergalacic': 'intergalactic', 'submillimetre': 'submillimeter', 
                                    'centre': 'center', 'agn': 'AGN', 'cd': 'CD', 'disc': 'disk'
                                  }
    
    @staticmethod
    def process (abstract):
        import re
        
        # initialize processing rules from expected patterns
        processing_rules = dict( AbstractTextProcessor._Chandra_Token_Repl_Patterns, 
                                 **AbstractTextProcessor._Format_Token_Replacement_Patterns) 
    
        # process it to pull out sources, changing spaces to underscore so we make
        # sure to capture the term fully
        for pattern in AbstractTextProcessor._Special_Token_Patterns:
            results = re.findall(pattern, abstract)
            replacement_labels = {}
            if results:
                for result in results:
                     
                    #clean up XML-ish formatting
                    result = re.sub('\<\/?\w+\>', '', result)
                     
                    # store the processing rule for downstream use
                    # replace spaces with underscore so we ensure tokenization
                    #processing_rules[result] = result.replace(' ','_')
                    abstract = abstract.replace(result, result.replace(' ','_'))
        
        # apply all of the processing rules now 
        for rule in processing_rules:
            abstract = abstract.replace(rule, processing_rules[rule])
            
        # finally, trim leading and trailing whitespace
        # and return
        return abstract.strip()
        
    def __init__(self): pass
    

def createTermDictionaryFromAbstracts (jsonfile, output_dict_model, min_term_occur):
    
    import pickle
    import json
    import codecs
    from gensim.parsing.preprocessing import STOPWORDS
    
    print ("Training using file: "+jsonfile+" with minimum term threshold:"+str(min_term_occur))
    
    print (" * Parsing chandra abstracts file")
    
    with codecs.open(jsonfile,'r',encoding='utf-8') as f:
        chandra_data = json.load(f)

    # process our corpus
    corpus = []
    for i in range((len(chandra_data))):
        if chandra_data[i]['response']['docs'] != [] and 'abstract' in chandra_data[i]['response']['docs'][0]:
            
            # grab the raw abstract
            abstract = chandra_data[i]['response']['docs'][0]['abstract']
            
            # collect
            corpus.append(abstract)
            
        else:
            pass

    print (" * Creating trained model from ADS abstract field")
    dict_model = ote.UnstructuredTextTermExtractor.train( corpus, stop_words=STOPWORDS, 
                                                          preprocess_text_tool=AbstractTextProcessor(),
                                                          stemming_tool=EnglishStemmer(),
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
    
    createTermDictionaryFromAbstracts(opts.input, opts.output_dict_model, opts.min_term_threshold)
    
    
    
