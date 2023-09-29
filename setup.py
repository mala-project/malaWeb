from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='malaWeb',
    version='0.1',
    install_requires=['json', 'dash==2.12.0', 'dash_bootstrap_components==1.4.1', 'pandas>=2.0.0', 'numpy>=1.22.4', 'plotly==5.14.0', 'ase==3.22.1', 'dash_uploader==0.7.0a1'],
    packages=[],
    url='https://github.com/mala-project/malaWeb/tree/main',
    license='',
    author='Maximilian Wenger',
    author_email='wengmax@proton.me',
    description='Web app to visualize on-the-fly MALA prediction'
)
