import re

import requests
from bs4 import BeautifulSoup

from ..models import BaseManga
from ..utils import clean_up_string


class Manganelo(BaseManga):
    _base_url = "https://manganelo.com"
    _session = requests.Session()
    _session.headers.update({"Referer": _base_url})
    _site_regex = re.compile(r"https?://manganelo\.com/manga/(?P<id>[^\s/]+)")
    _chapter_regex = re.compile(r" (\d+\.?\d*)(?:: (.*))?")

    @property
    def manga_url(self):
        return f"{self._base_url}/manga/{self._id}"

    def _get_main(self, title_return=False):
        r = self._session.get(self.manga_url, timeout=5)
        r.raise_for_status()
        if "404 - PAGE NOT FOUND" in r.text:
            return "HTTP code error: 404 Client Error"
        soup = BeautifulSoup(r.text, "html.parser")

        if self._title is None:
            title = soup.find(class_="story-info-right").find("h1").text
            self._title = clean_up_string(title)
        if title_return:
            return True

        try:
            url = soup.find(class_="info-image").img["src"]
            self._covers = {self._title: url}
        except AttributeError:
            pass

        self.data = soup.find_all(class_="chapter-name text-nowrap")[::-1]
        return True

    def _get_chapters(self):
        for chapter in self.data:

            search_reg = self._chapter_regex.search(chapter.text)
            try:
                num = search_reg.group(1)
                title = search_reg.group(2)
                try:
                    num = int(num)
                except ValueError:
                    num = float(num)
            except AttributeError:
                title = chapter.text
                inp = self.ask_for_chapter_number(title)
                if inp is False:
                    continue
                else:
                    num = inp

            if num in self._chapters:
                inp = self.ask_for_chapter_number(title, taken=True, num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            link = chapter["href"]

            self._chapters[num] = {
                "link": link,
                "title": clean_up_string(title),
            }
        return True

    def _get_info(self, ch):
        link = self._chapters[ch]["link"]

        r = self._session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            pages = soup.find(class_="container-chapter-reader").find_all("img")
        except AttributeError:
            return "Failed to find reader, most likely server error"

        page_links = [p["src"] for p in pages]

        self._chapters[ch]["pages"] = page_links
        return True
