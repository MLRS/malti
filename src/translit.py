import logging
import re

import numpy as np
from sklearn.feature_extraction.text import strip_accents_unicode

from malti2arabi_fst import *
from token_rankers import RandomRanker, TokenRanker

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


def apply_translit_fst_nondet(tok,backoff_fsts):
    tok = tok.replace('[','\[').replace(']','\]')
    tok = (f'<BOS>{tok}<EOS>')
    if backoff_fsts:
        backoff =  tok @ pn.union(*backoff_fsts).optimize() @ dediac
        if get_paths(backoff):
            return backoff
        else:
            return tok  @ translit_fst_nondet @ dediac
    else:
        return tok  @ translit_fst_nondet @ dediac
    # 
def apply_translit_fst_det(tok,backoff_fsts):
    tok = tok.replace('[','\[').replace(']','\]')
    tok = (f'<BOS>{tok}<EOS>')
    if backoff_fsts:
        backoff =  tok @ pn.union(*backoff_fsts).optimize() @ dediac
        if get_paths(backoff):
            return backoff
        else:
            return tok  @ translit_fst_det @ dediac
    else:
        return tok  @ translit_fst_det @ dediac

def filter_edge_diacritics(options):
    return [y for y in options if y[0] not in diacs and y[-1] not in diacs]

def translit_word(lowered_tok,backoffs,is_non_deterministic): #select on merged but return unmerged
    if is_non_deterministic:
        tok_fst = apply_translit_fst_nondet(lowered_tok,backoffs)
    else:
        tok_fst = apply_translit_fst_det(lowered_tok,backoffs)

    translit_toks = get_paths(tok_fst,words_only=True) 
    if not translit_toks:
        print(f'error is_non_deterministic:{is_non_deterministic}fst on:',lowered_tok)
        return ['#na']
    try:
        translit_toks = filter_edge_diacritics(translit_toks) # TODO: might not apply in current system, check what this does 
    except:
        if not is_non_deterministic=='det':
            pass
        else:
            print('err filtering diacs',translit_toks,lowered_tok)
    
    translit_toks = [ dediac_fst(x) for x in translit_toks]  # dediacritize
    return translit_toks


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
# 


def translit_and_rank_options(token: str,
                              token_mappings: list[str] = None,
                              token_rankers: list[TokenRanker] = None):
    if token_rankers is None:
        token_rankers = []
    if token_mappings is None:
        token_mappings = []

    def choose(alternatives):
        for ranker in token_rankers:
            alternatives = ranker.filter_best(alternatives)
            if len(alternatives) == 1:
                # no need to filter further
                break
        if len(alternatives) > 1:
            # unresolved ties
            logging.warning(f'Choosing randomly for token "{token}"')
            alternatives = RandomRanker().filter_best(alternatives)
        return alternatives[0]

    normalized = dediacritise_non_malti_accents(token)
    lowered = normalized.lower()

    backoffs = [get_token_mappings(path) for path in token_mappings]
    
    alternatives = translit_word(lowered, backoffs, token_rankers is not None)

    alternatives = [strip_plus(transliterated_token) for transliterated_token in alternatives]

    if len(alternatives) == 0:
        logging.warning(f'No valid alternatives for token "{token}", choosing same token')
        transliterated_token = token
    else:
        transliterated_token = choose(alternatives) if token_rankers else alternatives[0]

    return transliterated_token
