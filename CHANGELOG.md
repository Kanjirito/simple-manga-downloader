# Release History

## Pre-release

### Changes
- `-i/--ignore_input` and `-c/--check` are now mutually exclusive
- removed titles from mangadex links
- preserved order of input for `down`, `conf -a/--add-tracked`
- more verbose output for `conf -r/--remove-tracked` if argument is not tracked

### Internal
- all site modules now inherit from BaseManga
- all site modules now create a single `requests.Session()` used by all instances of it
- argument parsing moved to it's own module
- argument parser and config parser moved out of modules directory
- better checking if manga in tracked
- using regex to find module for link allowing for nicer module importing
- functions for setting `BaseManga` attributes added for clarity

## v1.8.0(2020-06-04)

### New
- `down -c/--check` to only check for what's available without downloading or asking for input
- `-i/--ignore_input` for both down and update mode, downloader will not ask for input but will start downloading
- `update -d/--directory` to change download directory

### Changes
- use sets instead of lists to remove duplicates from arguments
- additional and more verbose exception handling

### Fixes
- crash when trying to reset config
- spelling mistakes
- Manganelo chapters with no chapter number will now ask for one

## v1.7.0(2020-04-20)

### New
- a failed page download now shows the reason
- `page_download_timeout` setting to change the timeout for downloading images (in seconds)
- `conf --timeout` to change the timeout setting
- `down` now accepts int to download manga from the tracked list with the given index
- Keyboard Interruptions are now caught
- `update -c/--check` to only check for new chapters without downloading or needing input
- `version` mode, prints the current version
- `version -c/--check` checks if a new version is available

### Removed
- removed heaven manga support because it constantly keeps creating new problems (domain changes, cloudflare problems)
- removed cfscrape from the requirements (this also removes the node.js dependency)
- `-v/--version` flag, replaced by version mode

### Changes
- config and args variables changed back to globals to avoid passing them around all the time

### Fixes
- `conf -p` now prints the absolute path (only matters when using a custom config path)
- config_parser now properly creates a dict for the tracked manga if no config was present

## v1.6.1(20-01-14)

### Changes
- mangadex is back to it's .org domain (.cc links will still work)

## v1.6.0(20-01-08)

### New
- mangadex language code selection
- `conf --list_lang` to list available codes
- `conf --change_lang` to change the language
- `SMD -v (--version)` prints current version
- deletes failed chapters

### Changes
- the "to download" and after download summaries now include chapter titles when possible
- help message improvements
- moved config file to `~/.config/SMD`
- default download folder changed to `~/Manga`
- config file always gets created
- `conf -p (--print_conf)` now prints all settings
- `down` mode now requires a link
- downloader will abort if config failed to load
- manganelo moved to it's separate module

### Fixes
- crash if using `down -l` and no manga fits the criteria
- `conf -d (--default)` now sets the proper download directory

## v1.5.1(20-01-05)

### Fixes
- mangadex moved (temporarily) from .org to .cc (added error message to remind about the change if given a .org link)
- mangatown module fixed
- another heavenmanga url change 

## v1.5.0(19-11-15)

### New
- down -n/--name flag, downloads the given manga using a custom name
- if a mangadex chapter has no chapter number the downloader will ask for one

### Changes
- divided get\_chapters() into 2 methods (get\_main() and get\_chapters()) so that the downloader first prints what manga it's working on and then actually does the work (this will allow better handling of edge cases like the mangadex one listed above)
- added \_\_len\_\_() and \_\_bool\_\_() to manga classes
- added manganelo.com url support for the mangakakalot module

### Fixes
- another heavenmanga base url change

## v1.4.1(19-10-29)

### Changes
- selected chapters are now checked in a sorted order

### Fixes
- mangadex get_id crash when link did not end with a slash
- delayed chapters being included in the "to download" summary
- crash if trying to download multiple chapters for a manga

## v1.4.0(19-10-10)

### New
- covers, a new config setting that allows to download the covers for the manga, defaults to false
- conf -c/--covers flag to toggle the cover option
- after download lists what chapters have failed/succeeded
- invalid input in mangadex multiple groups selection will now skip the chapter instead of forcing a choice

### Changes
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

### Fixes
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
