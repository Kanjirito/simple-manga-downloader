import json
import os


class Config():
    def __init__(self):
        self.config_path = os.path.normpath(os.path.expanduser("~/.config/simple_manga_downloader_config.json"))

        # Loads the config or creates the base one if not present
        if os.path.isfile(self.config_path):
            with open(self.config_path, "r") as f:
                config = json.load(f)
        else:
            config = {"manga_directory": "/media/Dysk na media/Manga",
                      "tracking": []}

        # Gets the useful data for easy access
        self.manga_directory = os.path.normpath(config["manga_directory"])
        self.tracked_manga = config["tracking"]

    def add_tracked(self, new):
        '''Adds manga to the tracked list
        Accepts only a list as a argument'''
        for s in new:
            if s not in self.tracked_manga:
                self.tracked_manga.append(s)
            else:
                print(f"Manga {s} already tracked")

    def remove_tracked(self, delete):
        '''Removes manga from the tracked list
        Accepts only a list as a argument'''
        for s in delete:
            if s in self.tracked_manga:
                self.tracked_manga.remove(s)
            else:
                print(f"Manga {s} not tracked")

    def change_dir(self, dire):
        '''Changes the manga download directory'''
        self.manga_directory = os.path.normpath(dire)

    def clear_tracked(self):
        '''Clears the tracked shows'''
        confirm = input("Are you sure you want to clear tracked manga? [y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.tracked_manga = []

    def reset_config(self):
        '''Resets the config to the defaults'''
        confirm = input("Are you sure you want to restore the config file to the defaults? [y to confirm/anything else to cancel]").lower()
        if confirm == "y":
            self.manga_directory = "/media/Dysk na media/Manga"
            self.tracked_manga = []

    def list_tracked(self):
        '''Lists the tracked manga'''
        if len(self.tracked_manga) == 0:
            print("No shows tracked!")
            return
        print("Currently tracked manga:")
        for s in self.tracked_manga:
            print(s)

    def save_config(self):
        config = {"manga_directory": self.manga_directory,
                  "tracking": self.tracked_manga}
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=4)
