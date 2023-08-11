import logging

import pynini as pn

TOKEN_MAPPINGS = {}


def get_token_mappings(path):
    if path not in TOKEN_MAPPINGS:
        TOKEN_MAPPINGS[path] = pn.string_file(path).optimize()
    return TOKEN_MAPPINGS[path]


malti2arabi_2char_nondet = pn.string_file('character_non-deterministic_mappings/malti2arabi_2char.map').optimize()
malti2arabi_nondet = pn.string_file('character_non-deterministic_mappings/malti2arabi_1char.map').optimize()
shadda_nondet = pn.string_file('character_non-deterministic_mappings/shadda.map').optimize()
final_vowels_nondet = pn.string_file('character_non-deterministic_mappings/final_vowels.map').optimize()
special_nondet = pn.string_file('character_non-deterministic_mappings/special.map').optimize()
alif_initial_nondet = pn.string_file('character_non-deterministic_mappings/alif_initial.map').optimize()


arabic2arabic = pn.string_file('character_non-deterministic_mappings/arabic2arabic.map').optimize()
everything_else = pn.string_file('character_non-deterministic_mappings/everything_else.map').optimize()
alif_initial = pn.string_file('character_non-deterministic_mappings/alif_initial.map').optimize()
sigma_malti = pn.project(malti2arabi_nondet,'input')
sigma_arabi = pn.project(arabic2arabic,'output') 

# SIGMA
sigma_in = pn.project(pn.union(malti2arabi_nondet,special_nondet,arabic2arabic,final_vowels_nondet,everything_else),'input')
sigma = pn.project(pn.union(sigma_in,special_nondet,final_vowels_nondet,everything_else),'output').optimize()

rwr_first_fsts_nondet = pn.union(
    malti2arabi_2char_nondet,
    shadda_nondet,
    final_vowels_nondet,
    alif_initial_nondet,
).optimize()

# rwr_first_nondet = pn.cdrewrite(rwr_first_fsts_nondet,"","",sigma.closure(),mode='opt')
rwr_first_nondet = pn.cdrewrite(rwr_first_fsts_nondet,"","",sigma.closure())

second_fsts_nondet = pn.union(
    malti2arabi_nondet,
    special_nondet,
    arabic2arabic, 
    everything_else,
).optimize()

translit_fst_nondet = (rwr_first_nondet @ second_fsts_nondet.closure()).optimize()
# 
# deterministic
malti2arabi_2char_det = pn.string_file('character_deterministic_mappings/malti2arabi_2char.map').optimize()
malti2arabi_det= pn.string_file('character_deterministic_mappings/malti2arabi_1char_vowels_short.map').optimize()
special_det = pn.string_file('character_deterministic_mappings/special_deterministic.map').optimize()
shadda_det = pn.string_file('character_deterministic_mappings/shadda.map').optimize()


rwr_first_fsts_det = pn.union(
    malti2arabi_2char_det,
    shadda_det,
).optimize()

# rwr_first_det = pn.cdrewrite(rwr_first_fsts_det,"","",sigma.closure(),mode='opt')
rwr_first_det = pn.cdrewrite(rwr_first_fsts_det,"","",sigma.closure())

second_fsts_det = pn.union(
    malti2arabi_det,
    special_det,
    arabic2arabic, 
    everything_else,
).optimize()

translit_fst_det = (rwr_first_det @ second_fsts_det.closure()).optimize()

#dediac
diacs = 'ًٌٍَُِّْ'
dediac_cross = pn.string_file('character_non-deterministic_mappings/dediac.map')
dediac = pn.cdrewrite(dediac_cross,'','',sigma.closure())

def dediac_fst(text):
    try:
        return (text @ dediac).string()
    except:
        return text


def get_paths(fst,words_only=False):
    paths = list(fst.paths().items())
    if words_only:
        return [x[1] for x in paths]
    else:
        return paths


def apply_translit_fst_nondet(tok, token_fst):
    if token_fst:
        backoff = tok @ pn.union(*token_fst).optimize() @ dediac
        if get_paths(backoff):
            return backoff
        else:
            return tok  @ translit_fst_nondet @ dediac
    else:
        return tok  @ translit_fst_nondet @ dediac


def apply_translit_fst_det(tok, token_fst):
    if token_fst:
        backoff = tok @ pn.union(*token_fst).optimize() @ dediac
        if get_paths(backoff):
            return backoff
        else:
            return tok  @ translit_fst_det @ dediac
    else:
        return tok  @ translit_fst_det @ dediac


def filter_edge_diacritics(options):
    return [y for y in options if y[0] not in diacs and y[-1] not in diacs]


def translit_word(token, token_mappings, is_non_deterministic):
    def escape_token_characters(token):
        return token.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")

    token_mappings = [get_token_mappings(path) for path in token_mappings or []]

    escaped_token = escape_token_characters(token)
    escaped_token = f"<BOS>{escaped_token}<EOS>"
    if is_non_deterministic:
        tok_fst = apply_translit_fst_nondet(escaped_token, token_mappings)
    else:
        tok_fst = apply_translit_fst_det(escaped_token, token_mappings)

    translit_toks = get_paths(tok_fst,words_only=True)
    if not translit_toks:
        logging.warning(f'No valid alternatives for token "{token}", falling-back to original token.')
        return [token]
    try:
        translit_toks = filter_edge_diacritics(translit_toks)  # TODO: might not apply in current system, check what this does
    except:
        if not is_non_deterministic=='det':
            pass
        else:
            logging.warning("Encountered an error while filtering diacritics", translit_toks, escaped_token)

    translit_toks = [dediac_fst(escape_token_characters(x)) for x in translit_toks]
    return translit_toks
