import json
from pathlib import Path


class Config():
    def __init__(self, custom_conf):
        # Modified flag used for check if saving is needed
        self.modified = False
        self.exists = False
        self.directory = Path.home() / "Simple-Manga-Downloader"
        if custom_conf:
            self.config_path = Path(custom_conf)
        else:
            self.config_path = self.directory / "simple_manga_downloader_config.json"

        default_directory = self.directory / "Manga"
        # Loads the config or creates the base one if not present
        if self.config_path.is_file():
            self.exists = True
            with open(self.config_path, "r") as f:
                config = json.load(f)
        else:
            config = {"manga_directory": default_directory,
                      "tracking": {}}

        # Gets the useful data for easy access
        self.manga_directory = Path(config.get("manga_directory", default_directory))
        self.tracked_manga = config.get("tracking", [])
        self.covers = config.get("covers", False)

    def add_tracked(self, Manga):
        '''Adds manga to the tracked list'''
        if Manga.series_title not in self.tracked_manga:
            self.tracked_manga[Manga.series_title] = Manga.manga_link
            self.modified = True
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
        if to_remove:
            self.modified = True

    def change_dir(self, dire):
        '''Changes the manga download directory'''
        self.manga_directory = Path(dire).resolve()
        self.modified = True

    def clear_tracked(self):
        '''Clears the tracked shows'''
        confirm = input("Are you sure you want to clear tracked manga? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.tracked_manga = {}
            self.modified = True
            print("Tracked cleared")

    def reset_config(self):
        '''Resets the config to the defaults'''
        confirm = input("Are you sure you want to reset the config file to the defaults? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.manga_directory = self.directory.parent / "Manga"
            self.tracked_manga = {}
            self.covers = False
            self.modified = True
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

        self.modified = True
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
        self.modified = True

    def print_paths(self):
        if not self.exists:
            print("\nConfig file exists only in memory")
        print("\nConfig path:")
        print(self.config_path)
        print("\nManga download path:")
        print(self.manga_directory)
        print()

    def save_config(self):
        config = {"manga_directory": str(self.manga_directory),
                  "covers": self.covers,
                  "tracking": self.tracked_manga}
        try:
            self.directory.mkdir(parents=True)
        except FileExistsError:
            pass

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
