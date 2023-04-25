from malti2arabi_fst import *
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import strip_accents_unicode
import kenlm
from transformers import AutoTokenizer
import re

tokenizer = AutoTokenizer.from_pretrained("CAMeL-Lab/bert-base-arabic-camelbert-mix")
wordmodel = kenlm.Model('../data/arabi_data/arabic_lm/aggregated_country/lm/word/tn-maghreb.arpa')
charmodel = kenlm.Model('../data/arabi_data/arabic_lm/aggregated_country/lm/char/tn-maghreb.arpa')


def dediac_fst(text):
    text = text.replace('[','\[').replace(']','\]')
    try:
        return (text @ dediac).string()
    except:
        return np.nan
    

def get_paths(fst,words_only=False):
    paths = list(fst.paths().items())
    if words_only:
        return [x[1] for x in paths]
    else:
        return paths


def apply_translit_fst(tok,backoff_fsts=[baby_closed_class,augmented_closed_class]):
    tok = tok.replace('[','\[').replace(']','\]')
    tok = (f'<BOS>{tok}<EOS>')
    # if type=='det':
    #     return tok @ deterministic_transcriber @ dediac
    if backoff_fsts:
        backoff =  tok @ pn.union(*backoff_fsts).optimize() @ dediac
        if get_paths(backoff):
            return backoff
        else:
            return tok  @ translit_fst @ dediac
    else:
        return tok  @ translit_fst @ dediac

def filter_edge_diacritics(options):
    return [y for y in options if y[0] not in diacs and y[-1] not in diacs]

def translit_deterministic(lowered,backoffs=[]):
    lowered = lowered.replace('[','\[').replace(']','\]') 
    if backoffs:
        backofflowered = f'<BOS>{lowered}<EOS>'
        backoff = backofflowered @ pn.union(*backoffs).optimize() @ dediac
        if len(get_paths(backoff))==1:
            return backoff.string()
        elif len(get_paths(backoff))>1:
            print('error: fst is NOT deterministic on:',lowered)
            return '#na'
    # default
    try:
        maptranslit = (lowered @ pn.union(malti2arabi_det,special_deterministic,everything_else).closure().optimize() @ dediac).string()
        return maptranslit
    except:
        print('error detfst on:',lowered)
        return '#na'
            

def translit_word(lowered_tok,backoffs): #select on merged but return unmerged

    tok_fst = apply_translit_fst(lowered_tok,backoffs)
    translit_toks = get_paths(tok_fst,words_only=True) 
    if not translit_toks:
        print('error non-detfst on:',lowered_tok)
        return ['#na']
    try:
        translit_toks = filter_edge_diacritics(translit_toks) 
    except:
        print('err filtering diacs',translit_toks,lowered_tok)
    
    translit_toks = [ dediac_fst(x) for x in translit_toks]  # dediacritize
    return translit_toks



words_df= pd.read_fwf('../data/arabi_data/tn-maghreb-words.txt',header=None).rename(columns={0:'words'})
words_df['dediac'] = pd.Series([dediac_fst(x) for x in words_df['words']])

langmodelset =  set(words_df['dediac'])

def count_subtokens(text, tokenizer):
    return tokenizer(text, add_special_tokens=False, return_length=True)["length"]

def strip_plus(x):
    if x == "+":
        return x
    else:
        return x.rstrip("+")
    
def dediacritise_non_malti_accents(text: str, diacritics_to_keep: str = "ċġħżĊĠĦŻ") -> str:
    """
    Removes diacritics from the text.
    This preserves any special symbols which aren't diacritised characters.
    Args:
        text: The text to dediacritise.
        diacritics_to_keep: Optional diacritics to keep in the text.
    Returns:
        The dediacritised text.
    """

    normalised_text = strip_accents_unicode(text)
    if diacritics_to_keep:
        for character in re.finditer(rf"[{diacritics_to_keep}]", text):
            normalised_text = normalised_text[:character.start()] \
                              + character.group() \
                              + normalised_text[character.end():]
    return normalised_text


def translit_and_rank_options(word,backoffs,name='translit',fsttype='non-det'):
    normalized = dediacritise_non_malti_accents(word)
    lowered = normalized.lower()
    translit_dict = {
        'word_raw':word,
        'word_normalized':lowered,
        }
    
    if fsttype == 'det':
        translit = [translit_deterministic(lowered,backoffs)]
    elif fsttype == 'non-det':
        translit = translit_word(lowered,backoffs)
    else:
        raise Exception('wrong fsttype')

    translit_dict[name] = translit
    translit_dict['translit'] = translit # keep this, in order to merge later
    translit_dict['translit_stripped'] = [strip_plus(x) for x in translit]
    translit_dict['wordmodel_score'] = [wordmodel.score(x) for x in translit_dict['translit_stripped']]
    translit_dict['charmodel_score'] = [charmodel.score(' '.join(x)) for x in translit_dict['translit_stripped'] ]
    translit_dict['capitalized'] = word[0].isupper() # TODO: what about letter after sink as in 'L-Innu', does it matter?
    translit_dict['in_langmodel'] = [x in langmodelset for x in translit_dict['translit_stripped']]
    translit_dict['subtokens'] = count_subtokens(translit_dict['translit_stripped'], tokenizer)
    # translit_dict['subtokens_lowest_ties'] = sum(np.array(translit_dict['subtokens']) == min(translit_dict['subtokens']))

    return translit_dict


