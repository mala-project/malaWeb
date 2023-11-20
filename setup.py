from setuptools import setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="malaWeb",
    version="0.1",
    install_requires=required,
    packages=[],
    url="https://github.com/mala-project/malaWeb/tree/main",
    license="",
    author="Maximilian Wenger",
    author_email="wengmax@proton.me",
    description="Web app to visualize on-the-fly MALA prediction",
)
