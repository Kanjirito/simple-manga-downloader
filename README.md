# simple-manga-downloader
Simple manga console downloader written in python.

Currently supports:

- [mangadex.org](https://mangadex.org/)
- [mangaseeonline.us](https://mangaseeonline.us/)
- [mangatown.com](https://www.mangatown.com/)
- [heavenmanga.org](https://ww2.heavenmanga.org/)
- [mangakakalot.com](https://mangakakalot.com/page)


Allows you to download manga in 5 ways:

- all chapters of a series
- a range of chapters (from 5 to 15)
- a selection of chapters (5, 7, 10, 20)
- only the newest chapter
- check for new chapters for the tracked manga

Additional features of the downloader:

- It will check if a chapter on mangadex.org has multiple uploads by different groups and ask which one to download
- It handles the MangaPlus chapters
- You can change the directory where the manga is saved
- You can add ongoing manga to the tracked list for a easy way to check for new chapters
- Config is saved as a .json for readability and easy modification
- The downloader has a config "mode" that allows the modification of the config file without having to edit the .json manually


# Installation


## Requirements
- BeautifulSoup 4
- cfscrape

**IMPORTANT!**

[cfscrape requires Node.js to be installed](https://github.com/Anorov/cloudflare-scrape#nodejs-dependency)


## pip
```
pip install simple-manga-downloader
```


# USAGE

You can specify a different config to be used like this:

```
SMD -c "path/to/config" mode arguments
```

Examples:
```
SMD -c "~/Downloader/config.json" down link_to_manga -l
SMD -c "~/Downloader/config.json" update
```

## Download mode
This mode will download the manga from the link based on your selection, accepts multiple links.

Download all of the chapters:

```
SMD down link_to_manga [more_links]
```

Download a range of chapters (both ends are inclusive):

```
SMD down link_to_manga [more_links] -r 1 20
SMD down link_to_manga [more_links] --range 1 20
```

Download specific chapters (works if numbers are not in order):

```
SMD down link_to_manga [more_links] -s 1 10 5 15
SMD down link_to_manga [more_links] --selection 1 10 5 15
```

Download the newest chapter (based on chapter number not time of upload):

```
SMD down link_to_manga [more_links] -l
SMD down link_to_manga [more_links] --latest
```

Exclude chapters from download (works together with -r and -s):

```
SMD down link_to_manga [more_links] -e 5 10 1
SMD down link_to_manga [more_links] --exclude 5 10 1
```

Download into a different directory:
```
SMD down link_to_manga -d "some/path"
```

## Update mode
This mode will go over every manga tracked in the config and download every missing chapter

```
SMD update
```

## Config mode
This mode allows the modification of the config file.

Adding a manga to the tracked list:
```
SMD conf -a link_to_manga [more_links]
SMD conf --add-tracked link_to_manga [more_links]
```

Removing a manga from the tracked list using links:
```
SMD conf -r link_to_manga [more_links]
SMD conf --remove-tracked link_to_manga [more_links]
```

Removing a manga from the tracked list by index:
```
SMD conf -r 5 1 3
SMD conf --remove-tracked 5 1 3
```


**Note:**
*You can't add and remove at the same time, if both `-a` and `-r` are present it will only add manga.*


Removing a manga from the tracked list by title:
```
SMD conf -r title "title with spaces"
SMD conf --remove-tracked title "title with spaces"
```

Removal by index, title and link can be used together (works if multiple point to the same manga):
```
SMD conf -r link_to_manga 5 "sample title" link_to_manga 2
```

Clearing the tracked list:
```
SMD conf -t
SMD conf --clear-tracked
```

Changing the save directory:
```
SMD conf -s path/to/directory
SMD conf --save-directory path/to/directory
```

Toggle the covers setting:
```
SMD conf -c
SMD conf --covers
```

Reset the config to the default:
```
SMD conf -d
SMD conf --default
```

Listing all of the tracked manga(add -v/--verbose flag to also print the links):
```
SMD conf -l (-v)
SMD conf --list-tracked (--verbose)
```

Change the position of a manga:
```
SMD conf -m
SMD conf --modify-position
```

Print the config and download paths:
```
SMD conf -p
SMD conf --paths
```
