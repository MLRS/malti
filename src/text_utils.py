from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.transliterate import Transliterator
from camel_tools.utils import dediac
from sklearn.feature_extraction.text import strip_accents_unicode
import re


def dediacritise_malti(text, diacritics_to_keep=""):
    """
    Removes diacritics from the text.
    This preserves any special symbols which aren't diacritised characters.

    Args:
        text: The text to dediacritise.
        diacritics_to_keep: Optional diacritics to keep in the text.

    Returns:
        The dediacritised text.
    """

    normalised_sent = strip_accents_unicode(text)
    if diacritics_to_keep:
        for character in re.finditer(rf"[{diacritics_to_keep}]", text):
            normalised_sent = normalised_sent[:character.start()] + character.group() + normalised_sent[character.end():]
    return normalised_sent


# from camel_tools.utils.charsets import SAFEBW_CHARSET

# Instantiate the builtin bw2ar (Buckwalter to Arabic) CharMapper
ar2safebw = CharMapper.builtin_mapper('ar2safebw')
ar2bw = CharMapper.builtin_mapper('ar2bw')
bw2ar = CharMapper.builtin_mapper('bw2ar')
safebw2ar = CharMapper.builtin_mapper('safebw2ar')

# Instantiate Transliterator with the bw2ar CharMapper with '@@IGNORE@@' marker (default)
ar2safebw_translit = Transliterator(ar2safebw)
def ar2safebw(ar):   
    # Generate Arabic transliteration from BW
    sentence_safebw = ar2safebw_translit.transliterate(ar, strip_markers=True)

    return ar2safebw_translit.transliterate(ar) #strip_markers=False

ar2bw_translit = Transliterator(ar2bw)
def ar2bw(ar):   
    # Generate Arabic transliteration from BW
    sentence_bw = ar2bw_translit.transliterate(ar, strip_markers=True)

    return ar2bw_translit.transliterate(ar) #strip_markers=False

safebw2ar_translit = Transliterator(safebw2ar)
def safebw2ar(safebw):   
    # Generate Arabic transliteration from BW
    sentence_ar = safebw2ar_translit.transliterate(safebw, strip_markers=True)

    return safebw2ar_translit.transliterate(safebw) #strip_markers=False

bw2ar_translit = Transliterator(bw2ar)
def safebw2ar(bw):   
    # Generate Arabic transliteration from BW
    sentence_ar = bw2ar_translit.transliterate(bw, strip_markers=True)

    return bw2ar_translit.transliterate(bw) #strip_markers=False