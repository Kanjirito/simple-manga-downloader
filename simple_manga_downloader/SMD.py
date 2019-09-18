#!/usr/bin/env python3
from .modules.mangadex_org import Mangadex
from .modules.mangaseeonline_us import Mangasee
from .modules.mangatown_com import Mangatown
from .modules.heavenmanga_org import Heavenmanga
from .modules.mangakakalot_com import Mangakakalot
from .modules.config_parser import Config
from pathlib import Path
import argparse
import requests
import time
import html
import os
import imghdr

ARGS = None
CONFIG = None


def main():
    global ARGS
    global CONFIG
    ARGS = parser()
    CONFIG = Config(ARGS.custom_cfg)
    mode = ARGS.subparser_name
    if mode == "down":
        down_mode()
    elif mode == "conf":
        conf_mode()
    elif mode == "update":
        update_mode()


def site_detect(link, title_return=False, directory=None):
    '''Detects the site and creates a proper manga object'''
    if directory is None:
        directory = CONFIG.manga_directory

    if "mangadex.org" in link:
        site = Mangadex
    elif "mangaseeonline.us" in link:
        site = Mangasee
    elif "heavenmanga.org" in link:
        site = Heavenmanga
    elif "mangatown.com" in link:
        site = Mangatown
    elif "mangakakalot.com" in link:
        site = Mangakakalot
    else:
        print(f"Wrong link: \"{link}\"")
        return False

    Manga = site(link, directory)
    status = get_handler(Manga.manga_link, Manga.get_chapters, title_return)
    if status:
        return Manga
    else:
        return False


def get_handler(manga_link, func, arg):
    '''
    Runs the given func with given arg and handles all request exceptions
    Returns True if nothing failed, prints error and returns False otherwise
    '''
    try:
        status = func(arg)
    except requests.Timeout:
        status = "Request Timeout"
    except requests.ConnectionError:
        status = "Connection Error"
    except requests.HTTPError:
        status = "HTTP code error"
    except requests.RequestException as e:
        status = f"A unexpected problem {e}"

    if status is not True:
        print(f"\nSomething went wrong! \n{status}\n{manga_link}")
        return False
    else:
        return True


def parser():
    '''Parses the arguments'''
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--custom",
                        dest="custom_cfg",
                        default=None)

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
    parser_down.add_argument("-d", "--directory",
                             dest="custom_dire",
                             default=None,
                             help="Custom path for manga download")
    parser_down.add_argument("-e", "--exclude",
                             help="Chapters to exclude \"1 5 10 15\"",
                             nargs="+",
                             type=float,
                             default=[])
    group = parser_down.add_mutually_exclusive_group()
    group.add_argument("-r", "--range",
                       help="Accepts two chapter numbers,"
                       "both ends are inclusive. \"1 15\"",
                       nargs=2,
                       type=float)
    group.add_argument("-s", "--selection",
                       help="Accepts multiple chapters \"2 10 25\"",
                       nargs="+",
                       type=float)
    group.add_argument("-l", "--latest",
                       action='store_true')

    # Parser for config mode
    parser_conf.add_argument("-a", "--add-tracked",
                             help="Adds manga to the tracked",
                             dest="add",
                             nargs="+")
    parser_conf.add_argument("-r", "--remove-tracked",
                             help="Removes manga from tracked",
                             dest="remove",
                             nargs="+")
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
    parser_conf.add_argument("-v", "--verbose",
                             help="Used with -l or -m to print links",
                             action="store_true",
                             dest="verbose")
    parser_conf.add_argument("-p", "--paths",
                             help="Print config and manga path",
                             action="store_true",
                             dest="paths")

    args = parser.parse_args()
    return args


def down_mode():
    if ARGS.custom_dire:
        directory = Path(ARGS.custom_dire)
    else:
        directory = CONFIG.manga_directory

    manga_objects = []
    for link in ARGS.input:
        Manga = site_detect(link, directory=directory)
        if not Manga:
            continue
        filter_wanted(Manga)
        if Manga.chapters:
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

    if ARGS.add:
        for link in ARGS.add:
            Manga = site_detect(link, title_return=True)
            if Manga is False:
                continue
            CONFIG.add_tracked(Manga)
    elif ARGS.remove:
        CONFIG.remove_tracked(ARGS.remove)
    if ARGS.list:
        CONFIG.list_tracked(ARGS.verbose)
    if ARGS.m_dir:
        CONFIG.change_dir(ARGS.m_dir)
    if ARGS.position:
        CONFIG.change_position(ARGS.verbose)
    if ARGS.paths:
        CONFIG.print_paths()

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
    for link in CONFIG.tracked_manga.values():
        Manga = site_detect(link)
        if not Manga:
            continue
        filter_wanted(Manga, ignore=True)
        if Manga.chapters:
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
            total_num_ch += len(Manga.chapters)
            found_titles[Manga.series_title] = [ch for ch in Manga.chapters]

    print("------------------------\nChecking complete!\n")
    if not total_num_ch:
        print("Found 0 chapters ready to download.")
        return

    print(f"Chapters to download:")
    for title, chapter in found_titles.items():
        print(f"{title} - {len(chapter)} chapter(s):")
        for ch in chapter:
            print(f"    Chapter {ch}")
    print(f"{total_num_ch} chapter(s) ready to download")
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


