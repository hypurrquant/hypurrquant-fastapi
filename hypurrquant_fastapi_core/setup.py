from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name="hypurrquant_fastapi_core",  # 패키지 이름
    version="0.6.13",  # 버전
    author="NOH YUSEONG",
    author_email="shdbtjd8@gmail.com",
    packages=find_packages(),  # 현재 디렉토리에서 패키지 찾기
    install_requires=install_requires,
    python_requires=">=3.10",  # 지원하는 Python 버전
)
