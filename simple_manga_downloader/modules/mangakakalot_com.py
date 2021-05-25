import re

import requests
from bs4 import BeautifulSoup

from ..models import BaseManga
from ..utils import clean_up_string


class Mangakakalot(BaseManga):
    _base_url = "https://mangakakalot.com"
    _session = requests.Session()
    _session.headers.update({"Referer": _base_url})
    _site_regex = re.compile(r"https?://mangakakalot\.com/?(?P<id>(?:manga/)?[^\s/]+)")
    _chapter_regex = re.compile(r"[\w:]* (\d+[\.\d]*)")
    _title_regex = re.compile(r"\d ?: (.*)")

    @property
    def manga_url(self):
        return f"{self._base_url}/{self._id}"

    def _get_main(self, title_return=False):
        r = self._session.get(self.manga_url, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        if "Sorry, the page you have requested cannot be found" in r.text:
            return "HTTP code error: 404 Client Error"

        if self._title is None:
            title = soup.find(class_="manga-info-text").find("h1").text
            self._title = clean_up_string(title)
        if title_return:
            return True

        thumb = soup.find(class_="manga-info-pic")
        if thumb:
            self._covers = {self._title: thumb.img["src"]}

        self.data = soup.find_all(class_="row")[1:][::-1]
        return True

    def _get_chapters(self):
        for chapter in self.data:
            a_div = chapter.find("a")

            result = self._chapter_regex.search(a_div.text)
            if result is None:
                continue

            num = result.group(1)
            try:
                num = int(num)
            except ValueError:
                num = float(num)
            link = a_div["href"]

            title_result = self._title_regex.search(a_div.text)
            if title_result:
                title = title_result.group(1)
            else:
                title = None

            if num in self._chapters:
                inp = self.ask_for_chapter_number(title, taken=True, num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            self._chapters[num] = {
                "link": link,
                "title": clean_up_string(title),
            }
        return True

    def _get_info(self, ch):
        link = self.chapters[ch]["link"]

        r = self._session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        reader = soup.find(class_="container-chapter-reader")

        pages = [image["src"] for image in reader.find_all("img")]

        self._chapters[ch]["pages"] = pages
        return True
