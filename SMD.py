#!/bin/env python3
from modules.mangadex_org import Mangadex
from modules.mangaseeonline_us import Mangasee
from config_parser import Config
from pathlib import Path
import argparse
import requests
import time
import html
import os

ARGS = None
CONFIG = None


def main():
    global ARGS
    global CONFIG
    ARGS = parser()
    CONFIG = Config()
    mode = ARGS.subparser_name
    if mode == "down":
        down_mode()
    elif mode == "conf":
        conf_mode()
    elif mode == "update":
        update_mode()


def site_detect(link):
    '''Detects the site and creates a proper manga object'''
    if "mangadex.org" in link:
        Manga = Mangadex(link, CONFIG.manga_directory)
    elif "mangaseeonline.us" in link:
        Manga = Mangasee(link, CONFIG.manga_directory)
    else:
        print(f"Wrong link: \"{link}\"")
        return False

    status = Manga.get_chapters()
    if status is not True:
        print(f"\nSomething went wrong! \n{status}")
        return False
    return Manga


def parser():
    '''Parses the arguments'''
    parser = argparse.ArgumentParser()

    # Sub-parsers for the config and download functionality
    subparsers = parser.add_subparsers(dest="subparser_name",
                                       required=True)
    parser_conf = subparsers.add_parser("conf",
                                        help="Program will be in the config edit mode")
    parser_down = subparsers.add_parser("down",
                                        help="Program will be in the download mode")
    subparsers.add_parser("update",
                          help="Program will be in the update mode")

    # Parser for download mode
    parser_down.add_argument("input", nargs="*")
    # parser.add_argument("-d", "--directory")
    group = parser_down.add_mutually_exclusive_group()
    group.add_argument("-r", "--range",
                       help="Accepts two chapter numbers,"
                       "both ends are inclusive. \"1 15\"",
                       nargs=2)
    group.add_argument("-s", "--selection",
                       help="Accepts multiple chapters \"2 10 25\"",
                       nargs="+")
    group.add_argument("-l", "--latest",
                       action='store_true')

    # Parser for config mode
    parser_conf.add_argument("-a", "--add-tracked",
                             help="Adds manga to the tracked",
                             dest="add",
                             nargs="*")
    parser_conf.add_argument("-r", "--remove-tracked",
                             help="Removes manga from tracked",
                             dest="remove",
                             nargs="*")
    parser_conf.add_argument("-c", "--clear-tracked",
                             help="Clears the tracked list",
                             action="store_true")
    parser_conf.add_argument("-s", "--save-directory",
                             help="Changes the manga directory",
                             dest="m_dir")
    parser_conf.add_argument("-d", "--default",
                             help="Resets the config to defaults",
                             action="store_true")
    parser_conf.add_argument("-l", "--list-tracked",
                             help="Lists all of the tracked shows",
                             action="store_true",
                             dest="list")
    parser_conf.add_argument("-m", "--modify-position",
                             help="Changes the position of tracked manga",
                             action="store_true",
                             dest="position")

    args = parser.parse_args()
    return args


def down_mode():
    manga_objects = []
    for link in ARGS.input:
        Manga = site_detect(link)
        if not Manga:
            continue
        filter_wanted(Manga)
        if Manga.wanted:
            manga_objects.append(Manga)
    for Manga in manga_objects:
        print("\n------------------------\n"
              f"Getting: {Manga.series_title}"
              "\n------------------------")
        chapter_info_get(Manga)
        downloader([Manga])
    download_info_print()


def conf_mode():
    if ARGS.default:
        CONFIG.reset_config()
    elif ARGS.clear_tracked:
        CONFIG.clear_tracked()

    if ARGS.add is not None:
        CONFIG.add_tracked(ARGS.add)
    if ARGS.remove is not None:
        CONFIG.remove_tracked(ARGS.remove)
    if ARGS.list:
        CONFIG.list_tracked()
    if ARGS.m_dir is not None:
        CONFIG.change_dir(ARGS.m_dir)
    if ARGS.position:
        CONFIG.change_position()

    # Saves if config was modified
    if CONFIG.modified:
        CONFIG.save_config()


def update_mode():
    if not CONFIG.tracked_manga:
        print("No manga tracked!")
        return
    print(f"Updating {len(CONFIG.tracked_manga)} manga")
    manga_objects = []

    # Gets the main information about the manga
    for link in CONFIG.tracked_manga:
        Manga = site_detect(link)
        if not Manga:
            continue
        filter_wanted(Manga, ignore=True)
        if Manga.wanted:
            manga_objects.append(Manga)

    # Goes over every manga and gets the chapter information
    # Keeps track of some information
    total_num_ch = 0
    found_titles = {}
    if manga_objects:
        print("\n------------------------\n"
              "Getting info about chapters"
              "\n------------------------\n")
        for Manga in manga_objects:
            print(f"Getting chapter info for \"{Manga.series_title}\"",
                  "\n------------------------")
            chapter_info_get(Manga)
            print()
            total_num_ch += len(Manga.ch_info)
            found_titles[Manga.series_title] = [ch for ch in Manga.ch_info]

    print("------------------------\nChecking complete!\n")
    if not total_num_ch:
        print("Found 0 chapters ready to download.")
        return

    print(f"Found {total_num_ch} chapter(s) ready to download:")
    for title, chapter in found_titles.items():
        print(f"{title} - {len(chapter)} chapter(s):")
        for ch in chapter:
            print(f"    {ch['name']}")
    confirm = input(f"Start the download? "
                    "[y to confirm/anything else to cancel]: ").lower()
    if confirm == "y":
        downloader(manga_objects)
        download_info_print()
        print("Updated titles:")
        for title in found_titles:
            print(f"{title} - {len(found_titles[title])} chapter(s)")

    else:
        print("Download cancelled")


