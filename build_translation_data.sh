#!/bin/bash

# l1=en
# l2=fr
# testset=newstest2014
l1=$1
l2=$2
testset=$3
langPair=${l2}-${l1}
BPE_ROOT=$WORK/subword-nmt/subword_nmt
BPE_CODE=data/$langPair/joint_bpe.$langPair.32k

# Use train, dev and test data for word alignment

echo "Concatenating train dev sets..."
for cls in {dev,test}; do
  # for f in data/$langPair/$cls/$cls/*.$l1;
  for f in data/$langPair/$cls/$cls/toka.news*.$l1; do
    echo $(basename $f)
  done > data/$langPair/$cls/$cls/concat_order.txt
done

# for l in $l1 $l2; do
for f in `cat data/$langPair/dev/dev/concat_order.txt`; do
  cat data/$langPair/dev/dev/$f
done > data/$langPair/dev/dev/toka.dev_sets.${l1}

for f in `cat data/$langPair/dev/dev/concat_order.txt`;
do
  cat data/$langPair/dev/dev/${f/.$l1/.$l2}
done > data/$langPair/dev/dev/toka.dev_sets.${l2}

for l in $l1 $l2; do
  cat data/$langPair/train/toka.clean.${langPair}.$l data/$langPair/dev/dev/toka.dev_sets.$l data/$langPair/test/test/toka.$testset.$l > data/$langPair/train/toka.train_dev_test.$langPair.$l
done

echo "Done concatenation."
date

# cat data/$langPair/train/clean.${langPair}.${l1}.cons data/$langPair/dev/dev/dev_sets.${l1}.cons data/$langPair/test/test/$testset.$l1.cons > data/$langPair/train/train_dev_test.$langPair.$l1.cons
# cat data/$langPair/train/clean.${langPair}.${l2}.cons data/$langPair/dev/dev/dev_sets.${l2}.cons data/$langPair/test/test/$testset.$l2.cons > data/$langPair/train/train_dev_test.$langPair.$l2.cons

echo "Start word alignment..."
./word_alignment.sh toka.train_dev_test.$langPair.$l1 toka.train_dev_test.$langPair.$l2 new_aligns_trn_dev_tst $langPair
echo "Alignment finished."
date
 
echo "Start random replacement..."
python align_replace_amb_multiprocess.py -s data/$langPair/train/toka.train_dev_test.${langPair}.$l1 -t data/$langPair/train/toka.train_dev_test.${langPair}.$l2 -a data/$langPair/train/new_aligns_trn_dev_tst/align_units.clean.${langPair}.gdfa.src_consec -o data/$langPair/train/toka.train_dev_test.$langPair --max_rep 3
echo "Repalcement finished."
date

f=data/$langPair/train/toka.train_dev_test.$langPair.cs
echo "apply_bpe.py on $f..."
python $BPE_ROOT/apply_bpe.py -c $BPE_CODE -i $f -o ${f/toka/bpe}
date
