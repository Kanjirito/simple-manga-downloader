#!/usr/bin/env python3
from .modules import Mangadex
from .modules import Mangasee
from .modules import Mangatown
from .modules import Heavenmanga
from .modules import Mangakakalot
from .modules import Config
from .decorators import limiter, request_exception_handler
from pathlib import Path
import argparse
import html
import os
import imghdr
import time


def main():
    args = parser()
    config = Config(args.custom_cfg)
    mode = args.subparser_name
    if mode == "down":
        main_pipeline(args.input, args, config)
    elif mode == "update":
        main_pipeline(config.tracked_manga.values(), args, config)
    elif mode == "conf":
        conf_mode(args, config)


def site_detect(link, args, config):
    '''
    Detects the site and creates a proper manga object
    '''
    try:
        custom = args.custom_dire
        if custom:
            path = custom
        else:
            path = config.manga_directory
    except AttributeError:
        path = config.manga_directory

    directory = Path(path)

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

    return Manga


def get_cover(Manga):
    '''
    Gets the cover for given Manga
    Skips if cover already saved
    '''
    try:
        for file in Manga.manga_dir.iterdir():
            if Manga.series_title in file.stem:
                return False
    except FileNotFoundError:
        pass

    Manga.manga_dir.mkdir(parents=True, exist_ok=True)
    no_ext = Manga.manga_dir / Manga.series_title

    return download_image(Manga.cover_url, Manga.session, no_ext)


def conf_mode(args, config):
    if args.default:
        config.reset_config()
    elif args.clear_tracked:
        config.clear_tracked()

    if args.add:
        for link in args.add:
            print()
            Manga = site_detect(link, args, config)
            if Manga is False:
                continue
            title = Manga.get_chapters(title_return=True)
            if title is True:
                config.add_tracked(Manga)
            else:
                print(f"{title} for:\n{link}")
    elif args.remove:
        config.remove_tracked(args.remove)
    if args.list:
        config.list_tracked(args.verbose)
    if args.m_dir:
        config.change_dir(args.m_dir)
    if args.position:
        config.change_position(args.verbose)
    if args.paths:
        config.print_paths()
    if args.cover:
        config.toogle_covers()

    if config.modified:
        config.save_config()


def main_pipeline(links, args, config):
    '''
    Takes a list of manga links and does all of the required stuff
    '''
    if not links:
        print("\nNo manga tracked!")
        return

    print("\n------------------------\n"
          f"    Getting {len(links)} manga"
          "\n------------------------")

    ready = []
    total_num_ch = 0
    found_titles = {}
    for link in links:
        Manga = site_detect(link, args, config)
        if not Manga:
            continue

        status = handle_manga(Manga, config.covers, args)
        if status:
            ready.append(Manga)
            total_num_ch += len(Manga.chapters)
            found_titles[Manga.series_title] = [ch for ch in Manga.chapters]
        else:
            continue
    print("\n-----------------------------\n"
          "All manga checking complete!"
          "\n-----------------------------\n")
    if not ready:
        print("Found 0 chapters ready to download.")
        return

    print(f"Chapters to download:")
    for title, chapter in found_titles.items():
        print(f"{title} - {len(chapter)} chapter(s):")
        for ch in chapter:
            print(f"    Chapter {ch}")

    print(f"\n{total_num_ch} chapter(s) ready to download")
    confirm = input(f"Start the download? "
                    "[y to confirm/anything else to cancel]: "
                    ).lower()
    if confirm == "y":
        downloader(ready)
    else:
        print("Aborting!")


def handle_manga(Manga, covers, args):
    '''
    Handles all stuff related to the Manga
    returns True if everything fine
    '''
    ch_status = Manga.get_chapters()
    if ch_status is not True:
        print("\nSomething went wrong!"
              f"\n{ch_status}\n{Manga.manga_link}")
        return False

    message = f"Checking \"{Manga.series_title}\""
    line_break = make_line(message)
    print(f"\n{line_break}\n{message}\n{line_break}\n")

    if covers and Manga.cover_url:
        cov = get_cover(Manga)
        if cov is True:
            print("-----------\n"
                  "Cover saved"
                  "\n-----------\n")
        elif cov:
            cov_line = make_line(cov)
            print(f"{cov_line}\n"
                  "Failed to get cover"
                  f"\n{cov}"
                  f"\n{cov_line}\n")
    filter_wanted(Manga, args)

    if not Manga.chapters:
        print("Found 0 wanted chapters")
        return False

    message2 = f"Getting info about {len(Manga.chapters)} wanted chapter(s)"
    line_break2 = make_line(message2)
    print(f"{message2}\n{line_break2}")
    return chapter_info_get(Manga)


