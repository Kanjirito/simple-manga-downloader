#!/usr/bin/env python3
from . import modules
from .config_parser import Config
from .arg_parser import parse_arguments
from . import __version__
from . import utils
from pathlib import Path
import shutil
import imghdr
import time
import requests
import sys


def main():
    global ARGS
    global CONFIG
    ARGS = parse_arguments()
    CONFIG = Config(ARGS.custom_cfg)
    if not CONFIG:
        print("Loading config failed")
        return 1
    utils.REPLACEMENT_RULES = CONFIG.replacement_rules
    modules.set_mangadex_language(CONFIG.lang_code)
    modules.set_md_at_home(CONFIG.md_at_home)

    try:
        mode = ARGS.subparser_name

        if mode == "down":
            main_pipeline(ARGS.input)
        elif mode == "update":
            main_pipeline(CONFIG.tracked_manga.values())
        elif mode == "conf":
            conf_mode()
        elif mode == "version":
            return version_mode()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected, stopping!")
    finally:
        exit_code = CONFIG.save_config()
    return exit_code


def site_detect(link, tracked_allow=True):
    """Detects the site and creates a proper manga object"""

    # Checks if manga was given a custom name or if it has a tracked title
    if hasattr(ARGS, "name") and ARGS.name:
        title = " ".join(ARGS.name)
    elif tracked_allow:
        (if_tracked, message) = CONFIG.check_if_manga_in_tracked(link)
        if if_tracked:
            title = message
            if message == link or link.isdigit():
                link = CONFIG.tracked_manga[title]
        else:
            title = None
    else:
        title = None

    matched = modules.match_module(link, title)
    if matched:
        return matched
    else:
        msg = f"Wrong link: \"{link}\""
        line = make_line(msg)
        print(line)
        print(msg)
        print(line)
        return False


def get_cover(Manga):
    """
    Gets the cover for given Manga
    Skips if cover already saved
    """
    try:
        files = {file.stem for file in Manga.manga_dir.iterdir() if file.is_file()}
    except FileNotFoundError:
        files = set()

    to_download = {filename: url for filename, url in Manga.cover_url.items()
                   if filename not in files}
    if to_download:
        Manga.manga_dir.mkdir(parents=True, exist_ok=True)
    else:
        return

    print("--------------\n"
          "Getting covers")
    successful = 0
    for filename, url in to_download.items():
        no_ext = Manga.manga_dir / filename
        status = download_image(url, Manga.session, no_ext)
        if status is True:
            successful += 1
        else:
            print(status)
    print(f"\nGot {successful} cover(s)\n"
          "--------------\n")


def version_mode():
    """Version mode of the downloader """
    print(f"SMD (simple-manga-downloader) v{__version__}")

    if ARGS.version_check:
        check = check_for_update()
        if check is not True:
            print("Failed to check version!")
            print(check)
            return 1
    return 0


@utils.request_exception_handler
def check_for_update():
    """Checks for new versions using the PyPI API"""
    try:
        from pkg_resources import parse_version
    except ModuleNotFoundError:
        return "Can't check version because pkg_resources not installed"

    r = requests.get("https://pypi.org/pypi/simple-manga-downloader/json")
    r.raise_for_status()
    info = r.json()
    latest_version = info["info"]["version"]
    if parse_version(latest_version) > parse_version(__version__):
        date = info["releases"][latest_version][0]["upload_time"].split("T")[0]
        print(f"New version available: v{latest_version} ({date})")
    else:
        print("No new versions found")
    return True


def conf_mode():
    """Config mode for the downloader"""
    if ARGS.default:
        CONFIG.reset_config()
    elif ARGS.clear_tracked:
        CONFIG.clear_tracked()

    if ARGS.add_to_tracked:
        for link in ARGS.add_to_tracked:
            print()
            Manga = site_detect(link, tracked_allow=False)
            if Manga is False:
                continue
            title = Manga.get_main(title_return=True)
            if title is True:
                CONFIG.add_tracked(Manga)
            else:
                print(f"{title} for:\n{link}")
    elif ARGS.remove_from_tracked:
        CONFIG.remove_tracked(ARGS.remove_from_tracked)
    if ARGS.list_tracked:
        CONFIG.list_tracked(ARGS.verbose)
    if ARGS.manga_down_directory:
        CONFIG.change_dir(ARGS.manga_down_directory)
    if ARGS.modify_tracked_position:
        CONFIG.change_position(ARGS.verbose)
    if ARGS.change_name:
        renamed = CONFIG.change_manga_title(ARGS.verbose)
        if renamed:
            rename_old_files(renamed[0], renamed[1])
    if ARGS.toggle_covers:
        CONFIG.toogle_covers()
    if ARGS.change_lang:
        CONFIG.change_lang(ARGS.change_lang)
    if ARGS.list_lang:
        CONFIG.list_lang()
    if ARGS.timeout is not None:
        CONFIG.change_timeout(ARGS.timeout)
    if ARGS.md_at_home:
        CONFIG.toogle_md_at_home()
    if ARGS.replacement_reset:
        CONFIG.reset_replacement_rules()
    if ARGS.rule_add:
        CONFIG.add_replacemnt_rule(ARGS.rule_add)
    elif ARGS.rule_remove:
        CONFIG.remove_replacemnt_rule(ARGS.rule_remove)
    if ARGS.rule_print:
        CONFIG.print_replacement_rules()
    if ARGS.print_config:
        CONFIG.print_config()


