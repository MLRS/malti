import pynini as pn
from src.utils import safebw2ar,dediac
from random import randint
import re

# print() # toggle this to refresh tables on jupyterlab


def read_map_file(mapfile):
    """_summary_

    Args:
        mapfile (str): custom tsv file with mappings (see googlesheets)

    Returns:
        lefttable (pynini.SymbolTable): left symbol table
        righttable (pynini.SymbolTable): right symbol table
        contextual (list): handle init (^) and final ($) symbols
        left_sigma (pynini.Fst): left alphabet
        right_sigma (pynini.Fst): right alphabet
    """
    dictfile = mapfile.replace('.tsv','.dict') # file name for the dictfile that will be generated
   
    leftsymbols = set()
    rightsymbols = set()
    contextual = set()
    with open(mapfile,'r') as m:
        with open(dictfile,'w') as d:
            for line in m.readlines():
                if '[BOS]' in line  or '[EOS]' in line:
                    pass
                else:
            
                    dictline = re.sub(r'([^\t]+)\t([^\t]+)\t\n?$',r'\1\t\2\n',line)
                    d.write(dictline)
                line = line.strip('\n')
                trips = line.split('\t')
                weight = None
                if len(trips)==3:
                    leftpattern,rightpattern,weight = line.strip('\n').split('\t')
                    together = (leftpattern,rightpattern,weight)
                elif len(trips)==2:
                    leftpattern,rightpattern = line.strip('\n').split('\t')
                    together = (leftpattern,rightpattern)
                else:
                    raise Exception('no weight')
                
                    
                for symbol in leftpattern.split():
                    if symbol=='[BOS]' or symbol=='[EOS]':
                        contextual.add(together)
                    else:
                        leftsymbols.add(symbol)
                
                for symbol in rightpattern.split():
                    rightsymbols.add(symbol)
    
    
    lefttable = pn.SymbolTable()
    lefttable.add_symbol("<eps>", 0)
    righttable = pn.SymbolTable()
    righttable.add_symbol("<eps>", 0)
    
    
    try:
        for symbol in leftsymbols:
            lefttable.add_symbol(symbol,ord(symbol)+1000)    
        for symbol in rightsymbols:
            righttable.add_symbol(symbol,ord(symbol))    
    except Exception as e:
        print(symbol,e)
        # raise Exception(e)
    if weight:
        left_sigma = pn.union(*[pn.accep(x,token_type=lefttable, weight=weight) for x in leftsymbols]).optimize()
        right_sigma = pn.union(*[pn.accep(x,token_type=righttable, weight=weight) for x in rightsymbols]).optimize()
    else:    
        left_sigma = pn.union(*[pn.accep(x,token_type=lefttable) for x in leftsymbols]).optimize()
        right_sigma = pn.union(*[pn.accep(x,token_type=righttable) for x in rightsymbols]).optimize()
        
    return lefttable,righttable,contextual,left_sigma,right_sigma

MALTI_ORTHO, ARABI_ORTHO, CONTEXTUAL, MALTI_SIGMA, ARABI_SIGMA = read_map_file('malti2arabi.tsv')

MALTI2ARABI = pn.string_file('malti2arabi.dict',input_token_type=MALTI_ORTHO,output_token_type=ARABI_ORTHO).optimize()

