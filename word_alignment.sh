#!/bin/bash

FAST=$WORK/fast_align/build
UNFOLD=$WORK/corpora-tools/build/bin

src=$1
tgt=$2
aligns=$3
langPair=$4
base=data/$langPair/train

mkdir -p $base/$aligns

paste $base/$src $base/$tgt | perl -pe 's/\t/ \|\|\| /' > $base/mixed.tmp
echo "Running fast align forward"
$FAST/fast_align -i $base/mixed.tmp -d -o -v -p $base/$aligns/${langPair}.forward.probs -t -100000 > $base/$aligns/forward.align 2> $base/$aligns/forward.align.log
date
echo "Running fast align reverse"
$FAST/fast_align -i $base/mixed.tmp -d -o -v -r -p $base/$aligns/${langPair}.reverse.probs -t -100000 > $base/$aligns/reverse.align 2> $base/$aligns/reverse.align.log
date

echo "Running atools gdfa"
$FAST/atools -i $base/$aligns/forward.align -j $base/$aligns/reverse.align -c grow-diag-final-and > $base/$aligns/clean.${langPair}.gdfa
date
# echo "Running atools intersect"
# $FAST/atools -i $base/$aligns/forward.align -j $base/$aligns/reverse.align -c intersect > $base/$aligns/clean.${langPair}.inter
# date

echo "Running unfold gdfa"
$UNFOLD/unfold -s $base/$src -t $base/$tgt -a $base/$aligns/clean.${langPair}.gdfa -src_consec > $base/$aligns/align_units.clean.${langPair}.gdfa.src_consec
date
# echo "Running unfold intersect"
# $UNFOLD/unfold -s $base/$src -t $base/$tgt -a $base/$aligns/clean.${langPair}.inter -src_consec > $base/$aligns/align_units.clean.${langPair}.inter.src_consec
# date

rm $base/mixed.tmp
# rm $base/forward.*
# rm $base/reverse.*
