import requests
import re
from bs4 import BeautifulSoup
from ..utils import request_exception_handler, clean_up_string, ask_number
from .manga import BaseManga


class Manganelo(BaseManga):
    base_link = "https://manganelo.com/"
    session = requests.Session()
    session.headers.update({"Referer": base_link})
    site_re = re.compile(r"https?://manganelo\.com/manga/\S*")

    def __init__(self, link, title=None):
        if title:
            self.series_title = clean_up_string(title)
        else:
            self.series_title = None
        self.manga_link = link
        self.cover_url = None
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

        if self.series_title is None:
            title = soup.find(class_="story-info-right").find("h1").text
            self.series_title = clean_up_string(title)
        if title_return:
            return True

        try:
            url = soup.find(class_="info-image").img["src"]
            self.cover_url = {self.series_title: url}
        except AttributeError:
            pass

        self.data = soup.find_all(class_="chapter-name text-nowrap")
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """
        for chapter in self.data:

            search_reg = re.search(r" (\d+\.?\d*)(?:: (.*))?", chapter.text)
            try:
                num = search_reg.group(1)
                title = search_reg.group(2)
                try:
                    num = int(num)
                except ValueError:
                    num = float(num)

            except AttributeError:
                if self.check_only:
                    continue
                print(f"No chapter number for: \"{chapter.text}\"")
                inp = ask_number("Assign a unused chapter number to it "
                                 "(invalid input will ignore this chapter)",
                                 min_=0, num_type=float)
                title = chapter.text

                print()
                if inp is False:
                    continue
                else:
                    num = inp

            link = chapter["href"]
            self.chapters[num] = {
                "link": link,
                "title": clean_up_string(title)
            }
        return True

    @request_exception_handler
    def get_info(self, ch):
        """
        Gets the needed data abut the chapters from the site
        """
        link = self.chapters[ch]["link"]

        r = self.session.get(link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            pages = soup.find(class_="container-chapter-reader").find_all("img")
        except AttributeError:
            return "Failed to find reader, most likely server error"

        page_links = [p["src"] for p in pages]

        self.chapters[ch]["pages"] = page_links
        return True
