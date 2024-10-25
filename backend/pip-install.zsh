#!/bin/zsh

pip install "fastapi[all]" \
    aiofiles \
    bcrypt \
    cryptography \
    black \
    icecream \
    PyJWT \
    pymongo \
    asyncio \
    httpx \
    requests \
    flake8 \
    
pip freeze > requirements.txt