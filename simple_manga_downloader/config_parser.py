import json
import os
from pathlib import Path

from .modules.manga import BaseManga
from .utils import ask_confirmation, ask_number, clean_up_string

DEFAULT_REPLACEMENT_RULES = {
    "/": "",
    "\\": "",
    ":": "",
    ".": "",
    "<": "",
    ">": "",
    "?": "",
    "*": "",
    "|": "",
}

LANG_CODES = {
    "ar": "Arabic",
    "bn": "Bengali",
    "bg": "Bulgarian",
    "my": "Burmese",
    "ca": "Catalan",
    "zh": "Chinese (Simplified)",
    "zh-hk": "Chinese (Traditional)",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "de": "German",
    "el": "Greek",
    "he": "Hebrew",
    "hi": "Hindi",
    "hu": "Hungarian",
    "id": "Indonesian",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "lt": "Lithuanian",
    "ms": "Malay",
    "mn": "Mongolian",
    "no": "Norwegian",
    "NULL": "Other (Some releases have no language specified)",
    "fa": "Persian",
    "pl": "Polish",
    "pt-br": "Portuguese (Brazil)",
    "pt": "Portuguese (Portugal)",
    "ro": "Romanian",
    "ru": "Russian",
    "sh": "Serbo-Croatian",
    "es": "Spanish (Spain)",
    "es-la": "Spanish (Latin America)",
    "sv": "Swedish",
    "th": "Thai",
    "tr": "Turkish",
    "uk": "Ukrainian",
    "vi": "Vietnamese",
}


