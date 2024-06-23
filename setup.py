from setuptools import setup

with open("src/requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="malaWeb",
    version="0.3",
    install_requires=required,
    packages=[],
    url="https://github.com/mala-project/malaWeb/tree/dev",
    license="",
    author="Maximilian Wenger",
    author_email="wengmax@proton.me",
    description="Web app to visualize on-the-fly MALA prediction",
)
