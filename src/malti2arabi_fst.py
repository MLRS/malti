import pynini as pn
# 
TOKEN_MAPPINGS = {}


def get_token_mappings(path):
    if path not in TOKEN_MAPPINGS:
        TOKEN_MAPPINGS[path] = pn.string_file(path).optimize()
    return TOKEN_MAPPINGS[path]




malti2arabi_2char_nondet = pn.string_file('mappings/malti2arabi_2char.map').optimize()
malti2arabi_nondet = pn.string_file('mappings/malti2arabi_1char.map').optimize()
shadda_nondet = pn.string_file('mappings/shadda.map').optimize()
final_vowels_nondet = pn.string_file('mappings/final_vowels.map').optimize()
special_nondet = pn.string_file('mappings/special.map').optimize()
alif_initial_nondet = pn.string_file('mappings/alif_initial.map').optimize()


arabic2arabic = pn.string_file('mappings/arabic2arabic.map').optimize()
everything_else = pn.string_file('mappings/everything_else.map').optimize()
alif_initial = pn.string_file('mappings/alif_initial.map').optimize()
sigma_malti = pn.project(malti2arabi_nondet,'input')
sigma_arabi = pn.project(arabic2arabic,'output') 

# SIGMA
sigma_in = pn.project(pn.union(malti2arabi_nondet,special_nondet,arabic2arabic,final_vowels_nondet,everything_else),'input')
sigma = pn.project(pn.union(sigma_in,special_nondet,final_vowels_nondet),'output').optimize()

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
malti2arabi_2char_det = pn.string_file('mappings_deterministic/malti2arabi_2char.map').optimize()
malti2arabi_det= pn.string_file('mappings_deterministic/malti2arabi_1char_vowels_short.map').optimize()
special_det = pn.string_file('mappings_deterministic/special_deterministic.map').optimize()
shadda_det = pn.string_file('mappings_deterministic/shadda.map').optimize()


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
dediac_cross = pn.string_file('mappings/dediac.map')
dediac = pn.cdrewrite(dediac_cross,'','',sigma.closure())

# words = pn.string_file('../data/arabi_data/tn-maghreb-words.txt').optimize() @ dediac