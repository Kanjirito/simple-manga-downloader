import requests
from bs4 import BeautifulSoup
import re


class Heavenmanga:
    def __init__(self, link, directory):
        self.scraper = None
        self.site = "heavenmanga.org"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://ww2.heavenmanga.org/"

    def get_chapters(self, title_return):
        '''Gets the list of available chapters
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        try:
            r = requests.get(self.manga_link, timeout=5)
        except requests.Timeout:
            return "Request Timeout"
        if r.status_code != 200:
            return r.status_code

        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = soup.find(class_="name bigger").string
        if title_return:
            return True
        self.manga_dir = self.folder / self.series_title

        chapter_divs = soup.find_all(class_="two-rows go-border")

        # Loop that looks for the next page button, break if not found
        while True:
            next_page_button = soup.find(id="chapterList"
                                         ).find(class_="next page-numbers")
            if next_page_button:
                next_page = next_page_button["href"]
            else:
                break

            try:
                page = requests.get(next_page, timeout=5)
            except requests.Timeout:
                return "Request Timeout"
            if page.status_code != 200:
                return page.status_code
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

    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''
        link = self.chapters[ch]["link"]
        try:
            r = requests.get(link, timeout=5)
        except requests.Timeout:
            return "Request Timeout"
        if r.status_code != 200:
            return r.status_code

        soup = BeautifulSoup(r.text, "html.parser")
        viewer = soup.find("center")
        pages = [img["src"] for img in viewer.find_all("img")]

        # The site has sometimes broken chapters
        # Getting the first one to check if they work
        try:
            test = requests.get(pages[0], stream=True, timeout=5)
        except (requests.ConnectionError, requests.Timeout):
            return f"Chapter is probably broken\n{link}\n"
        if not test:
            return f"Chapter is probably broken\n{link}\n"

        self.chapters[ch]["pages"] = pages
        return True