def create_cdrewrites(contextual,in_ortho=MALTI_ORTHO,in_sigma=MALTI_SIGMA,out_ortho=ARABI_ORTHO):    
    rewrites = []
    newmaps = []    
    for together in contextual:        
        leftpattern,rightpattern,weight = together
        if weight:
            weight = int(weight)
        elif weight == '':                  
            weight = 0
        else:
            print(leftpattern,rightpattern)
            raise Exception('bad tsv map with [BOS]/[EOS] symbols')        
        
        rint = in_ortho.available_key()
        rstr = chr(rint)
        
        in_ortho.add_symbol(rstr,rint)        
        in_sigma = pn.union(in_sigma, pn.accep(rstr,token_type=in_ortho)).optimize()
        try:
            if '[BOS] ' in leftpattern and ' [EOS]' in leftpattern:
                leftpattern = leftpattern.replace('[BOS] ','')
                leftpattern = leftpattern.replace(' [EOS]','')
                rule = pn.cross(pn.accep(leftpattern,token_type=in_ortho),pn.accep(rstr,token_type=in_ortho))
                rewrite = pn.cdrewrite(rule,"[BOS]","[EOS]",in_sigma.closure())
                newmap = pn.cross(pn.accep(rstr,token_type=in_ortho,weight=weight),pn.accep(rightpattern,token_type=out_ortho))
            elif '[BOS] ' in leftpattern:
                leftpattern = leftpattern.replace('[BOS] ','')
                rule = pn.cross(pn.accep(leftpattern,token_type=in_ortho),pn.accep(rstr,token_type=in_ortho))
                rewrite = pn.cdrewrite(rule,"[BOS]","",in_sigma.closure())
                newmap = pn.cross(pn.accep(rstr,token_type=in_ortho,weight=weight),pn.accep(rightpattern,token_type=out_ortho))
            elif ' [EOS]' in leftpattern:
                leftpattern = leftpattern.replace(' [EOS]','')
                rule = pn.cross(pn.accep(leftpattern,token_type=in_ortho),pn.accep(rstr,token_type=in_ortho))
                rewrite = pn.cdrewrite(rule,"","[EOS]",in_sigma.closure())
                newmap = pn.cross(pn.accep(rstr,token_type=in_ortho,weight=weight),pn.accep(rightpattern,token_type=out_ortho))
        except:
            # return in_sigma
            raise Exception('yoo')    
        rewrites.append(rewrite)
        newmaps.append(newmap)
        
    
    return pn.union(*rewrites).optimize(), pn.union(*newmaps).optimize()


REWRITES, NEWMAPS = create_cdrewrites(CONTEXTUAL)

    

def malti(astring,set_symbols=True):
    if set_symbols:        
        return pn.accep(' '.join(astring),token_type=MALTI_ORTHO).set_input_symbols(MALTI_ORTHO)
    else:
        return pn.accep(' '.join(astring),token_type=MALTI_ORTHO)

def arabi(astring,set_symbols=True):
    if set_symbols:        
        return pn.accep(' '.join(astring),token_type=ARABI_ORTHO).set_input_symbols(ARABI_ORTHO)
    else:
        return pn.accep(' '.join(astring),token_type=ARABI_ORTHO)

def translit(astring,in_ortho=MALTI_ORTHO,out_ortho=ARABI_ORTHO):
    astring = astring.lower()
    if in_ortho==MALTI_ORTHO:
        infsa = malti(astring) @ REWRITES 
        mapfst = pn.union(NEWMAPS,MALTI2ARABI).closure()
        return ( infsa @ mapfst  ).optimize().set_input_symbols(MALTI_ORTHO).set_output_symbols(ARABI_ORTHO)
   
    # elif direction == 'arabi2malti':
    #     return ((pn.accep(string,token_type=arabi_ortho) ) @ (MALTI2ARABI.closure() @ REWRITES).invert()).optimize().set_input_symbols(arabi_ortho).set_output_symbols(malti_ortho)

def translit_sentence(sent,remove_diacs=False):
    sent = sent.strip().replace('\n','')
    # if '\n' in sent:
    
    if '\n' in sent:
        raise Exception('nooline')
    translit_sent = []
    translit_sent_ar = []
    for tok in sent.split():
        try:    
            translit_bw = get_paths(translit(tok))[0][1].replace(' ','')
            translit_ar = get_paths(translit(tok))[0][3].replace(' ','')
            if remove_diacs:
                translit_bw = dediac.dediac_bw(translit_bw)
                translit_ar = dediac.dediac_ar(translit_ar)                
            translit_sent.append(translit_bw)
            translit_sent_ar.append(translit_ar)
        except:
            translit_sent.append(f'bad@{tok}')
            translit_sent_ar.append(f'bad@{tok}')
                
    return ' '.join(translit_sent),' '.join(translit_sent_ar)


def get_paths(fst,in_ortho=MALTI_ORTHO,out_ortho=ARABI_ORTHO,target=None):
    path_items = list(fst.paths(input_token_type=in_ortho,output_token_type=out_ortho).items())
    path_items = [list(x) + [safebw2ar(x[1]).replace(' ','')] for x in path_items]

    if target:
        if not list(filter(lambda x: x[1].replace(' ','')==target,path_items)):
            print('target not in paths'.upper())
    
    return sorted(path_items,key=lambda x: int(x[2].to_string()))
