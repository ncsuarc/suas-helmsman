from distutils.core import setup
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md")) as f:
    long_description = f.read()

setup(
    name="suas_path_planning",
    version="0.1.0",
    description="ARC's Python-based Pre path planning",
    long_description=long_description,
    url="https://github.com/ncsuarc/sda_autogen",
    author="NC State Aerial Robotics Club",
    author_email="contact@aerialroboticsclub.com",
    packages=["autogen"],
    package_dir={"suas_path_planning": "autogen"},
    install_requires=[
        # NetworkX Library
        "networkx",
        # Shapely Library
        "Shapely",
        # PyGeodesy Library
        "PyGeodesy",
    ],
)
