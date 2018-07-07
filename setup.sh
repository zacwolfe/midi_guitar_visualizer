#!/usr/bin/env bash
git clone https://github.com/infojunkie/mma.git mma_main
cd mma_main
git apply ../mma.patch
python mma.py -G
cd ..
git clone https://github.com/olemb/mido.git
cd mido
git apply ../mido.patch
pip install .
cd ..
pip install -r requirements.txt