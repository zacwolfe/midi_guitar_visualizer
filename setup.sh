#!/usr/bin/env bash
git clone https://github.com/infojunkie/mma.git mma_main
cd mma_main
git checkout faa3a983cedff06fd9622df8a1729ea0e71c7b41
git apply ../mma.patch
python mma.py -G
cd ..
git clone https://github.com/olemb/mido.git
cd mido
git checkout e87384d7e5d62de361a65ab6b1d5d62750475e84
git apply ../mido.patch
pip install .
cd ..
pip install -r requirements.txt