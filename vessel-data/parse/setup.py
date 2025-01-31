from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="vessel-parse",
    version="0.5.4",
    author="Andrej Baranovskij",
    author_email="andrejus.baranovskis@gmail.com",
    description="Vessel Parse is a Python package (part of Vessel) for parsing and extracting information from documents.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vesselgpt/vessel/tree/main/vessel-data/parse",
    project_urls={
        "Homepage": "https://github.com/vesselgpt/vessel/tree/main/vessel-data/parse",
        "Repository": "https://github.com/vesselgpt/vessel",
    },
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3.10",
    ],
    entry_points={
        'console_scripts': [
            'vessel-parse=vessel_parse:main',
        ],
    },
    keywords="llm, vllm, ocr, vision",
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=requirements,
)
