# Detailed argument and mode explanation

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
SMD down link_to_manga -d "some/custom/path"
SMD down link_to_manga --directory "some/custom/path"
```

Download using a custom name:
```
SMD down link_to_manga -n Some new name
SMD down link_to_manga --name Some new name
```
**Warning:**
*Using a custom name when downloading multiple manga at once will cause overwriting of the files since all of them will be assigned the same name*

Download a manga from the tracked list by index or title:
```
SMD down 1 "tracked title" 5
```

Download manga without asking for any input (in case of multiple groups it will choose the alphabetically first one):
```
SMD down manga_url -i
SMD down manga_url --ignore-input
```

Same as above but without downloading:
```
SMD down manga_url -c
SMD down manga_url --check
```

Ignore the data saver config setting for this download (Mangadex only):
```
SMD down manga_url --data-saver true
SMD down manga_url --data-saver false
```

## Update mode
This mode will go over every manga tracked in the config and download every missing chapter. If a manga is tracked the downloader will use the saved name even if the title on the page changes.

```
SMD update
```

Use a custom directory:
```
SMD update -d "some/custom/path"
SMD update --directory "some/custom/path"
```

To only check for new chapters without downloading or needing input:
```
SMD update -c
SMD update --check
```

Same as above but with downloading:
```
SMD update -i
SMD update --ignore-input
```

**Warning:**
*Using `-c/--check` or `-i/--ignore-input` with manga that resets chapter numbers for each Volume/Season might cause unexpected behaviour.*

## Config mode
This mode allows the modification of the config file.

Changing the mangadex language:
```
SMD conf --change-lang code
```

Toggle if the downloader should get the lower quality images (off by default):
```
SMD conf --data-saver
```

Listing available language codes:
```
SMD conf --list-lang
```

Adding a manga to the tracked list:
```
SMD conf -a link_to_manga [more_links]
SMD conf --add-tracked link_to_manga [more_links]
```

You can also add a manga to the tracked list with a custom name, should not be used when adding multiple manga at once (the last manga will overwrite the rest):
```
SMD conf -a link_to_manga --name Some new name
SMD conf -a link_to_manga -n Some new name
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

Changing the manga download directory:
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

Change the title of a manga, will ask if you want to rename existing files (could overwrite other files):
```
SMD conf --change-name
```

Print the current settings:
```
SMD conf -p
SMD conf --print-conf
```

Change the page download timeout (in seconds):
```
SMD conf --timeout seconds
```

Reset the character replacement rules:
```
SMD conf --rules-reset
```

Remove a character replacement rule:
```
SMD conf --rule-remove CHAR
```

Add (or change) a character replacement rule, if no replacement is given it will be set to "":
```
SMD conf --rule-add CHAR
SMD conf --rule-add CHAR what to replace it with
```

Print the current character replacement rules:
```
SMD conf --rule-print
```


## Version mode
To print the current version:
```
SMD version
```

To check for new versions
```
SMD version -c
SMD version --check
```
