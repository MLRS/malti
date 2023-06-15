readonly DATA_PATH="../data"
readonly MODELS_PATH="../models"
readonly OUTPUT_PATH="../data/transliterations"

dataset=$1
if [ ${dataset} == "universal_dependencies" ];
then
    path="MUDT"
elif [ ${dataset} == "mlrs_pos" ];
then
    path="MLRS POS Gold"
elif [ ${dataset} == "mapa" ];
then
    path="MAPA"
elif [ ${dataset} == "sentiment_analysis" ];
then
    path="Maltese Sentiment"
fi

for token_mappings in "full" "small" ""; do
  for ranker in "sub_tokens_count_tunis" "word_model_score_tunis" "character_model_score_tunis" "sub_tokens_count_maghreb" "word_model_score_maghreb" "character_model_score_maghreb" "random" ""; do
    args=()

    # token mappings
    if [[ -n ${token_mappings} ]]; then
      system="+closed_class_${token_mappings}"

      args+=("--token_mappings")
      if [[ ${token_mappings} == "full" ]]; then
        args+=("token_mappings/additional_closed_class.map" "token_mappings/small_closed_class.map")
      elif [[ ${token_mappings} == "small" ]]; then
        args+=("token_mappings/small_closed_class.map")
      fi
    else # character mappings only
      system=""
    fi

    # rankers
    if [[ -n ${ranker} ]]; then  # non-deterministic
      system="non_deterministic${system}-${ranker}"
      args+=("--rankers" "$(echo $ranker | sed -e 's/_tunis//' -e 's/_maghreb//')" "character_model_score" "--ranker_models")

      # primary ranker
      if [[ ${ranker} == "sub_tokens_count"* ]]; then
        args+=("CAMeL-Lab/bert-base-arabic-camelbert-mix")
      elif [[ ${ranker} == "word_model_score_tunis" ]]; then
        args+=("${MODELS_PATH}/aggregated_country/lm/word/tn-maghreb.arpa")
      elif [[ ${ranker} == "character_model_score_tunis" ]]; then
        args+=("${MODELS_PATH}/aggregated_country/lm/char/tn-maghreb.arpa")
      elif [[ ${ranker} == "word_model_score_maghreb" ]]; then
        args+=("${MODELS_PATH}/aggregated_region/lm/word/maghreb.arpa")
      elif [[ ${ranker} == "character_model_score_maghreb" ]]; then
        args+=("${MODELS_PATH}/aggregated_region/lm/char/maghreb.arpa")
      elif [[ ${ranker} == "random" ]]; then
        args+=("")
      fi

      # fallback ranker
      if [[ ${ranker} = *_maghreb ]]; then
        args+=("${MODELS_PATH}/aggregated_region/lm/char/maghreb.arpa")
      else
        args+=("${MODELS_PATH}/aggregated_country/lm/char/tn-maghreb.arpa")
      fi
    else  # deterministic
      system="deterministic${system}"
    fi

    echo "========== $system =========="
    python transliterate_cli.py "${dataset}" "${DATA_PATH}/${path}" "${OUTPUT_PATH}/${system}/${path}" "${args[@]}"
  done
done
