
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gobattlesim",
    version="0.8.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ymenghank/GoBattleSim-Python",
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Development Status :: 4 - Beta"
    ],

    packages=setuptools.find_packages(),
    package_data={'gobattlesim': ['libGoBattleSim.dll', 'libGoBattleSim.so']},
)
