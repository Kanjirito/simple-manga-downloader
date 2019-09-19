# Cloud flare
import cfscrape
import requests.exceptions

# No cloudflare
import requests

from bs4 import BeautifulSoup


class ClassName:
    def __init__(self, link, directory):
        self.scraper = None
        self.site = "site.com"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://site.com"

    def get_chapters(self, title_return):
        '''Gets the list of available chapters
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = requests.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = "find title"
        self.manga_dir = self.folder / self.series_title
        if title_return:
            return True

        found_chapters = "finding all chapter links in the soup"

        self.chapters = {}
        for chapter in found_chapters:

            num = "finding chapter number in soup"
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = "finding chapter link in soup"

            self.chapters[num] = {"link": link,
                                  "title": None}
        return True

    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''
        link = self.chapters[ch]["link"]

        r = requests.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        pages = ["list of found image links"]

        self.chapters[ch]["pages"] = pages
        return True
