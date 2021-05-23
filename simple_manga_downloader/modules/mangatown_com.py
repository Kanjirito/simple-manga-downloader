import re

import requests
from bs4 import BeautifulSoup

from ..utils import clean_up_string, request_exception_handler
from .manga import BaseManga


class Mangatown(BaseManga):
    base_link = "https://www.mangatown.com/"
    session = requests.Session()
    site_re = re.compile(r"https?://www\.mangatown\.com/manga/[^\s/]*")

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
        r = self.session.get(self.manga_link, timeout=5, allow_redirects=False)
        r.raise_for_status()
        if r.status_code == 302:
            return "HTTP code error: 404 Client Error"
        soup = BeautifulSoup(r.text, "html.parser")

        if self.series_title is None:
            title = soup.find(class_="title-top").string
            self.series_title = clean_up_string(title)
        if title_return:
            return True

        thumb = soup.find(class_="detail_info")
        if thumb:
            self.covers = {self.series_title: thumb.img["src"]}

        self.data = soup.find(class_="chapter_list").find_all("li")[::-1]
        return True

    def get_chapters(self):
        """
        Gets the list of available chapters
        """
        for chapter in self.data:
            chapter_link = f"{self.base_link}{chapter.find('a')['href']}"
            try:
                if chapter.find("span")["class"] != ["time"]:
                    chapter_title = chapter.find("span").text
                    if chapter_title == "new":
                        chapter_title = None
                else:
                    chapter_title = None
            except KeyError:
                chapter_title = None

            reg = re.compile(r"c(\d\d\d[\.\d*]*)")
            num = reg.search(chapter_link).group(1)

            try:
                ch_num = int(num)
            except ValueError:
                ch_num = float(num)

            if ch_num in self.chapters:
                inp = self.ask_for_chapter_number(chapter_title, taken=True, num=ch_num)
                if inp is False:
                    continue
                else:
                    num = inp

            self.chapters[ch_num] = {
                "link": chapter_link,
                "title": clean_up_string(chapter_title),
            }
        return True

    @request_exception_handler
    def get_info(self, ch):
        """Gets the needed data abut the chapters from the site"""

        r = self.session.get(self.chapters[ch]["link"], timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find(class_="page_select").find_all("option")
        pages = [f"{self.base_link}{p['value']}" for p in links if "Featured" not in p]

        image_links = []
        for page in pages:
            page_r = self.session.get(page, timeout=5)
            page_r.raise_for_status()
            page_soup = BeautifulSoup(page_r.text, "html.parser")
            img_link = page_soup.find(id="image")["src"]
            image_links.append(f"https:{img_link}")

        self.chapters[ch]["pages"] = image_links
        return True
