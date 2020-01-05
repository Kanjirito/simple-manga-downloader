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
        self.base_link = "http://ww7.heavenmanga.org/"
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

        self.series_title = soup.find(class_="name bigger").string
        if title_return:
            return True
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

        self.data = chapter_divs
        return True

    def get_chapters(self):
        '''
        Handles the chapter data by assigning chapter numbers
        '''
        for chapter in self.data:
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