class Config:
    def __init__(self, custom_conf):
        self.status = False
        self.home = Path.home()
        if custom_conf:
            self.config_path = Path(custom_conf).resolve()
        elif os.getenv("XDG_CONFIG_HOME"):
            self.config_path = (
                Path(os.getenv("XDG_CONFIG_HOME")) / "SMD" / "SMD_conf.json"
            )
        else:
            self.config_path = self.home / ".config" / "SMD" / "SMD_conf.json"

        self.load_config()

    def __bool__(self):
        return self.status

    def load_config(self):
        """
        Loads the config if present, uses defaults if missing setting
        """
        if self.config_path.is_file():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except json.decoder.JSONDecodeError as e:
                print("\nConfig is invalid JSON. Fix or remove it.")
                print(f'"{e}"')
                print(f'Config located at: "{self.config_path}"')
                return
        else:
            config = {}

        default_dir = self.home / "Manga"
        self.manga_directory = Path(
            config.get("manga_directory", default_dir)
        ).resolve()
        self.tracked_manga = config.get("tracking", {})
        if not isinstance(self.tracked_manga, dict):
            print("Tracked manga is invalid, should be dict")
            return

        self.covers = config.get("covers", False)
        if not isinstance(self.covers, bool):
            print("Covers setting is invalid, should be true or false")
            return

        self.lang_code = config.get("lang_code", "en").lower()
        if not self.check_language_code(self.lang_code):
            return

        try:
            self.download_timeout = int(config.get("page_download_timeout", 5))
        except ValueError:
            print("Timeout setting is not a valid number, should be integer")
            return
        if self.download_timeout < 1:
            print("Timeout setting is invalid, can't be less than 1")
            return

        self.replacement_rules = config.get(
            "character_replacement_rules", DEFAULT_REPLACEMENT_RULES
        )
        if not isinstance(self.replacement_rules, dict):
            print("Replacement rules are invalid, should be dictionary (Key: value)")
            return

        self.data_saver = config.get("data_saver", False)
        if not isinstance(self.data_saver, bool):
            print("Data saver setting is invalid, should be true or false")
            return

        self.status = True

    def add_tracked(self, manga):
        """Adds manga to the tracked list"""
        current_title = manga.series_title
        manga_link = manga.manga_link

        tracked, message = self.check_if_manga_in_tracked(manga_link)

        if tracked:
            if message != current_title:
                print(f'Already tracking "{current_title}" as "{message}"')
            else:
                print(f'Already tracking  "{current_title}"')
        else:
            self.tracked_manga[current_title] = manga_link
            print(f"Added to tracked:  {current_title}")

    def remove_tracked(self, delete):
        """
        Removes manga from the tracked dict
        delete is a list of elements to remove
        """
        if not self.tracked_manga:
            print("Nothing to remove")
            return

        to_remove = set()
        for d in delete:
            tracked, message = self.check_if_manga_in_tracked(d)
            if tracked:
                to_remove.add(message)
            else:
                print(message)

        for r in to_remove:
            del self.tracked_manga[r]
            print(f"Removed from tracked: {r}")

    def check_if_manga_in_tracked(self, to_check):
        """
        Checks if given to_check is in the tracked list
        to_check can be an index of a tracked manga, title of a manga,
        link of a manga
        Returns a tuple of a bool and string, if to_check was found in
        tracked list returns (True, "series title") if it wasn't found
        returns (False, "why it failed message")
        """

        if to_check in self.tracked_manga:
            return (True, to_check)
        elif "/" in to_check:
            module = BaseManga.find_matching_module(to_check)
            if module:
                to_check = module.clean_up_link(to_check)

            for key, value in self.tracked_manga.items():
                if to_check in value:
                    return (True, key)
            else:
                return (False, f'Link not tracked: "{to_check}"')
        else:
            try:
                index = int(to_check)
                if 0 < index <= len(self.tracked_manga):
                    return (True, list(self.tracked_manga)[index - 1])
                else:
                    return (False, f'Index out of range: "{index}"')
            except ValueError:
                return (False, f'Not a tracked index, link or title: "{to_check}"')

    def change_dir(self, dire):
        """Changes the manga download directory"""
        path = Path(dire).resolve()
        self.manga_directory = path
        print(f'Manga download directory changed to : "{path}"')

    def clear_tracked(self):
        """Clears the tracked shows"""
        if ask_confirmation("Are you sure you want to clear tracked manga?"):
            self.tracked_manga = {}
            print("Tracked cleared")

    def reset_config(self):
        """Resets the config to the defaults"""
        if ask_confirmation(
            "Are you sure you want to reset the config file to the defaults?"
        ):
            self.manga_directory = self.home / "Manga"
            self.tracked_manga = {}
            self.covers = False
            self.lang_code = "en"
            self.download_timeout = 5
            self.replacement_rules = DEFAULT_REPLACEMENT_RULES
            self.data_saver = False
            print("Config was reset")

    def change_position(self, verbose):
        if len(self.tracked_manga) < 2:
            print("Less than 2 manga tracked")
            return
        self.list_tracked(verbose)

        select = ask_number(
            "Which manga do you want to move?", min_=1, max_=len(self.tracked_manga)
        )
        if select:
            select -= 1
        else:
            return
        move_index = ask_number(
            "Where do you want to move it?", min_=1, max_=len(self.tracked_manga)
        )
        if move_index:
            move_index -= 1
        else:
            return

        keys = list(self.tracked_manga)
        get = keys.pop(select)
        keys.insert(move_index, get)
        self.tracked_manga = {k: self.tracked_manga[k] for k in keys}

        print(f'Entry "{get}" moved to position {move_index + 1}')

    def change_manga_title(self, verbose):
        if not self.tracked_manga:
            print("No manga tracked")
            return None

        self.list_tracked(verbose)
        to_rename = ask_number(
            "Which manga do you want to rename?", min_=1, max_=len(self.tracked_manga)
        )
        if to_rename:
            to_rename -= 1
        else:
            return None

        new_name = input("New name: ")
        if not new_name:
            print("New name empty, aborting")
            return None
        new_name = clean_up_string(new_name)

        new_tracked_dict = {}
        for (n, (key, value)) in enumerate(self.tracked_manga.items()):
            if n == to_rename:
                old_name = key
                new_tracked_dict[new_name] = value
            else:
                new_tracked_dict[key] = value

        self.tracked_manga = new_tracked_dict
        print(f'Manga "{old_name}" was renamed to "{new_name}"\n')
        return (old_name, new_name)

    def list_tracked(self, verbose):
        """Lists the tracked manga"""
        if not self.tracked_manga:
            print("No shows tracked!")
            return
        print("\nCurrently tracked manga:")
        for n, manga in enumerate(self.tracked_manga.items(), 1):
            print(f"{n}. {manga[0]}")
            if verbose:
                print(manga[1])
        print()

    def toogle_covers(self):
        if self.covers:
            self.covers = False
            print("Cover download turned off!")
        else:
            self.covers = True
            print("Cover download turned on!")

    def toogle_data_saver(self):
        if self.data_saver:
            self.data_saver = False
            print("Data saver turned off")
        else:
            self.data_saver = True
            print("Data saver turned on")

    def print_config(self):
        print("\nConfig path:")
        print(self.config_path)
        print("\nManga download path:")
        print(self.manga_directory)
        print("\nCovers:")
        print(self.covers)
        print("\nMangadex language code:")
        print(self.lang_code)
        print("\nPage download timeout (s):")
        print(self.download_timeout)
        print("\nData saver:")
        print(self.data_saver)
        self.print_replacement_rules()
        print()

    def change_lang(self, code):
        new_code = code.lower()
        cur_code = self.lang_code.lower()
        if new_code != cur_code:
            if self.check_language_code(new_code):
                self.lang_code = code
                code_desc = LANG_CODES[new_code]
                print(f'Language changed to "{new_code}" - {code_desc}')
        else:
            print(f'"{new_code}" already set as current language')

    @staticmethod
    def check_language_code(code):
        """
        Checks if the given language code is a valid, returns bool
        """
        if code in LANG_CODES:
            return True
        else:
            print(f'Invalid language code: "{code}"')
            print('Use "SMD conf --list_lang" to list available codes')
            return False

    def list_lang(self):
        """
        Prints all of the language codes
        """
        print("Available language codes:")
        for code, desc in LANG_CODES.items():
            print(f'"{code}" - {desc}')

    def change_timeout(self, seconds):
        """
        Changes the download timeout to given seconds
        """

        if seconds <= 0:
            print("Value must be bigger than 0!")
            return
        self.download_timeout = seconds
        print(f"Timeout changed to {seconds} seconds!")

    def save_config(self):
        config = {
            "manga_directory": str(self.manga_directory),
            "covers": self.covers,
            "lang_code": self.lang_code,
            "page_download_timeout": self.download_timeout,
            "data_saver": self.data_saver,
            "character_replacement_rules": self.replacement_rules,
            "tracking": self.tracked_manga,
        }
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            print(f"Can't save config because {self.config_path.parent} is a file!")
            return 1

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
        return 0

    def reset_replacement_rules(self):
        """Resets the replacement rules to the default"""
        self.replacement_rules = DEFAULT_REPLACEMENT_RULES
        print("Replacement rules have been reset to defaults")

    def print_replacement_rules(self):
        print("\nCharacter replacement rules:")
        for char, rule in self.replacement_rules.items():
            print(f'"{char}" -> "{rule}"')

    def add_replacemnt_rule(self, args):
        """Sets replacement rule for character"""
        char = args[0]
        if len(args) > 1:
            replacement = " ".join(args[1::])
        else:
            replacement = ""

        if len(char) != 1:
            print("Can only set rules for single characters")
        else:
            if char in self.replacement_rules:
                confirm = ask_confirmation(
                    f'Character "{char}" is already replaced with "{self.replacement_rules[char]}", '
                    f'overwrite with "{replacement}"?'
                )
                if confirm:
                    self.replacement_rules[char] = replacement
                    print(f'Replacement for "{char}" set as: "{replacement}"')
                else:
                    print("Aborting")
            else:
                self.replacement_rules[char] = replacement
                print(f'Replacement for "{char}" set as: "{replacement}"')

    def remove_replacemnt_rule(self, char):
        """Removes a replacement rule for character"""
        if char in self.replacement_rules:
            del self.replacement_rules[char]
            print(f'Rule for "{char}" removed')
        else:
            print(f'No rule for "{char}"')
