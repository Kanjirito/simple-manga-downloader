import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

required = [
    "cfscrape",
    "beautifulsoup4"
]

setuptools.setup(
    name="simple-manga-downloader",
    version="1.4.1",
    author="Kanjirito",
    author_email="kanjirito@protonmail.com",
    license="GPLv3",
    url="https://github.com/Kanjirito/simple-manga-downloader",
    description="Simple manga console downloader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Console"
    ],
    python_requires=">=3",
    entry_points={
        "console_scripts": [
            "SMD=simple_manga_downloader.SMD:main"
        ]
    }
)
