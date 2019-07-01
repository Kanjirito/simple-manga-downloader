import sys
import requests
from bs4 import BeautifulSoup


class Mangasee():
    def __init__(self, link, directory):
        self.cloud_flare = False
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://mangaseeonline.us"
        self.get_chapters()

    def get_chapters(self):
        '''Gets the list of available chapters'''

        # Gets the main page
        r = requests.get(self.manga_link)
        try:
            r.raise_for_status()
        except Exception as e:
            sys.exit(e)

        # Creates the soup
        soup = BeautifulSoup(r.text, "html.parser")

        # Sets the series title and creates the manga_dir Path object
        self.series_title = soup.find(class_="SeriesName").string
        self.manga_dir = self.folder / self.series_title

        # Finds all of the chapters and creates the dict
        chapters = reversed(soup.find_all(class_="list-group-item"))

        self.chapters = {}
        for chapter in chapters:
            num = chapter["chapter"]
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            chapter_name = f"Chapter {num}"
            link = chapter["href"].replace("-page-1", "")

            self.chapters[num] = {"name": chapter_name,
                                  "link": link,
                                  "title": None}
        print("\n------------------------\n" + f"Found {len(self.chapters)} uploaded chapter(s) for {self.series_title}\n" + "------------------------")

    def get_info(self):
        '''Gets the needed data abut the chapters from the site'''

        # The dict used by the download function
        self.ch_info = []

        # Goes over every wanted chapter
        for ch in self.wanted:
            chapter_name = f"Chapter {ch}"
            print(f"Checking: {chapter_name}")

            # Gets the chapter page and makes the soup
            pages_link = f"{self.base_link}{self.chapters[ch]['link']}"
            r = requests.get(pages_link)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            # Finds the page links in the page and adds them to a list
            img_containers = soup.find_all(class_="fullchapimage")
            pages = [div.contents[0]["src"] for div in img_containers]

            # Saves the needed data
            self.ch_info.append({"name": self.chapters[ch]["name"],
                                 "title": self.chapters[ch]["title"],
                                 "pages": pages})
