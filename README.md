# Maltese Transliteration

A set of transliteration pipelines for Maltese texts to Arabic, implemented using finite-state machines.
This work first appeared in [Exploring the Impact of Transliteration on NLP Performance: Treating Maltese as an Arabic Dialect](https://aclanthology.org/2023.cawl-1.4/).


## Usage

### Installation

In a virtual environment install the dependencies:

```python
pip install -r requirements.txt
```

_Note that this might not work on Windows & might have to use [WSL](https://learn.microsoft.com/en-us/windows/wsl/)._

The word/character ranking models can be obtained from: https://github.com/CAMeL-Lab/HierarchicalArabicDialectID.
The sub-tokens count model is a reference to tokenizers compatable with [`transformers`](https://github.com/huggingface/transformers).

### Command line

Intended to transliterate entire datasets in one pass.
Execute `python transliterate_cli.py -h` to access the documentation.
The [command line interface](src/transliterate_cli.py) can be used as follows:

```shell
python transliterate_cli.py ${dataset} ${INPUT_PATH} ${OUTPUT_PATH} \
  --rankers word_model_score character_model_score \
  --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
  --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map
```

This transliterates using the full token mappings & the non-deterministic character mappings with Tunisian word model score ranking. 
Refer to [transliterate.sh](src/transliterate.sh) which transliterates a given dataset in all supported pipelines.

### Python Code

To transliterate a sequence of tokens using the full token mappings & the non-deterministic character mappings with Tunisian word model score ranking:

```python
from transliterate import transliterate_sequence
import token_rankers

transliterate_sequence(
    ["Il-", "ġurnata", "t-", "tajba", "!"],
    token_mappings=["token_mappings/small_closed_class.map", "token_mappings/additional_closed_class.map"],
    token_rankers=[
        token_rankers.WordModelScoreRanker("../models/aggregated_country/lm/word/tn-maghreb.arpa"),
        token_rankers.CharacterModelScoreRanker("../models/aggregated_country/lm/char/tn-maghreb.arpa"),
    ]
)
```

For a single token, use `transliterate` instead.

## Citations

Cite this work as follows:
```
@inproceedings{micallef-etal-2023-maltese-transliteration,
    title = "Exploring the Impact of Transliteration on {NLP} Performance for Low-Resource Languages: Treating {M}altese as an {A}rabic Dialect",
    author = "Micallef, Kurt and
              Eryani, Fadhl and
              Habash, Nizar and
              Bouamor, Houda and
              Borg, Claudia",
    booktitle = "Proceedings of the Workshop on Computation and Written Language (CAWL 2023)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.cawl-1.4",
    pages = "22--32",
}
```

For fine-tuning instructions & dataset references see: https://github.com/MLRS/BERTu/tree/2022.deeplo-1.10/finetune