def filter_wanted(Manga, args):
    '''
    Filters the chapters dict to match the criteria
    '''

    chapter_list = list(Manga.chapters)
    chapter_list.sort()

    if args.subparser_name == "update":
        wanted = (ch for ch in chapter_list)
    else:
        wanted = filter_selection(chapter_list, args)

    filtered = filter_downloaded(Manga.manga_dir, wanted)

    Manga.chapters = {k: Manga.chapters[k] for k in filtered}


def make_line(string):
    return "-" * len(string)


def filter_selection(chapter_list, args):
    '''A generator that yields wanted chapters based on selection'''

    if args.latest:
        yield max(chapter_list)
    elif args.range:
        a = args.range[0]
        b = args.range[1]
        for ch in chapter_list:
            if a <= ch <= b and ch not in args.exclude:
                yield ch
    elif args.selection:
        to_get = sorted(args.selection)
        for n in to_get:
            if n.is_integer():
                n = int(n)
            if n in chapter_list and n not in args.exclude:
                yield n
    else:
        for ch in chapter_list:
            if ch not in args.exclude:
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
    '''Calls the get_info() of the manga objects'''
    for ch in list(Manga.chapters):
        print(f"    Chapter {ch}")
        status = Manga.get_info(ch)
        if status is not True:
            print(f"{status}")
            del Manga.chapters[ch]
            print()
    return True


def downloader(manga_objects):
    '''Downloads the images in the proper directories'''

    start_time = time.time()
    page_total = 0
    failed = {}
    success = {}

    for Manga in manga_objects:
        Manga.manga_dir.mkdir(parents=True, exist_ok=True)

        for ch in Manga.chapters:
            status = get_chapter(Manga, ch)
            page_total += status[0]

            to_app = f"    Chapter {ch}"
            if status[1]:
                fail_list = failed.setdefault(Manga.series_title, [])
                fail_list.append(to_app)
            else:
                succ_list = success.setdefault(Manga.series_title, [])
                succ_list.append(to_app)

    total_time = time.time() - start_time
    download_summary(page_total, failed, success, total_time)


@limiter(0.5)
@request_exception_handler
def download_image(link, session, no_ext):
    '''
    Download function, gets the image from the link, limited by wrapper
    no_ext = save target Path object with no file extension
    '''
    content = session.get(link, stream=True, timeout=5)

    file_type = imghdr.what("", h=content.content)
    if not file_type:
        header = content.headers["Content-Type"]
        file_type = header.split("/")[1].split(";")[0]

    with open(f"{no_ext}.{file_type}", "wb") as f:
        for chunk in content.iter_content(None):
            f.write(chunk)

    return True


def download_summary(count, failed, success, total_time):
    '''Prints the summary of the download'''
    if count:
        m, s = divmod(round(total_time), 60)
        if m > 0:
            timing = f"{m:02}:{s:02}"
        else:
            timing = f"{s} second(s)"
        message = f"Finished downloading {count} pages in {timing}!"
        line_break = make_line(message)
        print(f"\n{line_break}\n{message}\n{line_break}")

    if failed:
        print("\nFailed downloads:")
        for fail, fail_list in failed.items():
            print(f"{fail}:")
            for f in fail_list:
                print(f)
    if success:
        print("\nSuccessfully downloaded:")
        for win, win_list in success.items():
            print(f"{win}:")
            for w in win_list:
                print(w)


def get_chapter(Manga, num):
    '''
    Downloads the pages for the given chapter
    Returns number of downloaded pages and failed bool
    num = number of the chapter to get
    '''

    count = 0
    failed = False
    title = Manga.series_title
    chapter_name = f"Chapter {num}"
    print(f"\nDownloading {title} - {chapter_name}"
          "\n------------------------")

    ch_dir = Manga.manga_dir / chapter_name
    ch_dir.mkdir()

    name_gen = page_name_gen(title,
                             Manga.chapters[num],
                             chapter_name)
    for page_name, link in name_gen:
        no_ext = ch_dir / page_name
        image = download_image(link, Manga.session, no_ext)
        if image is not True:
            print("Failed to get image, skipping to next chapter")
            failed = True
            break
        else:
            count += 1
    return (count, failed)


def page_name_gen(manga_title, data, chapter_name):
    '''A generator that yields a tuple with the page name and link'''
    for n, link in enumerate(data["pages"]):
        base_name = f"{manga_title} - {chapter_name} -"
        page_string = f"Page {n}"

        if data["title"]:
            title = f"{html.unescape(data['title'])} -"
            image_name = " ".join([base_name, title, page_string])
        else:
            image_name = " ".join([base_name, page_string])

        # Replaces a "/" in titles to something usable
        image_name = image_name.replace("/", "╱")
        print(f"    {page_string}")
        yield (image_name, link)


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
    parser_conf.add_argument("-t", "--clear-tracked",
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
    parser_conf.add_argument("-c", "--covers",
                             help="Toggles the cover download",
                             action="store_true",
                             dest="cover")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    main()
