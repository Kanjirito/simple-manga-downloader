# Release History

## v1.4.0(pre-release)

## New
- covers, a new config setting that allows to download the covers for the manga, defaults to false
- conf -c/--covers flag to toggle the cover option
- after download lists what chapters have failed/succeeded
- invalid input in mangadex multiple groups selection will now skip the chapter instead of forcing a choice

## Changes
- every module now uses request sessions
- changed get_handler() into a decorator
- modules now use the new exception handler decorator 
- moved decorators into a separate file
- conf -c/--clear-tracked had the short flag changed to -t
- config parser now falls back to defaults if setting is missing
- changed the download chunk size
- output changes
- down and update mode now have the same order of action
- a lot of code changes/clean-up

## Fixes
- heavenmanga switched to cfscrape and url changed
- conf -r index errors
- default download path when using custom config
- html entities in group names

## v1.3.0 (19-09-19)

### Changes
- new get_handler() function that handles all request exceptions, meaning all site modules don't have to catch them and can just raise them when needed
- shorter import statements

### Fixes
- fixed the mangatown_com module continuing to look for chapter pages even though one was not working, now raises a exception and stops the loop as expected

## v1.2.1 (19-09-17)

### Fixes
- requests.ConnectionError crash fix

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
- heavenmanga_org module exception
- file extension fix

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
