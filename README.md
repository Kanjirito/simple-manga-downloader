# simple-manga-downloader
Simple manga console downloader written in python. Made for Linux but should work on any platform.

Currently supports:

- [mangadex](https://mangadex.org)
- [mangatown](https://www.mangatown.com)
- [mangakakalot](https://mangakakalot.com/page)
- [manganelo](https://manganelo.com)

*Note:* mangadex is the main supported site, the others *might* be maintained but they are not my top priority.

Allows you to download manga in 5 ways:

- all chapters of a series
- a range of chapters (from 5 to 15)
- a selection of chapters (5, 7, 10, 20)
- only the newest chapter
- check for new chapters for the tracked manga

Additional features of the downloader:

- It will check if a chapter on mangadex.org has multiple uploads by different groups and ask which one to download
- It handles the MangaPlus chapters on mangadex
- It can download the cover(s) for the manga (off by default)
- You can specify the language (mangadex only)
- You can specify which chapters to exclude from the download
- You can change the directory where the manga is saved
- You can add ongoing manga to the tracked list for a easy way to check for new chapters
- Config is saved as a .json for readability and easy modification
- The downloader has a config "mode" that allows the modification of the config file without having to edit the .json manually
- It can check for new available versions
- It will remove (or replace) characters from titles that could cause problems, by default removes `/ \ | ? > < . : ? *` (note that backslash `\` needs to be escaped with another one `\\`)


# Installation

## Requirements
- BeautifulSoup 4
- requests

## Releases form PyPI

Installing using pip will handle the requirements automatically. I would also recommend using [pipx](https://github.com/pipxproject/pipx) instead of just pip.

```
pip install simple-manga-downloader
```

## Using the git repo

### Installing using pip

To install from the master branch

```
pip install git+https://github.com/Kanjirito/simple-manga-downloader@master
```

### Using the git repo without installing

Copy the repo, install the requirements and use the entry script in the main repo directory
```
cd path/to/repo
chmod +x SMD.py
pip install -r requirements.txt
./SMD.py [mode] [arguments]
```


# USAGE

## General info

The default manga download directory is `~/Manga` this can be changed in the config file or in the command. The config directory is `$XDG_CONFIG_HOME/SMD` (`~/.config/SMD` if variable not set), you can specify a different config to be used like this:

```
SMD -c "path/to/config" mode arguments
```

Examples:
```
SMD -c "~/Downloader/config.json" down link_to_manga -l
SMD -c "~/Downloader/config.json" update
```
To create the config file the downloader needs to successfully finish. If you want to have the config created before you use the downloader you can do:
```
SMD conf
```

## Details
For a more detailed explanation of the modes and their available arguments read the [USAGE.md](USAGE.md) file in the git repo.

# Changelog

Changelog can be found in [CHANGELOG.md](CHANGELOG.md) in the git repo.
