# Release History

## Pre-release

### Changes
- Add support for Manganelo links for Manganato (this might change at any point)
- The default replacement rules change to space instead of nothing

### Internal
- Better flake8 rule selection

## v1.15.3(2021-07-26)

### Changes
- Manganelo changed name to Manganato

## v1.15.2(2021-06-07)

### Fixes
- Crash caused by outdated urllib3

## v1.15.1(2021-05-26)

### Fixes
- Crash when getting some mangadex covers

## v1.15.0(2021-05-25)

### New
- Mangadex covers (they also now respect the data saver option)

### Fixes
- Rate limiting not actually working as it should
- Better message on rate limit error
- Mangadex results are now also sorted by volume (should help a bit with anthologies)

### Code-quality
- `cover_url` renamed to `covers`

## v1.14.0(2021-05-22)

### Fixes
- mangadex language selection (API changed the query parameter)
- Typo that would cause crash if downloader was ran directly

### Changes
- Very slight help message changes

### Internal
- Code moved to follow [black](https://black.readthedocs.io/en/stable/) formatting
- Added flake8 with plugins to catch mistakes
- Started using isort to automatically sort imports
- Added `requirements-dev.txt`

## v1.13.0(2021-05-21)

### Changes
- Migrated to the new Mangadex API
- Slight output changes
- Downloader will now exit with status code 1 if config has a invalid language code

### Removed
- MD@Home setting

### New
- Data saving setting `conf --data-saver` that will download the lower quality images (off by default)
- `--data-saver {yes(y),no(n)}` flag for `down` and `update` that overwrites the data saver setting in the config file
- `down --language` and `update --language` arguments that allow to overwrite the config language setting

### Fixes
- Mangadex no longer says that there's been an error when no chapters found matching the criteria but just prints that none were found
- Crash on python 3.6 because of unsupported `required` keyword argument in `add_subparsers`

## v1.12.0(2021-01-20)

### New
- MD@Home setting
- basic config validation

### Fixes
- mangakakalot crash
- crash when the link points to a non existing manga

### Changes
- Mangadex module now also works with URLs like `/manga/ID`
- downloader now checks the chapters in ascending order (won't effect much)
- downloader now asks for a new chapter number if it's already taken (fixes #21, might cause unexpected behaviour with `-c/--check` or `-i/--ignore-input`)

## v1.11.2(2021-01-11)

### Fixes
- version check now properly compares to the newest version

## v1.11.1(2021-01-11)

### Changes
- removed dot from cover filename for mangadex

## v1.11.0(2021-01-11)

### Changes
- migrated to the Mangadex V2 API
- downloader will now get all available covers (only mangadex supports this for now)

## v1.10.0(2020-10-22)

### New
- if manga is tracked the tracked title will be used instead of the fetched one
- title is now determined in order of: custom name > tracked title > fetched title
- you can now use a tracked title as a download target in down mode
- new `conf --change-name` argument for changing the title of tracked manga
- when renaming tracked manga downloader will ask if it should rename old files
- new `conf -n/--name` argument to allow adding manga to tracked with a custom name (should not be used when adding multiple manga)
- character replacement list for titles, by default replaces `/ \ | ? > < . : ? *` with nothing (just removes them)
- new conf arguments for the replacement rules (`--rule-reset/--rule-print/--rule-add/--rule-remove`)

### Changes
- help message changed to fit new functionality
- changed all long argument to use "-" instead of "\_"
- config will now look for the environment variable `XDG_CONFIG_HOME` before defaulting to `~/.config` 
- white space removed from beginning and end of titles (only really matters for custom titles)

### Fixes
- downloader no longer catches all exceptions (oops)

## v1.9.3(2020-09-07)

### Fixes
- Manga Plus releases not being handled correctly

## v1.9.2(2020-07-07)

### Removed
- mangaseeonline support, site now requires JS to work

### Changes
- internal stuff

## v1.9.1(2020-06-26)

### Fixes
- manganelo and mangakakalot image downloads no longer fail because of cloudflare

## v1.9.0(2020-06-21)

### Fixes
- fixed crash if manga had "/" in title, now is replaced with "╱"

### Changes
- `-i/--ignore_input` and `-c/--check` are now mutually exclusive
- removed titles from mangadex links
- `conf -r/--remove-tracked` uses the site regex to check if link can be shortened (for now only mangadex benefits from this)
- preserved order of input for `down`, `conf -a/--add-tracked`
- more verbose output for `conf -r/--remove-tracked` if argument is not tracked
- `-a/--add-tracked` and `-r/--remove-tracked` are now mutually exclusive giving an error instead of just doing one
- `-s/--save-directory` now prints a confirmation that the directory got changed
- config is now always saved after KeyboardInterrupt
- failing to load config will result in exit code 1

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

## v1.6.1(2020-01-14)

### Changes
- mangadex is back to it's .org domain (.cc links will still work)

## v1.6.0(2020-01-08)

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

## v1.5.1(2020-01-05)

### Fixes
- mangadex moved (temporarily) from .org to .cc (added error message to remind about the change if given a .org link)
- mangatown module fixed
- another heavenmanga url change 

## v1.5.0(2019-11-15)

### New
- down -n/--name flag, downloads the given manga using a custom name
- if a mangadex chapter has no chapter number the downloader will ask for one

### Changes
- divided get\_chapters() into 2 methods (get\_main() and get\_chapters()) so that the downloader first prints what manga it's working on and then actually does the work (this will allow better handling of edge cases like the mangadex one listed above)
- added \_\_len\_\_() and \_\_bool\_\_() to manga classes
- added manganelo.com url support for the mangakakalot module

### Fixes
- another heavenmanga base url change

## v1.4.1(2019-10-29)

### Changes
- selected chapters are now checked in a sorted order

### Fixes
- mangadex get_id crash when link did not end with a slash
- delayed chapters being included in the "to download" summary
- crash if trying to download multiple chapters for a manga

## v1.4.0(2019-10-10)

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

## v1.3.0 (2019-09-19)

### Changes
- new get_handler() function that handles all request exceptions, meaning all site modules don't have to catch them and can just raise them when needed
- shorter import statements

### Fixes
- fixed the mangatown_com module continuing to look for chapter pages even though one was not working, now raises a exception and stops the loop as expected

## v1.2.1 (2019-09-17)

### Fixes
- requests.ConnectionError crash fix

## v1.2.0 (2019-09-15)

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

## v1.1.1 (2019-09-10)

### New
- added CHANGELOG.md

### Fixes
- updated README.md

## v.1.1.0 (2019-09-10)

### New
- heavenmanga and mangatown modules

### Changes
- mangadex module uses regex to get the chapter id number
- removed useless comments
- small update mode output change - shows the number of chapters that will get downloaded right above the confirmation instead above the chapter listing
- using imghdr.what() to find file extension

## v1.0.0 (2019-09-06)
First PyPI release
