import cfscrape
from bs4 import BeautifulSoup
import re
from ..decorators import request_exception_handler


class Heavenmanga:
    def __init__(self, link, directory):
        self.session = cfscrape.create_scraper()
        self.site = "heavenmanga.org"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://ww4.heavenmanga.org/"
        self.cover_url = None

    @request_exception_handler
    def get_chapters(self, title_return=False):
        '''Gets the list of available chapters
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = self.session.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = soup.find(class_="name bigger").string
        if title_return:
            return True
        self.manga_dir = self.folder / self.series_title
        thumb = soup.find(alt="Cover Image")
        if thumb:
            self.cover_url = thumb["src"]

        chapter_divs = soup.find_all(class_="two-rows go-border")

        # Loop that looks for the next page button, break if not found
        while True:
            next_page_button = soup.find(id="chapterList"
                                         ).find(class_="next page-numbers")
            if next_page_button:
                next_page = next_page_button["href"]
            else:
                break

            page = self.session.get(next_page, timeout=5)
            page.raise_for_status()
            soup = BeautifulSoup(page.text, "html.parser")
            chapter_divs += soup.find_all(class_="two-rows go-border")

        self.chapters = {}
        for chapter in chapter_divs:
            a_div = chapter.find("a")
            chapter_link = a_div["href"]

            reg = re.compile(r"(Chap (\d+[\.\d]*))")
            result = reg.search(a_div.text)
            if result is None:
                continue
            num = result.group(2)

            try:
                ch_num = int(num)
            except ValueError:
                ch_num = float(num)

            self.chapters[ch_num] = {"link": chapter_link,
                                     "title": None}
        return True

    @request_exception_handler
    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''
        link = self.chapters[ch]["link"]
        r = self.session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        viewer = soup.find("center")
        pages = [img["src"] for img in viewer.find_all("img")]

        # The site has sometimes broken chapters
        # Getting the first one to check if they work
        test = self.session.get(pages[0], stream=True, timeout=5)
        test.raise_for_status()
        self.chapters[ch]["pages"] = pages
        return True
