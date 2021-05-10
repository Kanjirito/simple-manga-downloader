import requests
import html
import re
from ..utils import request_exception_handler, clean_up_string, limiter
from .manga import BaseManga


class Mangadex(BaseManga):
    base_link = "https://api.mangadex.org"
    lang_code = "en"
    session = requests.Session()
    site_re = re.compile(r"mangadex\.(?:org|cc)/(?:title|manga)/([\w-]+)")
    md_at_home = True
    scanlation_cache = {}

    def __init__(self, link, title=None):
        if title:
            self.series_title = clean_up_string(title)
        else:
            self.series_title = None
        self.id = self.site_re.search(link).group(1)
        self.mn_api_url = f"{self.base_link}/manga/{self.id}"
        self.manga_link = f"https://mangadex.org/title/{self.id}"
        self.cover_url = None
        self.chapters = {}

    @request_exception_handler
    def get_main(self, title_return=False):
        """
        Gets the main manga info like title, cover url and chapter links
        using the mangadex API
        title_return=True will only get the title and return
        """
        data = self.make_get_request(self.mn_api_url)["data"]

        if self.series_title is None:
            self.series_title = clean_up_string(data["attributes"]["title"]["en"])
        if title_return:
            return True

        # TODO: Covers
        # Covers are currently not available #

        limit = 500
        params = {"locales[]": self.lang_code,
                  "limit": limit,
                  "offset": 0,
                  "order[chapter]": "asc"}
        chapters_data = []

        while True:
            feed_data = self.make_get_request(f"{self.mn_api_url}/feed", params=params)
            for chapter in feed_data["results"]:
                if chapter["result"] == "ok":
                    chapters_data.append(chapter)
            if limit + params["offset"] >= feed_data["total"]:
                break
            else:
                params["offset"] += limit
        if not chapters_data:
            return "No chapters found"

        self.data = chapters_data
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """

        for chapter in self.data:
            attributes = chapter["data"]["attributes"]
            title = clean_up_string(attributes["title"])
            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 0 if oneshot
            # Checks for chapter number in title
            # Asks for number if title present
            # Else skips the chapter
            if attributes["chapter"]:
                num = float(attributes["chapter"])
            elif title.lower() == "oneshot":
                num = 0.0
            elif title.lower().startswith("chapter"):
                num = float(chapter["chapter"].split()[-1])
            elif title:
                inp = self.ask_for_chapter_number(title)
                if inp is False:
                    continue
                else:
                    num = inp
            else:
                num = 0.0
            if num.is_integer():
                num = int(num)

            # Handles multi group releases
            all_groups = tuple((r["id"] for r in chapter["relationships"] if r["type"] == "scanlation_group"))

            if num in self.chapters and all_groups in self.chapters[num]:
                inp = self.ask_for_chapter_number(title,
                                                  taken=True,
                                                  num=num)
                if inp is False:
                    continue
                else:
                    num = inp

            self.chapters.setdefault(num, {})[all_groups] = {
                "ch_id": chapter["data"]["id"],
                "hash": attributes["hash"],
                "page_names": attributes["data"],
                "title": clean_up_string(title)
            }
        return True

    def check_groups(self, ch):
        """Handles the possible different releases of a chapter"""
        num_of_releases = len(self.chapters[ch])

        # 4f1de6a2-f0c5-4ac5-bce5-02c7dbb67deb is the MangaPlus group ID
        if ("4f1de6a2-f0c5-4ac5-bce5-02c7dbb67deb", ) in self.chapters[ch]:
            if num_of_releases == 1:
                return "Only Manga Plus releases"
            else:
                del self.chapters[ch][("4f1de6a2-f0c5-4ac5-bce5-02c7dbb67deb", )]
                num_of_releases -= 1
        if num_of_releases == 1:
            self.chapters[ch] = self.chapters[ch][list(self.chapters[ch])[0]]
            return True

        self.fetch_groups(tuple(self.chapters[ch].keys()))

        release_mapping = {}
        for release in self.chapters[ch].keys():
            names = []
            for group in release:
                names.append(self.scanlation_cache[group])
            release_mapping[" | ".join(names)] = release

        sorted_groups = sorted(release_mapping)
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
        self.chapters[ch] = self.chapters[ch][release_mapping[group]]
        return True

    def fetch_groups(self, group_ids):
        to_check = set()
        for release in group_ids:
            for id_ in release:
                if id_ not in self.scanlation_cache:
                    to_check.add(id_)
        if to_check:
            data = self.make_get_request("https://api.mangadex.org/group",
                                         params={"ids[]": to_check, "limit": 100})
            for group in data["results"]:
                self.scanlation_cache[group["data"]["id"]] = html.unescape(group["data"]["attributes"]["name"])

    @request_exception_handler
    def get_info(self, ch):
        """Gets the data about the specific chapters using the mangadex API"""

        groups = self.check_groups(ch)

        if groups is not True:
            return groups

        ch_id = self.chapters[ch]["ch_id"]
        data = self.make_get_request(f"https://api.mangadex.org/at-home/server/{ch_id}")

        # TODO: Figure out delayed chapters
        # TODO: Find a way to not use MD@Home
        server = data["baseUrl"]

        url = f"{server}/data/{self.chapters[ch]['hash']}/"
        pages = [f"{url}{page}" for page in self.chapters[ch]["page_names"]]
        self.chapters[ch]["pages"] = pages

        return True

    @limiter(0.3)
    def make_get_request(self, url, **kwargs):
        r = self.session.get(url, timeout=5, **kwargs)
        r.raise_for_status()
        return r.json()
