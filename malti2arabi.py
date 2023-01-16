import pynini as pn

def translit(string):
    rules = (malti2safebw.closure() @ shadda_rule)
    return ( string @ rules.optimize()).rmepsilon()


# basic map
malti2safebw = pn.string_file('rules/malti2safebw.cross')

# sigmas
malti_sigma = pn.string_file('chars/malti.sym')
safebw_sigma = pn.string_file('chars/safebw.sym')

# shadda rule
shaddas = pn.string_file('rules/shadda.cross')
shadda_rule_sigma = pn.union(safebw_sigma,'~')
shadda_rule = pn.cdrewrite(shaddas,'','', shadda_rule_sigma.closure()).optimize()
