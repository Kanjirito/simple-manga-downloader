import re

import requests
from bs4 import BeautifulSoup

from ..models import BaseManga
from ..utils import clean_up_string


class Mangatown(BaseManga):
    _base_url = "https://www.mangatown.com"
    _session = requests.Session()
    _site_regex = re.compile(r"https?://www\.mangatown\.com/manga/(?P<id>[^\s/]+)")
    _chapter_regex = re.compile(r"c(\d\d\d[\.\d*]*)")

    @property
    def manga_url(self):
        return f"{self._base_url}/manga/{self._id}"

    def _get_main(self, title_return=False):
        r = self._session.get(self.manga_url, timeout=5, allow_redirects=False)
        r.raise_for_status()
        if r.status_code == 302:
            return "HTTP code error: 404 Client Error"
        soup = BeautifulSoup(r.text, "html.parser")

        if self._title is None:
            title = soup.find(class_="title-top").string
            self._title = clean_up_string(title)
        if title_return:
            return True

        thumb = soup.find(class_="detail_info")
        if thumb:
            self._covers = {self._title: thumb.img["src"]}

        self.data = soup.find(class_="chapter_list").find_all("li")[::-1]
        return True

    def _get_chapters(self):
        for chapter in self.data:
            chapter_link = f"{self._base_url}{chapter.find('a')['href']}"
            try:
                if chapter.find("span")["class"] != ["time"]:
                    chapter_title = chapter.find("span").text
                    if chapter_title == "new":
                        chapter_title = None
                else:
                    chapter_title = None
            except KeyError:
                chapter_title = None

            num = self._chapter_regex.search(chapter_link).group(1)

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

            self._chapters[ch_num] = {
                "link": chapter_link,
                "title": clean_up_string(chapter_title),
            }
        return True

    def _get_info(self, ch):
        r = self._session.get(self._chapters[ch]["link"], timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find(class_="page_select").find_all("option")
        pages = [f"{self._base_url}{p['value']}" for p in links if "Featured" not in p]

        image_links = []
        for page in pages:
            page_r = self._session.get(page, timeout=5)
            page_r.raise_for_status()
            page_soup = BeautifulSoup(page_r.text, "html.parser")
            img_link = page_soup.find(id="image")["src"]
            image_links.append(f"https:{img_link}")

        self._chapters[ch]["pages"] = image_links
        return True
