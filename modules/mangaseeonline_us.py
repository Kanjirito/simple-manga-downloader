import requests
from bs4 import BeautifulSoup


class Mangasee():
    def __init__(self, link, directory):
        self.cloud_flare = False
        self.site = "mangaseeonline.us"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://mangaseeonline.us"

    def get_chapters(self):
        '''Gets the list of available chapters'''

        # Gets the main page
        try:
            r = requests.get(self.manga_link, timeout=5)
        except requests.Timeout:
            return "Request Timeout"
        if r.status_code != 200:
            return r.status_code

        # Creates the soup
        soup = BeautifulSoup(r.text, "html.parser")

        # Sets the series title and creates the manga_dir Path object
        self.series_title = soup.find(class_="SeriesName").string
        self.manga_dir = self.folder / self.series_title

        # Finds all of the chapters and creates the dict
        chapters = soup.find_all(class_="list-group-item")
        chapters.reverse()

        self.chapters = {}
        for chapter in chapters:
            num = chapter["chapter"]
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = chapter["href"].replace("-page-1", "")

            self.chapters[num] = {"name": f"Chapter {num}",
                                  "link": link,
                                  "title": None}
        return True

    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''

        # Gets the chapter page and makes the soup
        pages_link = f"{self.base_link}{self.chapters[ch]['link']}"
        try:
            r = requests.get(pages_link, timeout=5)
        except requests.Timeout:
            return "Request Timeout"
        if r.status_code != 200:
            return r.status_code
        soup = BeautifulSoup(r.text, "html.parser")

        # Finds the page links in the page and adds them to a list
        img_containers = soup.find_all(class_="fullchapimage")
        pages = [div.contents[0]["src"] for div in img_containers]

        # Saves the needed data
        self.ch_info.append({"name": self.chapters[ch]["name"],
                             "title": self.chapters[ch]["title"],
                             "pages": pages})
        return True
