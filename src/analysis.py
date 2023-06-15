import numpy as np
import pandas as pd
from malti2arabi_fst import get_token_mappings

from token_rankers import SubTokensCountRanker, WordModelScoreRanker, CharacterModelScoreRanker
from transliterate import dediacritise_non_malti_accents, strip_plus, translit_word,  dediac_fst

SUB_TOKENS_COUNT_RANKER = SubTokensCountRanker("CAMeL-Lab/bert-base-arabic-camelbert-mix")
WORD_MODEL_SCORE_RANKER_TUNIS = WordModelScoreRanker("../data/arabi_data/arabic_lm/aggregated_country/lm/word/tn-maghreb.arpa")
CHARACTER_MODEL_SCORE_RANKER_TUNIS = CharacterModelScoreRanker("../data/arabi_data/arabic_lm/aggregated_country/lm/char/tn-maghreb.arpa")

WORD_MODEL_SCORE_RANKER_MAGHREB = WordModelScoreRanker('../data/arabi_data/arabic_lm/aggregated_region/lm/word/maghreb.arpa')
CHARACTER_MODEL_SCORE_RANKER_MAGHREB = CharacterModelScoreRanker('../data/arabi_data/arabic_lm/aggregated_region/lm/char/maghreb.arpa')

SMALL_CLOSED_CLASS = ["token_mappings/small_closed_class.map"]
FULL_CLOSED_CLASS = [*SMALL_CLOSED_CLASS, "token_mappings/additional_closed_class.map"]


words_df_maghreb= pd.read_fwf('../data/arabi_data/region_maghreb-words.txt',header=None).rename(columns={0:'words'})
words_df_maghreb = words_df_maghreb[~words_df_maghreb['words'].isna()]
words_df_maghreb['dediac'] = pd.Series([dediac_fst(x) for x in words_df_maghreb['words']])

words_df_tunis= pd.read_fwf('../data/arabi_data/country_tn-maghreb-words.txt',header=None).rename(columns={0:'words'})
words_df_tunis = words_df_tunis[~words_df_tunis['words'].isna()]
words_df_tunis['dediac'] = pd.Series([dediac_fst(x) for x in words_df_tunis['words']])


langmodelset_maghreb =  set(words_df_maghreb['dediac'])
langmodelset_tunis =  set(words_df_tunis['dediac'])


def transliterate_and_get_scores(word, token_mappings, name="translit", fsttype="non-det"):
    translit_dict = {
        "word_raw": word,
        "word_normalized": dediacritise_non_malti_accents(word).lower(),
    }

    backoffs = [get_token_mappings(path) for path in token_mappings]
    
    alternatives = translit_word(translit_dict['word_normalized'], backoffs,fsttype == "non-det")

    alternatives = [strip_plus(transliterated_token) for transliterated_token in alternatives]


    translit_dict[name] = alternatives
    translit_dict["translit"] = alternatives  # keep this, in order to merge later
    translit_dict["translit_stripped"] = [strip_plus(x) for x in alternatives]
    translit_dict["subtokens"] = SUB_TOKENS_COUNT_RANKER.score(alternatives)
    translit_dict["wordmodel_tunis_score"] = WORD_MODEL_SCORE_RANKER_TUNIS.score(alternatives)
    translit_dict["wordmodel_maghreb_score"] = WORD_MODEL_SCORE_RANKER_MAGHREB.score(alternatives)
    translit_dict["charmodel_tunis_score"] = CHARACTER_MODEL_SCORE_RANKER_TUNIS.score(alternatives)
    translit_dict["charmodel_maghreb_score"] = CHARACTER_MODEL_SCORE_RANKER_MAGHREB.score(alternatives)
    translit_dict["capitalized"] = any(map(lambda character: character.isupper(), word))
    translit_dict['in_langmodel_tunis'] = [x in langmodelset_tunis for x in translit_dict['translit_stripped']]
    translit_dict['in_langmodel_maghreb'] = [x in langmodelset_maghreb for x in translit_dict['translit_stripped']]

    return translit_dict


def generate_table(word):
    det = transliterate_and_get_scores(word, name='det', fsttype='det', token_mappings=[])
    det_smallcc = transliterate_and_get_scores(word, name='det_smallcc', fsttype='det', token_mappings=SMALL_CLOSED_CLASS)
    det_fullcc = transliterate_and_get_scores(word, name='det_fullcc', fsttype='det', token_mappings=FULL_CLOSED_CLASS)
    nondet = transliterate_and_get_scores(word, name='nondet', fsttype='non-det', token_mappings=[])
    nondet_smallcc = transliterate_and_get_scores(word, name='nondet_smallcc', fsttype='non-det',
                                               token_mappings=SMALL_CLOSED_CLASS)
    nondet_fullcc = transliterate_and_get_scores(word, name='nondet_fullcc', fsttype='non-det',
                                              token_mappings=FULL_CLOSED_CLASS)
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

    return first.sort_values('wordmodel_maghreb_score',ascending=False)[[
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
        'capitalized',
        'wordmodel_tunis_score',
        'charmodel_tunis_score',
        'in_langmodel_tunis',
        'wordmodel_maghreb_score',
        'charmodel_maghreb_score',
        'in_langmodel_maghreb',
        'subtokens',
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


    detlistdf = pd.DataFrame(detlist).explode(['translit','det','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])
    det_smallcclistdf = pd.DataFrame(det_smallcclist).explode(['translit','det_smallcc','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])
    det_fullcclistdf = pd.DataFrame(det_fullcclist).explode(['translit','det_fullcc','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])
    nondetlistdf = pd.DataFrame(nondetlist).explode(['translit','nondet','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])
    nondet_smallcclistdf = pd.DataFrame(nondet_smallcclist).explode(['translit','nondet_smallcc','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])
    nondet_fullcclistdf = pd.DataFrame(nondet_fullcclist).explode(['translit','nondet_fullcc','translit_stripped','wordmodel_tunis_score','wordmodel_maghreb_score','charmodel_tunis_score','charmodel_maghreb_score','in_langmodel_tunis','in_langmodel_maghreb','subtokens'])

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
