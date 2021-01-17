import requests
import html
import re
from ..utils import request_exception_handler, clean_up_string
from .manga import BaseManga


class Mangadex(BaseManga):
    base_link = "https://mangadex.org"
    lang_code = "gb"
    session = requests.Session()
    site_re = re.compile(r"mangadex\.(?:org|cc)/(?:title|manga)/(\d+)")
    md_at_home = True

    def __init__(self, link, title=None):
        if title:
            self.series_title = clean_up_string(title)
        else:
            self.series_title = None
        self.id = self.site_re.search(link).group(1)
        self.mn_api_url = f"{self.base_link}/api/v2/manga/{self.id}"
        self.ch_api_url = f"{self.base_link}/api/v2/chapter/"
        self.manga_link = f"{self.base_link}/title/{self.id}"
        self.cover_url = None
        self.chapters = {}

    @request_exception_handler
    def get_main(self, title_return=False):
        """
        Gets the main manga info like title, cover url and chapter links
        using the mangadex API
        title_return=True will only get the title and return
        """
        r = self.session.get(self.mn_api_url, timeout=5)
        r.raise_for_status()
        data = r.json()["data"]

        if self.series_title is None:
            self.series_title = clean_up_string(data["title"])
        if title_return:
            return True

        cover = data.get("mainCover")
        covers = self.session.get(f"{self.mn_api_url}/covers")
        if covers.ok:
            covers = covers.json()
            self.cover_url = {f"{self.series_title} Vol {cov['volume']}": cov["url"]
                              for cov in covers["data"]}
        elif cover:
            self.cover_url = {self.series_title: data["mainCover"]}

        chapters_r = self.session.get(f"{self.mn_api_url}/chapters")
        chapters_r.raise_for_status()
        chapters_data = chapters_r.json()["data"]

        if not chapters_data["chapters"]:
            return "No chapters found"

        groups_dict = {group["id"]: group["name"] for group in chapters_data["groups"]}
        self.chapters_data = {"chapters": chapters_data["chapters"],
                              "groups": groups_dict}
        self.data = data
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """

        for chapter in self.chapters_data["chapters"][::-1]:
            if chapter["language"].lower() != self.lang_code.lower():
                continue

            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 0 if oneshot
            # Checks for chapter number in title
            # Asks for number if title present
            # Else skips the chapter
            if chapter["chapter"]:
                num = float(chapter["chapter"])
            elif chapter["title"].lower() == "oneshot":
                num = 0.0
            elif chapter["title"].lower().startswith("chapter"):
                num = float(chapter["chapter"].split()[-1])
            elif chapter["title"]:
                inp = self.ask_for_chapter_number(chapter["title"])
                if inp is False:
                    continue
                else:
                    num = inp
            else:
                num = 0.0
            if num.is_integer():
                num = int(num)

            if num in self.chapters:
                inp = self.ask_for_chapter_number(chapter["title"],
                                                  taken=True,
                                                  num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            # Handles multi group releases
            all_groups = [self.chapters_data["groups"][g] for g in chapter["groups"]]
            all_groups_str = html.unescape(" | ".join(all_groups))

            self.chapters.setdefault(num, {})
            self.chapters[num][all_groups_str] = {
                "ch_id": chapter["id"],
                "title": clean_up_string(chapter["title"])
            }
        return True

    def check_groups(self, ch):
        """Handles the possible different releases of a chapter"""
        num_of_releases = len(self.chapters[ch])

        if "MangaPlus" in self.chapters[ch]:
            if num_of_releases == 1:
                return "Only Manga Plus releases"
            else:
                del self.chapters[ch]["MangaPlus"]
                num_of_releases -= 1
        if num_of_releases == 1:
            self.chapters[ch] = self.chapters[ch][list(self.chapters[ch])[0]]
            return True

        sorted_groups = sorted(self.chapters[ch])
        if self.check_only:
            select = 1
        else:
            print(f"Multiple groups for chapter {ch}, select one by number:")
            selections = []
            for n, g in enumerate(sorted_groups, 1):
                print(f"{n}.{g}")
                selections.append(n)

            try:
                in_str = "Enter the number of the group [invalid input will skip chapter]:"
                select = int(input(in_str))
            except ValueError:
                select = len(sorted_groups) + 1
            if select not in selections:
                return "Invalid input, skipping chapter"
            print()

        group = sorted_groups[select - 1]
        self.chapters[ch] = self.chapters[ch][group]
        return True

    @request_exception_handler
    def get_info(self, ch):
        """Gets the data about the specific chapters using the mangadex API"""

        groups = self.check_groups(ch)

        if groups is not True:
            return groups

        ch_id = self.chapters[ch]["ch_id"]
        r = self.session.get(f"{self.ch_api_url}{ch_id}", timeout=5)
        if r.status_code != 200 and r.status_code != 409:
            raise requests.HTTPError

        data = r.json()
        # Skips chapter if the release is delayed
        if data["status"] == "delayed":
            return "Chapter is a delayed release, ignoring it"

        # Fixes the incomplete link
        if data["data"]["server"] == "/data/":
            server = f"{self.base_link}/data/"
        else:
            server = data["data"]["server"]
        fallback_server = data["data"].get("serverFallback")

        if not self.md_at_home and fallback_server:
            server_to_use = fallback_server
        else:
            server_to_use = server

        url = f"{server_to_use}{data['data']['hash']}/"
        pages = [f"{url}{page}" for page in data["data"]["pages"]]
        self.chapters[ch]["pages"] = pages

        return True
