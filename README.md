# simple-manga-downloader
Simple manga downloader written in python.
Currently supports mangadex.org and mangaseeonline.us.

Allows you to download manga in 4 ways:

- all chapters of a series
- a range of chapters (from 5 to 15)
- a selection of chapters (5, 7, 10, 20)
- check for new chapters for the tracked manga

Additional features of the downloader:
- It will check if a chapter on mangadex.org has multiple uploads by different groups and ask which one to download
- You can change the directory where the manga is saved
- You can add ongoing manga to the tracked list for a easy way to check for new chapters
- Config is saved as a .json for readability and easy modification
- The downloader has a config "mode" that allows the modification of the config file without having to edit the .json manually


# USAGE

## Download mode
This mode will download the manga from the link based on your selection.

Download all of the chapters:

```
SMD.py down link_to_manga
```

Download a range of chapters (both ends are inclusive):

```
SMD.py down link_to_manga -r 1 20
SMD.py down link_to_manga --range 1 20
```

Download specific chapters:

```
SMD.py down link_to_manga -s 1 5 10 15
SMD.py down link_to_manga --selection 1 5 10 15
```

Download the newest chapter (based on chapter number not time of upload):

```
SMD.py down link_to_manga -l
SMD.py down link_to_manga --latest
```

## Update mode
This mode will go over every manga tracked in the config and download every missing chapter

```
SMD.py update
```

## Config mode
This mode allows the modification of the config file.

Adding a manga to the tracked list:
```
SMD.py conf -a link_to_manga
SMD.py conf --add-tracked link_to_manga
```

Removing a manga from the tracked list:
```
SMD.py conf -r link_to_manga
SMD.py conf --remove-tracked link_to_manga
```

Clearing the tracked list:
```
SMD.py conf -c
SMD.py conf --clear-tracked
```

Changing the save directory:
```
SMD.py conf -s path_to_directory
SMD.py conf --save-directory path_to_directory
```

Reset the config to the default:
```
SMD.py conf -d 
SMD.py conf --default
```

Listing all of the tracked manga:
```
SMD.py conf -l 
SMD.py conf --list-tracked
```

