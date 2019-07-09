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
        manga = Mangadex(link, CONFIG.manga_directory)
    elif "mangaseeonline.us" in link:
        manga = Mangasee(link, CONFIG.manga_directory)
    return manga


def parser():
    '''Parses the arguments'''
    parser = argparse.ArgumentParser()

    # Sub-parsers for the config and download functionality
    subparsers = parser.add_subparsers(dest="subparser_name", required=True)
    parser_conf = subparsers.add_parser("conf",
                                        help="Program will be in the config edit mode")
    parser_down = subparsers.add_parser("down",
                                        help="Program will be in the download mode")
    subparsers.add_parser("update",
                          help="Program will download new chapters based on the config")

    # Parser for download mode
    parser_down.add_argument("input", nargs="*")
    # parser.add_argument("-d", "--directory")
    group = parser_down.add_mutually_exclusive_group()
    group.add_argument("-r", "--range",
                       help="Accepts two chapter numbers,"
                       "both ends are inclusive. \"1 15\"", nargs=2)
    group.add_argument("-s", "--selection",
                       help="Accepts multiple chapters \"2 10 25\"", nargs="+")
    group.add_argument("-l", "--latest", action='store_true')

    # Parser for config mode
    parser_conf.add_argument("-a", "--add-tracked",
                             help="Adds manga to the tracked",
                             dest="add", nargs="*")
    parser_conf.add_argument("-r", "--remove-tracked",
                             help="Removes manga from tracked",
                             dest="remove", nargs="*")
    parser_conf.add_argument("-c", "--clear-tracked",
                             help="Clears the tracked list",
                             action="store_true")
    parser_conf.add_argument("-s", "--save-directory",
                             help="Changes the manga directory", dest="m_dir")
    parser_conf.add_argument("-d", "--default", help="Resets the config to defaults",
                             action="store_true")
    parser_conf.add_argument("-l", "--list-tracked",
                             help="Lists all of the tracked shows",
                             action="store_true", dest="list")
    parser_conf.add_argument("-m", "--modify-position",
                             help="Changes the position of tracked manga",
                             action="store_true", dest="position")

    args = parser.parse_args()
    return args


def down_mode():
    manga_objects = []
    for link in ARGS.input:
        manga = site_detect(link)
        filter_wanted(manga)
        manga_objects.append(manga)
    for manga in manga_objects:
        if manga.wanted:
            print("\n------------------------\n"
                  f"Getting chapter info about {manga.series_title}"
                  "\n------------------------")
            manga.get_info()
            download([manga])
        else:
            print()


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
        manga = site_detect(link)
        filter_wanted(manga, ignore=True)
        if manga.wanted:
            manga_objects.append(manga)

    # Goes over every manga and gets the chapter information
    # Keeps track of some information
    total_num_ch = 0
    found_titles = {}
    print("\n------------------------\n"
          "Getting info about chapters"
          "\n------------------------\n")
    for manga in manga_objects:
        if manga.wanted:
            print(f"Getting chapter info for \"{manga.series_title}\":")
            manga.get_info()
            print()
            total_num_ch += len(manga.ch_info)
            found_titles[manga.series_title] = [ch for ch in manga.ch_info]

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
        if download(manga_objects):
            print("Updated titles:")
            for title in found_titles:
                print(f"{title} - {len(found_titles[title])} chapter(s)")

    else:
        print("Download cancelled")


def filter_wanted(manga, ignore=None):
    '''Creates a list of chapters that fit the wanted criteria
    ignore=True skips argument checking, used for update mode'''
    if ignore is None:
        ignore = False

    chapter_list = list(manga.chapters)
    # Gets the chapter selection
    if ignore:
        filtered = chapter_list
    else:
        # If "oneshot" selection is ignored
        if len(manga.chapters) == 1 and not chapter_list[0]:
            filtered = chapter_list
        elif ARGS.latest:
            filtered = [max(chapter_list)]
        elif ARGS.range is not None:
            filtered = []
            a, b = [float(n) for n in ARGS.range]
            for ch in chapter_list:
                if a <= ch <= b:
                    filtered.append(ch)
        elif ARGS.selection is not None:
            filtered = []
            index = ARGS.selection
            for n in index:
                n = float(n)
                if n.is_integer():
                    n = int(n)
                if n in chapter_list:
                    filtered.append(n)
        else:
            filtered = chapter_list
    filtered.sort()

    # Checks if the chapters that fit the selection are already downloaded
    if not manga.manga_dir.is_dir():
        downloaded_chapters = None
    else:
        downloaded_chapters = os.listdir(manga.manga_dir)

    manga.wanted = []
    if downloaded_chapters is None:
        manga.wanted = filtered
    else:
        for n in filtered:
            chapter_name = f"Chapter {n}"
            if chapter_name not in downloaded_chapters:
                manga.wanted.append(n)

    print("\n------------------------\n"
          f"Found {len(manga.wanted)} wanted chapter(s) for {manga.series_title}"
          "\n------------------------")

    if manga.site == "mangadex.org":
        manga.check_groups()


def download(manga_objects):
    '''Downloads the images in the proper directories'''

    # Counts downloaded pages and times the download
    down_count = 0
    t1 = time.time()

    for manga in manga_objects:

        # Creates the manga folder
        if not manga.manga_dir.is_dir():
            manga.manga_dir.mkdir()

        # Goes ever every chapter
        for ch in manga.ch_info:
            print(f"\nDownloading {manga.series_title} - {ch['name']}"
                  "\n------------------------")

            # Creates the chapter folder
            ch_dir = manga.manga_dir / ch["name"]
            ch_dir.mkdir()

            # Goes over every page and saves it with a small delay
            for n, img in enumerate(ch["pages"]):
                if ch["title"] != "" and ch["title"] is not None:
                    image_name = f"{manga.series_title} - {ch['name']} - " \
                                 f"{html.unescape(ch['title'])} - " \
                                 f"Page {n}{Path(img).suffix}"
                else:
                    image_name = f"{manga.series_title} - {ch['name']} - " \
                                 f"Page {n}{Path(img).suffix}"

                # Replaces a "/" in titles to something usable
                image_name = image_name.replace("/", "╱")

                print(f"Page {n}")

                # If site uses cloud flare protection us the scraper
                # Otherwise uses requests
                if manga.cloud_flare:
                    content = manga.scraper.get(img, stream=True)
                else:
                    content = requests.get(img, stream=True)
                with open(ch_dir / image_name, "wb") as f:
                    for chunk in content.iter_content(1024):
                        f.write(chunk)
                down_count += 1
                time.sleep(0.4)
    if down_count:
        t2 = time.time()
        delta = round(t2 - t1)
        m, s = divmod(delta, 60)
        if m > 0:
            timing = f"{m:02}:{s:02}"
        else:
            timing = f"{s} second(s)"
        print("\n------------------------\n"
              f"Finished downloading {down_count} pages in {timing}!"
              "\n------------------------")
    return True


if __name__ == '__main__':
    main()
