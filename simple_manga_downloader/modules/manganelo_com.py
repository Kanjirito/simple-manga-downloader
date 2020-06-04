import requests
import re
from bs4 import BeautifulSoup
from ..decorators import request_exception_handler


class Manganelo:
    def __init__(self, link, directory, check_only, *args, **kwargs):
        self.session = requests.Session()
        self.site = "manganelo.com"
        self.folder = directory
        self.manga_link = link
        self.base_link = "https://manganelo.com/"
        self.cover_url = None
        self.chapters = {}
        self.check_only = check_only

    @property
    def manga_dir(self):
        return self.folder / self.series_title

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.chapters)

    @request_exception_handler
    def get_main(self, title_return=False):
        """
        Gets the main manga info like title, cover url and chapter links
        title_return=True will only get the title and return
        """
        r = self.session.get(self.manga_link, timeout=5)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        try:
            self.cover_url = soup.find(class_="info-image").img["src"]
        except AttributeError:
            return "Failed to get page"

        self.series_title = soup.find(class_="story-info-right").find("h1").text
        if title_return:
            return True

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
                inp = input("Assign a unused chapter number to it "
                            "(invalid input will ignore this chapter): ")
                title = chapter.text
                try:
                    num = float(inp)
                except ValueError:
                    print("Skipping\n")
                    continue
                print()

            link = chapter["href"]
            self.chapters[num] = {"link": link,
                                  "title": title}
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
