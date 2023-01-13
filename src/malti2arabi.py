import pynini as pn

# basic map
malti2safebw = pn.string_file('../rules/malti2safebw.cross')

# sigmas
malti_sigma = pn.string_file('../chars/malti.sym')
safebw_sigma = pn.string_file('../chars/safebw.sym')

# shadda rule
shaddas = pn.string_file('../rules/shadda.cross')
shadda_rule_sigma = pn.union(safebw_sigma,'~')
shadda_rule = pn.cdrewrite(shaddas,'','', shadda_rule_sigma.closure()).optimize()

# alif_init rule
alif_inits = pn.string_file('../rules/alif_init.cross')
alif_init_rule = pn.cdrewrite(alif_inits,'[BOS]','', safebw_sigma.closure()).optimize()

# alif_mid rule
alif_mid = pn.cross('ie','A')
alif_mid_rule = pn.cdrewrite(alif_mid,'','', safebw_sigma.closure()).optimize()


def translit(string):
    rules = malti2safebw.closure() @ shadda_rule @ alif_init_rule @ alif_mid_rule
    return  string @ rules.optimize()