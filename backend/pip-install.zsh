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
    
pip freeze > requirements.txt