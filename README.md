# Maltese Transliteration

To transliterate Maltese you can:
- Use the [command line interface](src/transliterate_cli.py):
  ```shell
  python transliterate_cli.py ${dataset} \
    ${INPUT_PATH} \
    ${OUTPUT_PATH} \
    --rankers word_model_score character_model_score \
    --ranker_models "../models/aggregated_country/lm/word/tn-maghreb.arpa" "../models/aggregated_country/lm/char/tn-maghreb.arpa" \
    --token_mappings mappings/small_closed_class.map mappings/additional_closed_class.map
  ```
  Execute `python transliterate_cli.py -h` to access the documentation.
  Alternatively, refer to [transliterate.sh](src/transliterate.sh) which transliterates a given dataset in all supported pipelines.
- Through [Python code](src/transliterate.py):
  ```python
  from transliterate import transliterate_sequence
  import token_rankers
  
  transliterate_sequence(
    ["Il-", "ġurnata", "t-", "tajba", "!"],
    ["token_mappings/small_closed_class.map", "token_mappings/additional_closed_class.map"],
    [
        token_rankers.WordModelScoreRanker("../models/aggregated_country/lm/word/tn-maghreb.arpa"),
        token_rankers.CharacterModelScoreRanker("../models/aggregated_country/lm/char/tn-maghreb.arpa"),
    ]
  )
  ```

to run pynini locally (tried on mac), I could only do it using conda

```
conda create -n maltifst python=3.9
conda activate maltifst
conda install pynini
pip install -r requirements.txt

```
# malti_arabi_fst

malti datasets ![link](https://drive.google.com/drive/folders/1f4clDAtCKoCGHxuvqbiF5yNxFItLUXo1)

arabic language models ![link](https://drive.google.com/drive/folders/1-_uZnl8LamZO9RPYguJJOywJTvJtWUyg?usp=sharing)
<br>
(see https://github.com/CAMeL-Lab/HierarchicalArabicDialectID)