def main_pipeline(links):
    """Takes a list of manga links and does all of the required stuff"""

    if not links:
        print("\nNo manga to download!")
        return

    print("\n------------------------\n"
          f"    Getting {len(links)} manga"
          "\n------------------------")

    if ARGS.custom_down_dire:
        path = Path(ARGS.custom_down_dire).resolve()
    else:
        path = CONFIG.manga_directory
    modules.set_download_directory(path)

    if ARGS.check_only or ARGS.ignore_input:
        modules.toggle_check_only()

    ready = []
    total_num_ch = 0
    found_titles = {}
    for link in links:
        Manga = site_detect(link)
        if not Manga:
            continue

        status = handle_manga(Manga)
        if status:
            ready.append(Manga)
            total_num_ch += len(Manga)
            chapter_list = []
            for ch in Manga.chapters:
                title = Manga.chapters[ch]["title"]
                if title:
                    save_text = f"{ch} - \"{title}\""
                else:
                    save_text = f"{ch}"
                chapter_list.append(save_text)
            found_titles[Manga.series_title] = chapter_list
        else:
            continue
    print("\n-----------------------------\n"
          "All manga checking complete!"
          "\n-----------------------------\n")
    if not total_num_ch:
        print("Found 0 chapters ready to download.")
        return

    print("Chapters to download:")
    for title, chapter in found_titles.items():
        print(f"{title} - {len(chapter)} chapter(s):")
        for ch in chapter:
            print(f"    Chapter {ch}")

    print(f"\n{total_num_ch} chapter(s) ready to download")

    if ARGS.check_only:
        return

    if ARGS.ignore_input:
        confirm = True
    else:
        confirm = utils.ask_confirmation("Start the download?")
    if confirm:
        downloader(ready)
    else:
        print("Aborting!")


def handle_manga(Manga):
    """
    Handles all stuff related to a single Manga
    returns True if everything fine
    """
    main_status = Manga.get_main()
    if main_status is not True:
        print("\nSomething went wrong!"
              f"\n{main_status}\n{Manga.manga_link}")
        return False

    message = f"Checking \"{Manga.series_title}\""
    line_break = make_line(message)
    print(f"\n{line_break}\n{message}\n{line_break}\n")

    if CONFIG.covers and Manga.cover_url:
        get_cover(Manga)

    Manga.get_chapters()
    filter_wanted(Manga)

    if not Manga.chapters:
        print("Found 0 wanted chapters")
        return False

    message2 = f"Getting info about {len(Manga)} wanted chapter(s)"
    line_break2 = make_line(message2)
    print(f"{message2}\n{line_break2}")
    return chapter_info_get(Manga)


def filter_wanted(Manga):
    """Filters the chapters dict to match the criteria"""

    chapter_list = list(Manga.chapters)
    chapter_list.sort()

    if ARGS.subparser_name == "update":
        wanted = (ch for ch in chapter_list)
    else:
        wanted = filter_selection(chapter_list)

    filtered = filter_downloaded(Manga.manga_dir, wanted)

    Manga.chapters = {k: Manga.chapters[k] for k in filtered}


def make_line(string):
    """Returns a string of "-" with the same length as the given string"""
    return "-" * len(string)


def filter_selection(chapter_list):
    """A generator that yields wanted chapters based on selection"""

    if ARGS.latest:
        try:
            yield max(chapter_list)
        except ValueError:
            pass
    elif ARGS.range:
        a = ARGS.range[0]
        b = ARGS.range[1]
        for ch in chapter_list:
            if a <= ch <= b and ch not in ARGS.exclude:
                yield ch
    elif ARGS.selection:
        to_get = sorted(ARGS.selection)
        for n in to_get:
            if n.is_integer():
                n = int(n)
            if n in chapter_list and n not in ARGS.exclude:
                yield n
    else:
        for ch in chapter_list:
            if ch not in ARGS.exclude:
                yield ch


def filter_downloaded(manga_dir, wanted):
    """Filters the "wanted" based on what is already downloaded"""
    if not manga_dir.is_dir():
        filtered = list(wanted)
    else:
        filtered = []
        directory_contents = {item.name for item in manga_dir.iterdir()
                              if item.is_dir()}
        for n in wanted:
            chapter_name = f"Chapter {n}"
            if chapter_name not in directory_contents:
                filtered.append(n)
    return filtered


def chapter_info_get(Manga):
    """Calls the get_info() of the manga objects"""
    for ch in list(Manga.chapters):
        print(f"    Chapter {ch}")
        status = Manga.get_info(ch)
        if status is not True:
            print(f"{status}")
            del Manga.chapters[ch]
            print()
    if Manga.chapters:
        return True
    else:
        return False


