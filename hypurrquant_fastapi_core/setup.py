from setuptools import setup, find_packages

setup(
    name="hypurrquant_fastapi_core",  # 패키지 이름
    version="0.0.2",  # 버전
    author="NOH YUSEONG",
    author_email="shdbtjd8@gmail.com",
    packages=find_packages(),  # 현재 디렉토리에서 패키지 찾기
    install_requires=[
        "aiohappyeyeballs==2.4.4",
        "aiohttp==3.11.11",
        "aiosignal==1.3.2",
        "annotated-types==0.7.0",
        "anyio==4.8.0",
        "async-timeout==5.0.1",
        "attrs==24.3.0",
        "bitarray==3.0.0",
        "certifi==2024.12.14",
        "charset-normalizer==3.4.1",
        "click==8.1.8",
        "cytoolz==1.0.1",
        "dnspython==2.7.0",
        "eth-abi==4.2.1",
        "eth-account==0.10.0",
        "eth-hash==0.7.0",
        "eth-keyfile==0.8.1",
        "eth-keys==0.6.0",
        "eth-rlp==1.0.1",
        "eth-typing==5.1.0",
        "eth-utils==2.3.2",
        "exceptiongroup==1.2.2",
        "fastapi==0.115.6",
        "frozenlist==1.5.0",
        "gunicorn==23.0.0",
        "h11==0.14.0",
        "hexbytes==0.3.1",
        "httpcore==1.0.7",
        "httpx==0.28.1",
        "hyperliquid-python-sdk==0.9.0",
        "idna==3.10",
        "iniconfig==2.0.0",
        "motor==3.6.0",
        "msgpack==1.1.0",
        "multidict==6.1.0",
        "numpy==2.2.1",
        "packaging==24.2",
        "pandas==2.2.3",
        "parsimonious==0.9.0",
        "pluggy==1.5.0",
        "propcache==0.2.1",
        "pycryptodome==3.21.0",
        "pydantic==2.10.5",
        "pydantic_core==2.27.2",
        "pymongo==4.9.2",
        "pytest==8.3.4",
        "pytest-asyncio==0.25.2",
        "python-dateutil==2.9.0.post0",
        "python-dotenv==1.0.1",
        "pytz==2024.2",
        "redis==5.2.1",
        "regex==2024.11.6",
        "requests==2.32.3",
        "rlp==4.0.1",
        "sentry-sdk==2.20.0",
        "six==1.17.0",
        "sniffio==1.3.1",
        "starlette==0.41.3",
        "tomli==2.2.1",
        "toolz==1.0.0",
        "typing_extensions==4.12.2",
        "tzdata==2024.2",
        "urllib3==2.3.0",
        "uvicorn==0.34.0",
        "websocket-client==1.8.0",
        "yarl==1.18.3",
    ],
    python_requires=">=3.7",  # 지원하는 Python 버전
)