def generate_table(word):
    det = translit_and_rank_options(word,name='det',fsttype='det',backoffs=[])    
    det_smallcc = translit_and_rank_options(word,name='det_smallcc',fsttype='det', backoffs=[baby_closed_class_deterministic])    
    det_fullcc = translit_and_rank_options(word,name='det_fullcc',fsttype='det', backoffs=[baby_closed_class_deterministic,augmented_closed_class])    
    nondet = translit_and_rank_options(word,name='nondet',fsttype='non-det',backoffs=[])
    nondet_smallcc = translit_and_rank_options(word,name='nondet_smallcc',fsttype='non-det',backoffs=[baby_closed_class])
    nondet_fullcc = translit_and_rank_options(word,name='nondet_fullcc',fsttype='non-det',backoffs=[baby_closed_class,augmented_closed_class])
    det['freq'] = np.nan
    det_smallcc['freq'] = np.nan
    det_fullcc['freq'] = np.nan
    nondet['freq'] = np.nan
    nondet_smallcc['freq'] = np.nan
    nondet_fullcc['freq'] = np.nan
    
    return (det,det_smallcc,det_fullcc,nondet,nondet_smallcc,nondet_fullcc,)
   
# det,det_smallcc,det_fullcc,nondet,nondet_smallcc,nondet_fullcc = generate_table(word)
# det = pd.DataFrame(det)
# det_smallcc = pd.DataFrame(det_smallcc)
# det_fullcc = pd.DataFrame(det_fullcc)
# nondet = pd.DataFrame(nondet)
# nondet_smallcc = pd.DataFrame(nondet_smallcc)
# nondet_fullcc = pd.DataFrame(nondet_fullcc)

def merge_multiple(dfs):
    first = dfs[0]
    for df in dfs[1:]:
        first = first.merge(df,how='outer')
    
    return first.sort_values('wordmodel_score',ascending=False)[[
        'word_raw',
        'word_normalized',
        'freq',
        'translit',
        'det',
        'det_smallcc',
        'det_fullcc',
        'nondet',
        'nondet_smallcc',
        'nondet_fullcc',        
        'translit_stripped',
        'wordmodel_score',
        'charmodel_score',
        'capitalized',
        'in_langmodel',
        'subtokens',
        # 'subtokens_lowest_ties',
        ]]

def translit_dataset(word_hist):
    
    detlist = []
    det_smallcclist = []
    det_fullcclist = []
    nondetlist = []
    nondet_smallcclist = []
    nondet_fullcclist = []

    for word,freq in word_hist.values[:]:
        
        det, det_smallcc, det_fullcc, nondet, nondet_smallcc, nondet_fullcc = generate_table(word)
        det['freq'] = freq
        det_smallcc['freq'] = freq
        det_fullcc['freq'] = freq
        nondet['freq'] = freq
        nondet_smallcc['freq'] = freq
        nondet_fullcc    ['freq'] = freq
        
        detlist.append(det)
        det_smallcclist.append(det_smallcc)
        det_fullcclist.append(det_fullcc)
        nondetlist.append(nondet)
        nondet_smallcclist.append(nondet_smallcc)
        nondet_fullcclist.append(nondet_fullcc)
        
    
    detlistdf = pd.DataFrame(detlist).explode(['translit','det','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])
    det_smallcclistdf = pd.DataFrame(det_smallcclist).explode(['translit','det_smallcc','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])
    det_fullcclistdf = pd.DataFrame(det_fullcclist).explode(['translit','det_fullcc','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])
    nondetlistdf = pd.DataFrame(nondetlist).explode(['translit','nondet','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])
    nondet_smallcclistdf = pd.DataFrame(nondet_smallcclist).explode(['translit','nondet_smallcc','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])
    nondet_fullcclistdf = pd.DataFrame(nondet_fullcclist).explode(['translit','nondet_fullcc','translit_stripped','wordmodel_score','charmodel_score','in_langmodel','subtokens'])

    return merge_multiple(dfs=
                          [
detlistdf,
det_smallcclistdf,
det_fullcclistdf,
nondetlistdf,
nondet_smallcclistdf,
nondet_fullcclistdf,
                          ]
                          )