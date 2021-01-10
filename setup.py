from distutils.core import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="suas_helmsman",
    version="0.1.0",
    description="ARC's Python-based Pre Path Planning Library",
    long_description=long_description,
    url="https://github.com/ncsuarc/suas-helmsman",
    author="NC State Aerial Robotics Club",
    author_email="contact@aerialroboticsclub.com",
    packages=["suas_helmsman"],
    install_requires=[
        "networkx",
        "Shapely",
        "PyGeodesy",
    ],
)
