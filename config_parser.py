import json
from pathlib import Path
import __main__


class Config():
    def __init__(self):
        # Modified flag used for check if saving is needed
        self.modified = False
        self.config_path = Path(__main__.__file__).parent.resolve() / "simple_manga_downloader_config.json"

        # Loads the config or creates the base one if not present
        if self.config_path.is_file():
            with open(self.config_path, "r") as f:
                config = json.load(f)
        else:
            self.modified = True
            config = {"manga_directory": self.config_path.parent / "Manga",
                      "tracking": []}

        # Gets the useful data for easy access
        self.manga_directory = Path(config["manga_directory"])
        self.tracked_manga = config["tracking"]

        # Creates manga download folder if not present
        try:
            self.manga_directory.mkdir(parents=True)
        except FileExistsError:
            pass

    def add_tracked(self, new):
        '''Adds manga to the tracked list
        Accepts only a list as a argument'''
        for s in new:
            # Simple input check
            if "mangadex.org" not in s and "mangaseeonline.us" not in s:
                print(f"Not a proper link:  {s}")
                continue
            if s not in self.tracked_manga:
                # Removes the unwanted "/chapters" from mangadex links
                self.tracked_manga.append(s.replace("/chapters", ""))
                self.modified = True
                print(f"Added to tracked:  {s}")
            else:
                print(f"Already tracked:  {s}")

    def remove_tracked(self, delete):
        '''Removes manga from the tracked list
        Accepts only a list as a argument'''
        delete.sort(reverse=True)
        for s in delete:
            try:
                s = int(s) - 1
                try:
                    removed = self.tracked_manga.pop(s)
                    self.modified = True
                    print(f"Removed from tracked:  {removed}")
                except IndexError:
                    print("Wrong index")
            except ValueError:
                s = s.replace("/chapters", "")
                if s in self.tracked_manga:
                    self.tracked_manga.remove(s)
                    self.modified = True
                    print(f"Removed from tracked:  {s}")
                else:
                    print(f"Not tracked:  {s}")

    def change_dir(self, dire):
        '''Changes the manga download directory'''
        self.manga_directory = Path(dire).resolve()
        self.modified = True

    def clear_tracked(self):
        '''Clears the tracked shows'''
        confirm = input("Are you sure you want to clear tracked manga? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.tracked_manga = []
            self.modified = True
            print("Tracked cleared")

    def reset_config(self):
        '''Resets the config to the defaults'''
        confirm = input("Are you sure you want to reset the config file to the defaults? "
                        "[y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.manga_directory = self.config_path.parent / "Manga"
            self.tracked_manga = []
            self.modified = True
            print("Config was reset")

    def change_order(self):
        if len(self.tracked_manga) < 2:
            print("Less than 2 manga tracked")
            return
        self.list_tracked()

        try:
            select = int(input("\nWhich manga do you want to move?: ")) - 1
        except ValueError:
            print("Not a number, aborting")
            return
        if select not in range(len(self.tracked_manga)):
            print("Selection out of index range, aborting")
            return
        else:
            try:
                move_index = int(input("Where do you want to move it?: ")) - 1
            except ValueError:
                print("Not a number, aborting")
                return
            if move_index not in range(len(self.tracked_manga)):
                print("Number out of index range, aborting")
            else:
                # Swaps the 2 elements using tuples
                get = self.tracked_manga[select], self.tracked_manga[move_index]
                self.tracked_manga[move_index], self.tracked_manga[select] = get
                self.modified = True
                print("Order changed")

    def list_tracked(self):
        '''Lists the tracked manga'''
        if not self.tracked_manga:
            print("No shows tracked!")
            return
        print("\nCurrently tracked manga:")
        for n, link in enumerate(self.tracked_manga, 1):
            print(f"{n}. {link}")
        print()

    def save_config(self):
        config = {"manga_directory": str(self.manga_directory),
                  "tracking": self.tracked_manga}
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
