import requests
from bs4 import BeautifulSoup
import re


class Mangakakalot:
    def __init__(self, link, directory):
        self.scraper = None
        self.site = "mangakakalot.com"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://mangakakalot.com"

    def get_chapters(self, title_return):
        '''Gets the list of available chapters
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = requests.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        self.series_title = soup.find(class_="manga-info-text").find("h1").text
        self.manga_dir = self.folder / self.series_title
        if title_return:
            return True

        found_chapters = soup.find_all(class_="row")[1:]

        self.chapters = {}
        for chapter in found_chapters:
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

            self.chapters[num] = {"link": link,
                                  "title": title}
        return True

    def get_info(self, ch):
        '''Gets the needed data abut the chapters from the site'''
        link = self.chapters[ch]["link"]

        r = requests.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        reader = soup.find(id="vungdoc")

        pages = [image["src"] for image in reader.find_all("img")]

        self.chapters[ch]["pages"] = pages
        return True
