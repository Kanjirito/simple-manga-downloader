# simple-manga-downloader
Simple manga downloader written in python.
Currently supports only mangadex.org.

Allows you to download manga in 4 ways:

-all chapters of a series

-a range of chapters (from 5 to 15)

-a selection of chapters (5, 7, 10, 20)

-check for new chapters for the tracked manga

The downloader will check if a chapter has multiple uploads by different groups and ask which one to download.

The downloader will save a simple config file in a json format with the directory where the manga will be saved and a list of the tracked manga. The downloader has a "mode" to allow the editing of the config file without having to do it manually.

# USAGE
To download manga using a link:

`main.py down link_to_manga`

To download a range of chapters:

`main.py down link_to_manga -r 1 20 (both ends are inclusive)`

To download a selection of manga:

`main.py down link_to_manga -s 1 5 10 15`


To check for new updates for the tracked manga:

`main.py update`
