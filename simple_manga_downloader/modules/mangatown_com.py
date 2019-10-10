import requests
from bs4 import BeautifulSoup
from ..decorators import request_exception_handler
import re


class Mangatown():
    def __init__(self, link, directory):
        self.session = requests.Session()
        self.site = "mangatown.com"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://www.mangatown.com/"
        self.cover_url = None

    @request_exception_handler
    def get_chapters(self, title_return=False):
        '''Gets the list of available chapters
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = self.session.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = soup.find(class_="title-top").string
        if title_return:
            return True
        thumb = soup.find(class_="detail_info")
        if thumb:
            self.cover_url = thumb.img["src"]
        self.manga_dir = self.folder / self.series_title

        chapters_soup = soup.find(class_="chapter_list").find_all("li")

        self.chapters = {}
        for chapter in chapters_soup:
            chapter_link = f"https:{chapter.find('a')['href']}"
            try:
                if chapter.find("span")["class"] != ["time"]:
                    chapter_title = chapter.find("span").text
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

            self.chapters[ch_num] = {"link": chapter_link,
                                     "title": chapter_title}
        return True

    @request_exception_handler
    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''

        r = self.session.get(self.chapters[ch]["link"], timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        links = soup.find(class_="page_select").find_all("option")
        pages = [f"https:{p['value']}" for p in links if "Featured" not in p]

        image_links = []
        for page in pages:
            page_r = self.session.get(page, timeout=5)
            page_r.raise_for_status()
            page_soup = BeautifulSoup(page_r.text, "html.parser")
            img_link = page_soup.find(id="image")["src"]
            image_links.append(img_link)

        # Saves the needed data
        self.chapters[ch]["pages"] = image_links
        return True
