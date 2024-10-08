#!/usr/bin/env bash

BASEDIR=$(dirname "$0")
cd "$BASEDIR"

cd misc
rm mb_rime.txt
rm mb.txt
python gen_mb.py
cd ..

cd ibus
cat header.txt > hanma_ibus.txt
cat ../misc/mb_ibus.txt >> hanma_ibus.txt
echo "END_TABLE" >> hanma_ibus.txt
cd ..

cd rime
cat header.txt > hanma.dict.yaml
cat ../misc/mb_rime.txt >> hanma.dict.yaml
cd ..

cd fcitx
cat header.txt > hanma.txt
cat ../misc/mb.txt >> hanma.txt

# mkdir build
# cd build
# cmake ../
# make
# sudo make install