def filter_wanted(Manga, ignore=False):
    '''Creates a list of chapters that fit the wanted criteria
    ignore=True skips argument checking, used for update mode'''

    chapter_list = list(Manga.chapters)
    chapter_list.sort()

    if ignore:
        wanted = (ch for ch in chapter_list)
    else:
        wanted = filter_selection(chapter_list)

    filtered = filter_downloaded(Manga.manga_dir, wanted)

    print("\n------------------------\n"
          f"Found {len(filtered)} wanted chapter(s) for {Manga.series_title}"
          "\n------------------------")

    Manga.chapters = {k: Manga.chapters[k] for k in filtered}
    if Manga.site == "mangadex.org":
        Manga.check_groups()


def filter_selection(chapter_list):
    '''A generator that yields wanted chapters based on selection'''

    if ARGS.latest:
        yield max(chapter_list)
    elif ARGS.range:
        a = ARGS.range[0]
        b = ARGS.range[1]
        for ch in chapter_list:
            if a <= ch <= b and ch not in ARGS.exclude:
                yield ch
    elif ARGS.selection:
        for n in ARGS.selection:
            if n.is_integer():
                n = int(n)
            if n in chapter_list and n not in ARGS.exclude:
                yield n
    else:
        for ch in chapter_list:
            if ch not in ARGS.exclude:
                yield ch


def filter_downloaded(manga_dir, wanted):
    '''Filters the "filtered" based on what is already downloaded'''
    if not manga_dir.is_dir():
        filtered = list(wanted)
    else:
        filtered = []
        for n in wanted:
            chapter_name = f"Chapter {n}"
            if chapter_name not in os.listdir(manga_dir):
                filtered.append(n)
    return filtered


def chapter_info_get(Manga):
    '''Calls the get_info() of the manga objects and handles the exceptions'''
    for ch in list(Manga.chapters):
        print(f"Checking: Chapter {ch}")
        status = get_handler(Manga, Manga.get_info, ch)
        if not status:
            del Manga.chapters[ch]
            print()


def downloader(manga_objects):
    '''Downloads the images in the proper directories'''

    for Manga in manga_objects:

        try:
            Manga.manga_dir.mkdir(parents=True)
        except FileExistsError:
            pass

        # Goes ever every chapter
        for ch in Manga.chapters.items():
            chapter_name = f"Chapter {ch[0]}"

            print(f"\nDownloading {Manga.series_title} - {chapter_name}"
                  "\n------------------------")

            ch_dir = Manga.manga_dir / chapter_name
            ch_dir.mkdir()

            # Goes over every page using a generator
            page_info = page_gen(Manga, ch, chapter_name)
            for image_name, link in page_info:

                image = download(link, Manga.scraper)
                if not image:
                    print("Failed to get image, skipping to next chapter")
                    failed_text = f"{Manga.series_title} - {chapter_name}"
                    download.failed.append(failed_text)
                    break

                file_type = imghdr.what("", h=image.content)
                if not file_type:
                    header = image.headers["Content-Type"]
                    file_type = header.split("/")[1].split(";")[0]
                full_image_name = f"{image_name}.{file_type}"

                with open(ch_dir / full_image_name, "wb") as f:
                    for chunk in image.iter_content(1024):
                        f.write(chunk)


def counter_timer(func):
    '''Decorator for the download function that keeps track of stats and
    times the download'''
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
    '''Download function, gets the image from the link, limited by wrapper'''
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
        for f in download.failed:
            print(f)


def page_gen(Manga, ch, chapter_name):
    '''A generator that yields a tuple with the page name and link'''
    for n, link in enumerate(ch[1]["pages"]):
        base_name = f"{Manga.series_title} - {chapter_name} -"
        page_string = f"Page {n}"

        if ch[1]["title"]:
            title = f"{html.unescape(ch[1]['title'])} -"
            image_name = " ".join([base_name, title, page_string])
        else:
            image_name = " ".join([base_name, page_string])

        # Replaces a "/" in titles to something usable
        image_name = image_name.replace("/", "╱")
        print(f"Page {n}")
        yield (image_name, link)


if __name__ == '__main__':
    main()
