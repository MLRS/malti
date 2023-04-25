import pyconll
import pandas as pd

def merge_conllu(dataset):
    dev = pyconll.load_from_file(f'../data/malti_data/{dataset}/dev.conllu')
    train = pyconll.load_from_file(f'../data/malti_data/{dataset}/train.conllu')
    test = pyconll.load_from_file(f'../data/malti_data/{dataset}/test.conllu')
    allsets = dev._sentences + train._sentences + test._sentences

    print(f'# of sents in {dataset}',len(allsets))

    keys = ["id","form","lemma","upos","xpos","feats","head","deprel","deps","misc"]

    sents = []
    for sent in allsets:
        # toks = [pd.Series({'sent_id':sent.id,'sent':sent.text})]
        toks = []
        for tok in sent:
            tokdict = {'sent_id':sent.id}
            tokdict.update( {k:tok.__getattribute__(k) for k in keys})
            toks.append (pd.Series(tokdict))
        sents.append(pd.DataFrame(toks))
    df = pd.concat(sents)    
    # word_hist
    
    word_hist = df['form'].dropna().value_counts().reset_index()
    # word_hist.to_clipboard()
    print(f'# of words (uniq) in {dataset}',len(word_hist))
    # # char hist
    char_hist = pd.DataFrame([y for x in df['form'].dropna().str.casefold() for y in x]).value_counts()
    # char_hist.to_clipboard()
    print(f'# of chars (uniq) {dataset}',len(char_hist))
    return df

def merge_datasets(datasets=['MLRS POS','Sentiment Analysis','MAPA','mt_mudt-ud']):
    loaded_datasets = []
    for d in datasets:
        merged = merge_conllu(d)
        loaded_datasets.append(merged)

    return pd.concat(loaded_datasets)


def get_char_hist(alldata):
    return pd.Series([' '.join(x) for x in alldata['form'].values]).str.lower().str.split().explode().value_counts()


def get_alldata_hist(alldata):
    return alldata['form'].dropna().value_counts().reset_index()