def downloader(manga_objects):
    """Downloads the images in the proper directories"""

    start_time = time.time()
    page_total = 0
    failed = {}
    success = {}

    for Manga in manga_objects:
        Manga.manga_dir.mkdir(parents=True, exist_ok=True)

        for ch in Manga.chapters:
            status = get_chapter(Manga, ch)
            page_total += status[0]

            title = Manga.chapters[ch]["title"]
            if title:
                to_app = f"    Chapter {ch} - \"{title}\""
            else:
                to_app = f"    Chapter {ch}"
            if status[1]:
                fail_list = failed.setdefault(Manga.series_title, [])
                fail_list.append(to_app)
            else:
                succ_list = success.setdefault(Manga.series_title, [])
                succ_list.append(to_app)

    total_time = time.time() - start_time
    download_summary(page_total, failed, success, total_time)


@utils.limiter(0.5)
@utils.request_exception_handler
def download_image(link, session, no_ext):
    """
    Download function, gets the image from the link, limited by wrapper
    no_ext = save target Path object with no file extension
    """
    content = session.get(link, stream=True,
                          timeout=CONFIG.download_timeout)

    content.raise_for_status()
    file_type = imghdr.what("", h=content.content)
    if not file_type:
        header = content.headers["Content-Type"]
        file_type = header.split("/")[1].split(";")[0]

    with open(f"{no_ext}.{file_type}", "wb") as f:
        for chunk in content.iter_content(None):
            f.write(chunk)

    return True


def download_summary(count, failed, success, total_time):
    """Prints the summary of the download"""
    if count:
        m, s = divmod(round(total_time), 60)
        if m > 0:
            timing = f"{m:02}:{s:02}"
        else:
            timing = f"{s} second(s)"
        message = f"Finished downloading {count} pages in {timing}!"
        line_break = make_line(message)
        print(f"\n{line_break}\n{message}\n{line_break}")

    if success:
        msg = "Successful downloads:"
        print(f"\n{msg}\n{make_line(msg)}")
        for win, win_list in success.items():
            print(f"{win}:")
            for w in win_list:
                print(w)
    if failed:
        msg = "Failed downloads:"
        print(f"\n{msg}\n{make_line(msg)}")
        for fail, fail_list in failed.items():
            print(f"{fail}:")
            for f in fail_list:
                print(f)


def get_chapter(Manga, num):
    """
    Downloads the pages for the given chapter
    Returns number of downloaded pages and failed bool
    num = number of the chapter to get
    """

    count = 0
    failed = False
    title = Manga.series_title
    chapter_name = f"Chapter {num}"
    print(f"\nDownloading {title} - {chapter_name}"
          "\n------------------------")

    ch_dir = Manga.manga_dir / chapter_name
    ch_dir.mkdir()

    try:
        name_gen = page_name_gen(title,
                                 Manga.chapters[num],
                                 chapter_name)
        for page_name, link in name_gen:
            no_ext = ch_dir / page_name
            image = download_image(link, Manga.session, no_ext)
            if image is not True:
                print("Failed to get image, skipping to next chapter")
                print(image)
                failed = True
                count = 0
                shutil.rmtree(ch_dir)
                break
            else:
                count += 1
    except KeyboardInterrupt:
        shutil.rmtree(ch_dir)
        raise KeyboardInterrupt
    return (count, failed)


def page_name_gen(manga_title, data, chapter_name):
    """A generator that yields a tuple with the page name and link"""
    for n, link in enumerate(data["pages"]):
        base_name = f"{manga_title} - {chapter_name} -"
        page_string = f"Page {n}"

        if data["title"]:
            title = f"{data['title']} -"
            image_name = " ".join([base_name, title, page_string])
        else:
            image_name = " ".join([base_name, page_string])

        print(f"    {page_string}")
        yield (image_name, link)


def rename_old_files(old_title, new_title):
    if old_title == new_title:
        return False
    manga_dir = CONFIG.manga_directory / old_title
    if not manga_dir.is_dir():
        return False

    if (manga_dir.parent / new_title).exists():
        confirm = utils.ask_confirmation(
            "Do you want to rename the exisitng files?\n"
            "Existing file/directory found, this action will overwrite it. "
            "Are you sure you want to continue?")
        pass
    else:
        confirm = utils.ask_confirmation("Do you want to rename the exisitng files?")
    if not confirm:
        return False

    for chapter_dir in manga_dir.iterdir():
        if chapter_dir.is_dir():
            for page in chapter_dir.iterdir():
                new_file_name = page.name.replace(old_title, new_title, 1)
                page.rename(page.parent / new_file_name)
        else:
            new_file_name = chapter_dir.name.replace(old_title, new_title, 1)
            chapter_dir.rename(chapter_dir.parent / new_file_name)
    manga_dir.rename(manga_dir.parent / new_title)
    print("Files have been renamed")
    return True


if __name__ == '__main__':
    sys.exti(main())
