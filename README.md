# Maltese Text Processing

A set of processing pipelines for Maltese mapping tokens to Arabic transliterations, translations, or to original token.

This repository used to contain code for [Exploring the Impact of Transliteration on NLP Performance: Treating Maltese as an Arabic Dialect](https://aclanthology.org/2023.cawl-1.4/).
For a snapshot of the code for replication purposes refer to the [`2023.cawl-1.4`](https://github.com/MLRS/malti/tree/2023.cawl-1.4) tag.

The current code contains improvements as detailed in [Cross-Lingual Transfer from Related Languages: Treating Low-Resource Maltese as Multilingual Code-Switching](https://aclanthology.org/2024.eacl-long.61/).
A summary of changes from the previous work:
- Transliteration character mapping updates: added `t`→`ث`, digits, & other miscellaneous symbols.
  Also fixed a bug which wasn't generating `ظ`/`ث`/`أ` characters.
- [Word Etymology data](src/etymology_data/annotations.tsv).
- Etymology Classification [code](src/etymology_classification.py) & [classifier](src/etymology_data/model.pickle).
- [Pre-computed word-level translations](src/translations) using [Google Translate](https://translate.google.com/).
- Updated the transliteration pipeline to allow for translations, passing as is, & mixing decisions using the etymology classifier.

## Usage

### Installation

In a virtual environment install the dependencies:

```shell
pip install -r requirements.txt
```

_Note that this might not work on Windows & might have to use [WSL](https://learn.microsoft.com/en-us/windows/wsl/)._

The word/character ranking models can be obtained from: https://github.com/CAMeL-Lab/HierarchicalArabicDialectID.
The sub-tokens count model is a reference to tokenizers compatible with [`transformers`](https://github.com/huggingface/transformers).

### Command line

A [script](src/process.py) intended to process entire datasets in one pass.
Execute `python process.py -h` to access the documentation.

<details>
<summary>Transliteration (X<sub>ara</sub>)</summary>

To perform transliteration, specify the `transliterate` parameter as well as any other additional parameters:

```shell
python process.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --transliterate \
  --rankers word_model_score character_model_score \
  --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
  --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map
```

This performs the T<sub>ara</sub> pipeline, which is transliteration using the full token mappings & the non-deterministic character mappings with Tunisian word model score ranking.
Refer to [transliterate.sh](src/transliterate.sh) which transliterates a given dataset in all configurations from [Exploring the Impact of Transliteration on NLP Performance: Treating Maltese as an Arabic Dialect](https://aclanthology.org/2023.cawl-1.4/).
</details>

<details>
<summary>(Word) Translation (T<sub>*</sub>)</summary>

To perform word-level translation, specify the `translate` parameter.
For instance, to apply the T<sub>en</sub> pipeline (English translation):

```shell
python process.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --translate \
  --translation_system "mt-en"
```

where `translation_system` corresponds to one of the [translation files](src/translations).
</details>

<details>
<summary>Partial Transliteration (X<sub>ara</sub>/P)</summary>

When specifying etymology tags with the `transliterate`/`translate` parameter, partial transliteration/translation is performed.
This uses an `etymology_model` to predict the etymology of the word before applying the action specified.
A "pass" (leaving the token as is) is performed for any token with an etymology tag unspecified in these parameters.

```shell
python process.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --etymology_model="etymology_data/model.pickle" \
  --transliterate "Arabic" \
  --rankers word_model_score character_model_score \
  --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
  --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map
```
</details>

<details>
<summary>Transliteration & Translation Mixing (X<sub>ara</sub>/T<sub>*</sub>)</summary>

Specify the etymology tags (corresponding to those predicted by the `etymology_model`) with the `transliterate` & `translate` parameters, mixes transliteration with translation at the token level.
For instance, to apply the X<sub>ara</sub>/T<sub>eng</sub> pipeline:

```shell
python process.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --etymology_model="etymology_data/model.pickle" \
  --transliterate "Arabic" \
  --translate "Non-Arabic" "Name" \
  --rankers word_model_score character_model_score \
  --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
  --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map \
  --translation_system "mt-en"
```

Multiple translation systems can also be specified, for each etymology tag specified in the `translate` argument.
For instance, to apply the X<sub>ara</sub>/T<sub>ara</sub> pipeline:

```shell
python process.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --etymology_model="etymology_data/model.pickle" \
  --transliterate "Arabic" "Symbol" \
  --translate "Non-Arabic" "Code-Switching" "Name" \
  --rankers word_model_score character_model_score \
  --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
  --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map \
  --translation_system "mt-ar" "en-ar" "mt-ar"
```
</details>

### Python Code

Refer to the [demo notebook](src/demo.ipynb) for examples.

## Citations

The latest version of this work is published under:
```bibtex
@misc{micallef-etal-2024-maltese-etymology,
    title = "Cross-Lingual Transfer from Related Languages: Treating Low-Resource {M}altese as Multilingual Code-Switching",
    author = "Micallef, Kurt  and
              Habash, Nizar  and
              Borg, Claudia  and
              Eryani, Fadhl  and
              Bouamor, Houda",
    editor = "Graham, Yvette  and
              Purver, Matthew",
    booktitle = "Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = mar,
    year = "2024",
    address = "St. Julian{'}s, Malta",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.eacl-long.61",
    pages = "1014--1025",
}
```

The original transliteration system was published under:
```bibtex
@inproceedings{micallef-etal-2023-maltese-transliteration,
    title = "Exploring the Impact of Transliteration on {NLP} Performance: Treating {M}altese as an {A}rabic Dialect",
    author = "Micallef, Kurt  and
              Eryani, Fadhl  and
              Habash, Nizar  and
              Bouamor, Houda  and
              Borg, Claudia",
    editor = "Gorman, Kyle  and
              Sproat, Richard  and
              Roark, Brian",
    booktitle = "Proceedings of the Workshop on Computation and Written Language (CAWL 2023)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.cawl-1.4",
    doi = "10.18653/v1/2023.cawl-1.4",
    pages = "22--32",
}
```

For fine-tuning instructions & dataset references see: https://github.com/MLRS/BERTu/tree/2022.deeplo-1.10/finetune
