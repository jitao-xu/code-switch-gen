#!/bin/bash

l1=en
l2=fr
langPair=${l2}-${l1}

SCRIPTS=$WORK/mosesdecoder/scripts
TOKENIZER=$SCRIPTS/tokenizer/tokenizer.perl
CLEAN=$SCRIPTS/training/clean-corpus-n.perl
NORM_PUNC=$SCRIPTS/tokenizer/normalize-punctuation.perl
REM_NON_PRINT_CHAR=$SCRIPTS/tokenizer/remove-non-printing-char.perl
BPEROOT=$WORK/subword-nmt/subword_nmt
BPE_TOKENS=32000

# # for f in data/$langPair/train/wmt_raw/{commoncrawl,europarl-v7,news-commentary-v8,undoc.2000}.es-en.en;
# for f in data/$langPair/train/wmt_raw/{commoncrawl,europarl-v7,giga-release2-fixed,news-commentary-v9,undoc.2000}.${langPair}.en;
# do
#   cat $f;
# done > data/$langPair/train/raw.${langPair}.en
# 
# # for f in data/$langPair/train/wmt_raw/{commoncrawl,europarl-v7,news-commentary-v8,undoc.2000}.es-en.es;
# for f in data/$langPair/train/wmt_raw/{commoncrawl,europarl-v7,giga-release2-fixed,news-commentary-v9,undoc.2000}.${langPair}.fr;
# do
#   cat $f;
# done > data/$langPair/train/raw.${langPair}.fr
# 
# python2 corpus-clean-bitext.py -src data/${langPair}/train/raw.${langPair}.fr -tgt data/${langPair}/train/raw.${langPair}.en -out data/${langPair}/train -tag parallel -max 100 -tok conservative
# perl -p -i -e "s/\r//g" data/${langPair}/train/parallel.raw.${langPair}.en
# perl -p -i -e "s/\r//g" data/${langPair}/train/parallel.raw.${langPair}.fr
# 
# python corpus_clean_lid.py -s data/${langPair}/train/parallel.raw.${langPair}.en -t data/${langPair}/train/parallel.raw.${langPair}.fr -m lid.176.bin --src_lang en --tgt_lang fr -o data/${langPair}/train/clean.${langPair}
# 
# # rm data/$langPair/train/parallel.*
 
echo "Running initial aggressive tokenization..."
for l in $l1 $l2; do
    rm data/$langPair/train/toka.clean.$langPair.$l
    cat data/$langPair/train/clean.$langPair.$l | \
        perl $NORM_PUNC $l | \
        perl $REM_NON_PRINT_CHAR | \
        perl $TOKENIZER -threads 10 -a -l $l >> data/$langPair/train/toka.clean.$langPair.$l &
done

wait

perl $CLEAN -ratio 1.5 data/$langPair/train/toka.clean.$langPair $l1 $l2 data/$langPair/train/test.toka.clean.$langPair 1 250
for l in $l1 $l2; do
  mv data/$langPair/train/test.toka.clean.$langPair.$l data/$langPair/train/toka.clean.$langPair.$l
done

TRAIN=data/$langPair/train/toka.clean.$langPair.$l1$l2
BPE_CODE=data/$langPair/joint_bpe.$langPair.32k
rm -f $TRAIN
for l in $l1 $l2; do
    cat data/$langPair/train/toka.clean.$langPair.$l >> $TRAIN
done

echo "learn_bpe.py on ${TRAIN}..."
python $BPEROOT/learn_bpe.py -s $BPE_TOKENS -i $TRAIN -o $BPE_CODE

for L in $l1 $l2; do
    f=data/$langPair/train/toka.clean.$langPair.$L
    echo "apply_bpe.py to ${f}..."
    python $BPEROOT/apply_bpe.py -c $BPE_CODE -i $f -o data/$langPair/train/bpe.clean.$langPair.$L & 
done

wait

