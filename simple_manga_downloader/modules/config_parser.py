import json
from pathlib import Path


class Config():
    def __init__(self, custom_conf):
        self.lang_codes = {
            "sa": "Arabic",
            "bd": "Bengali",
            "bg": "Bulgarian",
            "mm": "Burmese",
            "ct": "Catalan",
            "cn": "Chinese (Simple)",
            "hk": "Chinese (Traditional)",
            "cz": "Czech",
            "dk": "Danish",
            "nl": "Dutch",
            "gb": "English",
            "ph": "Filipino",
            "fi": "Finnish",
            "fr": "French",
            "de": "German",
            "gr": "Greek",
            "il": "Hebrew",
            "hu": "Hungarian",
            "id": "Indonesian",
            "it": "Italian",
            "jp": "Japanese",
            "kr": "Korean",
            "lt": "Lithuanian",
            "my": "Malay",
            "mn": "Mongolian",
            "ir": "Persian",
            "pl": "Polish",
            "br": "Portuguese (Brazil)",
            "pt": "Portuguese (Portugal)",
            "ro": "Romanian",
            "ru": "Russian",
            "rs": "Serbo-Croatian",
            "es": "Spanish (Spain)",
            "mx": "Spanish (Latin America)",
            "se": "Swedish",
            "th": "Thai",
            "tr": "Turkish",
            "ua": "Ukrainian",
            "vn": "Vietnamese",
        }
        self.status = False
        self.home = Path.home()
        if custom_conf:
            self.config_path = Path(custom_conf)
        else:
            self.config_path = self.home / ".config" / "SMD" / "SMD_conf.json"

        self.load_config()

    def __bool__(self):
        return self.status

    def load_config(self):
        '''
        Loads the config if present, uses defaults if missing setting
        '''
        if self.config_path.is_file():
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)
            except json.decoder.JSONDecodeError:
                print("\nCould not load config file! Fix or remove it!")
                print(f"Config located at: \"{self.config_path}\"")
                return
        else:
            config = {}

        default_dir = self.home / "Manga"
        self.manga_directory = Path(config.get("manga_directory", default_dir))
        self.tracked_manga = config.get("tracking", [])
        self.covers = config.get("covers", False)
        self.lang_code = config.get("lang_code", "gb")
        self.status = True

    def add_tracked(self, Manga):
        '''Adds manga to the tracked list'''
        if Manga.series_title not in self.tracked_manga:
            self.tracked_manga[Manga.series_title] = Manga.manga_link
            print(f"Added to tracked:  {Manga.series_title}")
        else:
            print(f"Already tracked:  {Manga.series_title}")

    def remove_tracked(self, delete):
        '''
        Removes manga from the tracked list
        Accepts only a list as an argument
        '''
        if not self.tracked_manga:
            print("Nothing to remove")
            return
        to_remove = set()
        for n in delete:
            if n in self.tracked_manga:
                to_remove.add(n)
            elif "/" in n:
                for key, value in self.tracked_manga.items():
                    if value == n:
                        to_remove.add(key)
                        break
                else:
                    print("Link not found")
            else:
                try:
                    index = int(n)
                    if 0 < index <= len(self.tracked_manga):
                        to_remove.add(list(self.tracked_manga)[index - 1])
                    else:
                        print("Index out of range")
                except ValueError:
                    print("Not an index, link or title")

        for r in to_remove:
            del self.tracked_manga[r]
            print(f"Removed from tracked: {r}")

    def change_dir(self, dire):
        '''Changes the manga download directory'''
        self.manga_directory = Path(dire).resolve()

    def clear_tracked(self):
        '''Clears the tracked shows'''
        confirm = input("Are you sure you want to clear tracked manga? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.tracked_manga = {}
            print("Tracked cleared")

    def reset_config(self):
        '''Resets the config to the defaults'''
        confirm = input("Are you sure you want to reset the config file to the defaults? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.manga_directory = self.home / "Manga"
            self.tracked_manga = {}
            self.covers = False
            self.lang_code = "gb"
            print("Config was reset")

    def change_position(self, verbose):
        if len(self.tracked_manga) < 2:
            print("Less than 2 manga tracked")
            return
        self.list_tracked(verbose)

        try:
            select = int(input("Which manga do you want to move?: ")) - 1
        except ValueError:
            print("Not a number, aborting")
            return
        if select not in range(len(self.tracked_manga)):
            print("Number out of index range, aborting")
            return
        try:
            move_index = int(input("Where do you want to move it?: ")) - 1
        except ValueError:
            print("Not a number, aborting")
            return
        if move_index not in range(len(self.tracked_manga)):
            print("Number out of index range, aborting")
            return

        keys = list(self.tracked_manga)
        get = keys.pop(select)
        keys.insert(move_index, get)
        self.tracked_manga = dict([(k, self.tracked_manga[k]) for k in keys])

        print(f"Entry \"{get}\" moved to {move_index + 1}")

    def list_tracked(self, verbose):
        '''Lists the tracked manga'''
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

    def print_paths(self):
        print("\nConfig path:")
        print(self.config_path)
        print("\nManga download path:")
        print(self.manga_directory)
        print("\nCovers:")
        print(self.covers)
        print("\nMangadex language code:")
        print(self.lang_code)
        print()

    def change_lang(self, code):
        new_code = code.lower()
        cur_code = self.lang_code.lower()
        if new_code != cur_code:
            if new_code in self.lang_codes:
                self.lang_code = code
                code_desc = self.lang_codes[new_code]
                print(f"Language changed to \"{new_code}\" - {code_desc}")
            else:
                print(f"Invalid language code: \"{new_code}\"")
                print("Use \"SMD conf --list_lang\" to list available codes")
        else:
            print(f"\"{new_code}\" already set as current language")

    def list_lang(self):
        print("Available language codes:")
        for code, desc in self.lang_codes.items():
            print(f"\"{code}\" - {desc}")

    def save_config(self):
        config = {"manga_directory": str(self.manga_directory),
                  "covers": self.covers,
                  "lang_code": self.lang_code,
                  "tracking": self.tracked_manga}
        try:
            self.config_path.parent.mkdir(parents=True)
        except FileExistsError:
            pass

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
