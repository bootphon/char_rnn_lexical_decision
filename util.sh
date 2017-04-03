cd probs/exp50M/
for filename in *; do
        ( cd ../../
        python stats_table.py -input_table probs/exp50M/$filename -output_table tables/exp50M/$filename -corpus_h5 networks/data/corpus50M.h5 -corpus_json networks/data/corpus50M.json
        )
done
