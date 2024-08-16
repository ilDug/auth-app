#!/bin/zsh

pip install "fastapi[all]" \
    aiofiles \
    bcrypt \
    cryptography \
    black \
    icecream \
    PyJWT \
    pymongo \
    requests \
    
pip freeze > requirements.txt