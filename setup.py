
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gobattlesim",
    version="0.4.1",
    author="Hank Meng",
    author_email="ymenghank@gmail.com",
    description="A Pokemon Go Battle Simulator engine with Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ymenghank/GoBattleSim-Python",
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha"
    ],

    packages=setuptools.find_packages(),
    package_data={'gobattlesim': ['GoBattleSim.dll', 'libGoBattleSim.so']},
)