def filter_wanted(Manga, ignore=None):
    '''Creates a list of chapters that fit the wanted criteria
    ignore=True skips argument checking, used for update mode'''
    if ignore is None:
        ignore = False

    chapter_list = list(Manga.chapters)
    # Gets the chapter selection
    if ignore:
        filtered = chapter_list
    else:
        # If "oneshot" selection is ignored
        if len(Manga.chapters) == 1 and not chapter_list[0]:
            filtered = chapter_list
        elif ARGS.latest:
            filtered = [max(chapter_list)]
        elif ARGS.range is not None:
            a, b = [float(n) for n in ARGS.range]
            filtered = [ch for ch in chapter_list if a <= ch <= b]
        elif ARGS.selection is not None:
            filtered = []
            for n in ARGS.selection:
                n = float(n)
                if n.is_integer():
                    n = int(n)
                if n in chapter_list:
                    filtered.append(n)
        else:
            filtered = chapter_list
    filtered.sort()

    # Checks if the chapters that fit the selection are already downloaded
    if not Manga.manga_dir.is_dir():
        downloaded_chapters = None
    else:
        downloaded_chapters = os.listdir(Manga.manga_dir)

    Manga.wanted = []
    if downloaded_chapters is None:
        Manga.wanted = filtered
    else:
        Manga.wanted = []
        for n in filtered:
            chapter_name = f"Chapter {n}"
            if chapter_name not in downloaded_chapters:
                Manga.wanted.append(n)

    print("\n------------------------\n"
          f"Found {len(Manga.wanted)} wanted chapter(s) for {Manga.series_title}"
          "\n------------------------")

    if Manga.site == "mangadex.org":
        Manga.check_groups()


def chapter_info_get(Manga):
    '''Calls the get_info() of the manga objects'''
    Manga.ch_info = []
    for ch in Manga.wanted:
        print(f"Checking: Chapter {ch}")
        status = Manga.get_info(ch)
        if status is not True:
            print(f"\nSomething went wrong! \n{status}")


def downloader(manga_objects):
    '''Downloads the images in the proper directories'''

    for Manga in manga_objects:

        if not Manga.manga_dir.is_dir():
            Manga.manga_dir.mkdir()

        # Goes ever every chapter
        for ch in Manga.ch_info:
            print(f"\nDownloading {Manga.series_title} - {ch['name']}"
                  "\n------------------------")

            ch_dir = Manga.manga_dir / ch["name"]
            ch_dir.mkdir()

            # Goes over every page using a generator
            page_info = page_gen(Manga, ch)
            for image_name, link in page_info:

                content = download(link, Manga.scraper)

                if not content:
                    print("Failed to get image, skipping to next chapter")
                    failed_text = f"{Manga.series_title} - {ch['name']}"
                    download.failed.append(failed_text)
                    break

                with open(ch_dir / image_name, "wb") as f:
                    for chunk in content.iter_content(1024):
                        f.write(chunk)


def counter_timer(func):
    def wrapper(link, scraper):
        before = time.time()
        difference = before - wrapper.last_get_time
        if difference < 0.5:
            time.sleep(0.5 - difference)
        content = func(link, scraper)
        after = time.time()
        wrapper.last_get_time = after
        wrapper.count += 1
        wrapper.time += after - before
        return content
    wrapper.count = 0
    wrapper.time = 0
    wrapper.last_get_time = 0
    wrapper.failed = []
    return wrapper


@counter_timer
def download(link, scraper):
    try:
        if scraper:
            content = scraper.get(link, stream=True, timeout=5)
        else:
            content = requests.get(link, stream=True, timeout=5)
    except requests.Timeout:
        return False
    return content


def download_info_print():
    '''Prints the summary of the download'''
    if download.count:
        m, s = divmod(round(download.time), 60)
        if m > 0:
            timing = f"{m:02}:{s:02}"
        else:
            timing = f"{s} second(s)"
        print("\n------------------------\n"
              f"Finished downloading {download.count} pages in {timing}!"
              "\n------------------------")
    if download.failed:
        print("\nFailed downloads:")
        [print(f) for f in download.failed]


def page_gen(Manga, ch):
    '''A generator that yields a tuple with the page name and link'''
    for n, link in enumerate(ch["pages"]):
        base_name = f"{Manga.series_title} - {ch['name']} -"
        extension = f"Page {n}{Path(link).suffix}"

        if ch["title"]:
            title = f"{html.unescape(ch['title'])} -"
            image_name = " ".join([base_name, title, extension])
        else:
            image_name = " ".join([base_name, extension])

        # Replaces a "/" in titles to something usable
        image_name = image_name.replace("/", "╱")
        print(f"Page {n}")
        yield (image_name, link)


if __name__ == '__main__':
    main()
