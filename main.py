#!/bin/env python3
from modules.mangadex_org import Manga
from config_parser import Config
import argparse
import os
import time
import html


def main():
    config = Config()
    args = parser()
    mode = args.subparser_name
    if mode == "down":
        down_mode(args, config)
    elif mode == "conf":
        conf_mode(args, config)
    elif mode == "update":
        update_mode(config)


def get_id(input):
    if "/" in input:
        ID = input.split("/")[4]
    else:
        ID = input
    return ID


def parser():
    '''Parses the arguments'''
    parser = argparse.ArgumentParser()

    # Subparsers for the conifg and download functionality
    subparsers = parser.add_subparsers(dest="subparser_name", required=True)
    parser_conf = subparsers.add_parser("conf", help="Program will be in the config edit mode")
    parser_down = subparsers.add_parser("down", help="Program will be in the download mode")
    subparsers.add_parser("update", help="Program will download new chapters based on the config")

    # Parser for download mode
    parser_down.add_argument("input")
    # parser.add_argument("-d", "--directory")
    group = parser_down.add_mutually_exclusive_group()
    group.add_argument("-r", "--range", help="Accepts two chapter numbers, both ends are inclusive. \"1 15\"", nargs=2)
    group.add_argument("-s", "--selection", help="Accepts multiple chapters \"2 10 25\"", nargs="+")
    group.add_argument("-l", "--latest", action='store_true')

    # Parser for config mode
    parser_conf.add_argument("-a", "--add-tracked", help="Adds manga to the tracked", dest="add")
    parser_conf.add_argument("-r", "--remove-tracked", help="Removes mangda from tracked", dest="remove")
    parser_conf.add_argument("-c", "--clear-tracked", help="Clears the tracked list",
                             action="store_true")
    parser_conf.add_argument("-d", "--default", help="Resets the config to defaults",
                             action="store_true")
    parser_conf.add_argument("-l", "--list-tracked", help="Lists all of the tracked shows",
                             action="store_true", dest="list")

    args = parser.parse_args()
    return args


def down_mode(args, config):
    # Gets the chapter selection
    if args.latest:
        selection = "NEW"
    elif args.range is not None:
        selection = ["range", args.range]
    elif args.selection is not None:
        selection = ["selection", args.selection]
    else:
        selection = "ALL"

    ID = get_id(args.input)
    manga = Manga(ID, config.manga_directory)
    manga.filter_wanted(selection)
    manga.get_info()
    manga_objects = [manga]
    download(manga_objects)


def conf_mode(args, config):
    if args.default:
        config.reset_config()
    elif args.clear_tracked:
        config.clear_tracked()

    if args.add is not None:
        add = args.add.split()
        config.add_tracked(add)
    if args.remove is not None:
        remove = args.remove.split()
        config.remove_tracked(remove)
    if args.list:
        config.list_tracked()
    config.save_config()


def update_mode(config):
    print(f"Updating {len(config.tracked_manga)} manga")
    manga_objects = []
    for ID in config.tracked_manga:
        manga = Manga(get_id(ID), config.manga_directory)
        manga.filter_wanted("ALL")
        manga.get_info()
        manga_objects.append(manga)

    total_num_ch = 0
    found_titles = {}
    for manga in manga_objects:
        if len(manga.wanted) > 0:
            title = manga.series_title
            wanted_count = len(manga.wanted)
            total_num_ch += wanted_count
            found_titles.setdefault(title, 0)
            found_titles[title] += wanted_count

    print("\nChecking complete!\n")
    if total_num_ch == 0:
        print(f"Found {total_num_ch} chapters ready to download.")
    elif total_num_ch > 0:
        print(f"Found {total_num_ch} chapter(s) ready to download for:")
        for title in found_titles:
            print(f"{title} - {found_titles[title]} chapter(s)")
        confirm = input(f"Start the download? [y to confirm/anything else to cancel]: ").lower()
        if confirm == "y":
            if download(manga_objects):
                print("Updated titles:")
                for title in found_titles:
                    print(f"{title} - {found_titles[title]} chapter(s)")

        else:
            print("Download cancelled")


def download(manga_objects):
    '''Downloands the image in the proper directories'''

    # Counts downloaded pages
    down_count = 0
    t1 = time.time()

    for manga in manga_objects:
        # Creates the manga folder
        if not os.path.isdir(manga.manga_dir):
            os.mkdir(manga.manga_dir)

        # Goes ever every chapter
        for ch in manga.ch_info:
            print(f"\nDownloading {manga.series_title} - {ch['name']}\n------------------------")

            # Creates the chapter folder
            ch_dir = os.path.join(manga.manga_dir, ch["name"])
            os.mkdir(ch_dir)

            # Goes over every page and saves it with 1 s delay
            for n, img in enumerate(ch["pages"]):
                img_url = ch["url"] + img
                if ch["title"] != "":
                    image_name = f"{manga.series_title} - {ch['name']} - {html.unescape(ch['title'])} - Page {n}{os.path.splitext(img)[1]}"
                else:
                    image_name = f"{manga.series_title} - {ch['name']} - Page {n}{os.path.splitext(img)[1]}"
                image_name = image_name.replace("/", "╱")
                print(f"Getting image: {img}")
                content = manga.scraper.get(img_url).content
                with open(os.path.join(ch_dir, image_name), "wb") as f:
                    f.write(content)
                down_count += 1
                time.sleep(0.5)
    if down_count > 0:
        t2 = time.time()
        delta = round(t2 - t1)
        m, s = divmod(delta, 60)
        if m > 0:
            timing = f"{m:02}:{s:02}"
        else:
            timing = f"{s:02} second(s)"
        print("------------------------\n" + f"Finished downloading {down_count} pages in {timing}!\n" + "------------------------")
    return True


if __name__ == '__main__':
    main()
