import requests
from ..decorators import request_exception_handler
from bs4 import BeautifulSoup


class Mangasee():
    def __init__(self, link, directory):
        self.session = requests.Session()
        self.site = "mangaseeonline.us"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://mangaseeonline.us"
        self.cover_url = None
        self.chapters = {}

    @property
    def manga_dir(self):
        return self.folder / self.series_title

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.chapters)

    @request_exception_handler
    def get_main(self, title_return=False):
        '''
        Gets the main manga info like title, cover url and chapter links
        title_return=True will only get the title and return
        '''
        r = self.session.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = soup.find(class_="SeriesName").string
        if title_return:
            return True
        thumb = soup.find(class_="leftImage")
        if thumb:
            self.cover_url = thumb.img["src"]

        self.data = soup.find_all(class_="list-group-item")
        return True

    def get_chapters(self):
        '''
        Handles the chapter data by assigning chapter numbers
        '''

        for chapter in self.data:
            num = chapter["chapter"]
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = chapter["href"].replace("-page-1", "")

            self.chapters[num] = {"link": link,
                                  "title": None}
        return True

    @request_exception_handler
    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''

        pages_link = f"{self.base_link}{self.chapters[ch]['link']}"

        r = self.session.get(pages_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        img_containers = soup.find_all(class_="fullchapimage")
        pages = [div.contents[0]["src"] for div in img_containers]

        self.chapters[ch]["pages"] = pages
        return True
