import re

import requests
from bs4 import BeautifulSoup

from ..utils import clean_up_string, request_exception_handler
from .manga import BaseManga


class MangaPageName(BaseManga):
    base_link = "https://site.com"
    session = requests.Session()
    site_re = re.compile(r"regex for site")

    def __init__(self, link, title=None):
        if title:
            self.title = clean_up_string(title)
        else:
            self.series_title = None
        self.manga_link = link
        self.covers = None
        self.chapters = {}

    @request_exception_handler
    def get_main(self, title_return=False):
        """
        Gets the main manga info like title, cover url and chapter links
        title_return=True will only get the title and return
        """
        r = self.session.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.covers = {self.series_title: "get cover here"}

        self.series_title = "find title"
        if title_return:
            return True

        self.data = "finding all chapter links in the soup"
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """
        for chapter in self.data:

            num = "finding chapter number in soup"
            title = "get title"
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = "finding chapter link in soup"

            if num in self.chapters:
                inp = self.ask_for_chapter_number(title, taken=True, num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            self.chapters[num] = {
                "link": link,
                "title": None,
            }
        return True

    @request_exception_handler
    def get_info(self, ch):
        """Gets the needed data abut the chapters from the site"""
        link = self.chapters[ch]["link"]

        r = self.session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        pages = ["list of found image links"]

        self.chapters[ch]["pages"] = pages
        return True
