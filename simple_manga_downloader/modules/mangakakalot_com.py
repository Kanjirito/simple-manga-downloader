import re

import requests
from bs4 import BeautifulSoup

from ..utils import clean_up_string, request_exception_handler
from .manga import BaseManga


class Mangakakalot(BaseManga):
    base_link = "https://mangakakalot.com"
    session = requests.Session()
    session.headers.update({"Referer": base_link})
    site_re = re.compile(r"https?://mangakakalot\.com/\S*")

    def __init__(self, link, title=None):
        if title:
            self.series_title = clean_up_string(title)
        else:
            self.series_title = None
        self.manga_link = link
        self.covers = {}
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
        if "Sorry, the page you have requested cannot be found" in r.text:
            return "HTTP code error: 404 Client Error"

        if self.series_title is None:
            title = soup.find(class_="manga-info-text").find("h1").text
            self.series_title = clean_up_string(title)
        if title_return:
            return True

        thumb = soup.find(class_="manga-info-pic")
        if thumb:
            self.covers = {self.series_title: thumb.img["src"]}

        self.data = soup.find_all(class_="row")[1:][::-1]
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """
        for chapter in self.data:
            a_div = chapter.find("a")

            reg = re.compile(r"[\w:]* (\d+[\.\d]*)")
            result = reg.search(a_div.text)
            if result is None:
                continue

            num = result.group(1)
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = a_div["href"]

            title_reg = re.compile(r"\d ?: (.*)")
            title_result = title_reg.search(a_div.text)
            if title_result:
                title = title_result.group(1)
            else:
                title = None

            if num in self.chapters:
                inp = self.ask_for_chapter_number(title, taken=True, num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            self.chapters[num] = {
                "link": link,
                "title": clean_up_string(title),
            }
        return True

    @request_exception_handler
    def get_info(self, ch):
        """Gets the needed data abut the chapters from the site"""
        link = self.chapters[ch]["link"]

        r = self.session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        reader = soup.find(class_="container-chapter-reader")

        pages = [image["src"] for image in reader.find_all("img")]

        self.chapters[ch]["pages"] = pages
        return True
