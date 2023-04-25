import pynini as pn


malti2arabi_2char = pn.string_file('mappings/malti2arabi_2char.map').optimize()
arabic2arabic = pn.string_file('mappings/arabic2arabic.map').optimize()
malti2arabi_1char = pn.string_file('mappings/malti2arabi_1char.map').optimize()
shadda = pn.string_file('mappings/shadda.map').optimize()
final_vowels = pn.string_file('mappings/final_vowels.map').optimize()
special = pn.string_file('mappings/special.map').optimize()
everything_else = pn.string_file('mappings/everything_else.map').optimize()
alif_initial = pn.string_file('mappings/alif_initial.map').optimize()
baby_closed_class = pn.string_file('mappings/baby_closed_class.map').optimize()
baby_closed_class_deterministic = pn.string_file('mappings_deterministic/baby_closed_class_deterministic.map').optimize()

sigma_malti = pn.project(malti2arabi_1char,'input')
sigma_arabi = pn.project(arabic2arabic,'output') 

# SIGMA
sigma_in = pn.project(pn.union(malti2arabi_1char,special,arabic2arabic,final_vowels,everything_else),'input')
sigma = pn.project(pn.union(sigma_in,special,final_vowels),'output').optimize()

rwr_first_fsts = pn.union(
    malti2arabi_2char,
    shadda,
    final_vowels,
    alif_initial,
).optimize()

rwr_first = pn.cdrewrite(rwr_first_fsts,"","",sigma.closure())

second_fsts = pn.union(
    malti2arabi_1char,
    arabic2arabic, 
    special,
    everything_else,
).optimize()

translit_fst = (rwr_first @ second_fsts.closure()).optimize()

# deterministic
malti2arabi_det= pn.string_file('mappings_deterministic/malti2arabi_1char_vowels_short.map').optimize()
special_deterministic = pn.string_file('mappings_deterministic/special_deterministic.map').optimize()

diacs = 'ًٌٍَُِّْ'
dediac_cross = pn.string_file('mappings/dediac.map')
dediac = pn.cdrewrite(dediac_cross,'','',sigma.closure())

augmented_closed_class = pn.string_file('mappings/augmented_closed_class.map').optimize()

# words = pn.string_file('../data/arabi_data/tn-maghreb-words.txt').optimize() @ dediac