# Release History

## v1.2.0 (19-09-15)

### New
- added template module to git repository
- down -e/--exclude flag that will exclude given chapters from being downloaded
- mangakakalot.com module

### Changes
- mangadex module will now show all groups for a chapter (Group A | Group B | Group C)
- down -r and -s flags now will decline non-number input
- removed the Manga.ch_info list, now Manga.chapters gets edited
- small changes to the filtering functions

### Fixes
- manga that only has 1 chapter with chapter number 0 will no longer ignore selection
- fixed images saving as .None when imghdr.what() did not find the file type, the response header will be used in that case

## v1.1.1 (19-09-10)

### New
- added CHANGELOG.md

### Fixes
- updated README.md

## v.1.1.0 (19-09-10)

### New
- heavenmanga and mangatown modules

### Changes
- mangadex module uses regex to get the chapter id number
- removed useless comments
- small update mode output change - shows the number of chapters that will get downloaded right above the confirmation instead above the chapter listing
- using imghdr.what() to find file extension

## v1.0.0 (19-09-06)
First PyPI release
