import pynini as pn

# basic map
malti2arabi = pn.string_file('../rules/malti2arabi.cross')

# sigmas
malti_sigma = pn.string_file('../chars/malti.sym')
arabi_sigma = pn.string_file('../chars/arabi.sym')
sigma_star = pn.union(malti_sigma, arabi_sigma).closure()

# shadda rule
shaddas = pn.string_file('../rules/shadda.cross')
malti2arabi = pn.union(malti2arabi,pn.project(shaddas,'output'))
shadda_rule = pn.cdrewrite(shaddas,'','', sigma_star).optimize()

# alif_init rule
alif_inits = pn.string_file('../rules/alif_init.cross')
malti2arabi = pn.union(malti2arabi,'ا')
alif_init_rule = pn.cdrewrite(alif_inits,'[BOS]','', sigma_star).optimize()

# alif_mid rule
alif_mid = pn.cross('ie','ا')
malti2arabi = pn.union(malti2arabi,'ا')
alif_mid_rule = pn.cdrewrite(alif_mid,'','', sigma_star).optimize()


def translit(string):
    rules =  shadda_rule @ alif_init_rule @ alif_mid_rule 
    return  (string @ rules.optimize() @  malti2arabi.closure() ).optimize()