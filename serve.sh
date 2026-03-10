#!/bin/bash
# Acha o requirements e instala onde quer que ele esteja
pip install -r $(find . -name requirements.txt)
# Acha o main.py e executa
python $(find . -name main.py)



