import cfscrape
import requests.exceptions
import html
import re
from ..decorators import request_exception_handler


class Mangadex():
    def __init__(self, link, directory):
        # Initializes the data
        self.session = cfscrape.create_scraper()
        self.site = "mangadex.org"
        self.folder = directory
        self.manga_link = link.split("/chapters")[0].rstrip("/")
        self.mn_api_url = "https://mangadex.org/api/manga/{}"
        self.ch_api_url = "https://mangadex.org/api/chapter/{}"
        self.id = self.get_id(link)
        self.cover_url = None

    def get_id(self, link):
        reg = re.compile(r"title/(\d*)/?")
        return reg.search(link).group(1)

    @request_exception_handler
    def get_chapters(self, title_return=False):
        '''Gets the manga data using the mangadex API
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = self.session.get(self.mn_api_url.format(self.id), timeout=5)
        r.raise_for_status()
        data = r.json()
        self.series_title = html.unescape(data["manga"]["title"])
        if title_return:
            return True
        cover = data["manga"].get("cover_url")
        if cover:
            self.cover_url = f"https://mangadex.org{cover}"
        else:
            self.cover_url = None
        self.manga_dir = self.folder / self.series_title

        # Checks if chapters exist
        try:
            data["chapter"]
        except KeyError:
            return "No chapters found!"

        self.chapters = {}

        for chapter, ch in data["chapter"].items():
            # Only English
            if ch["lang_code"] != "gb":
                continue

            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 0 if oneshot
            # Slices title if "Chapter XX"
            if ch["chapter"]:
                num = float(ch["chapter"])
            elif ch["title"].lower() == "oneshot":
                num = 0.0
            elif ch["title"].lower().startswith("chapter"):
                num = float(ch["chapter"].split()[-1])
            else:
                num = 0.0
            if num.is_integer():
                num = int(num)

            all_groups = []
            if ch["group_name"]:
                all_groups.append(ch["group_name"])
            if ch["group_name_2"]:
                all_groups.append(ch["group_name_2"])
            if ch["group_name_3"]:
                all_groups.append(ch["group_name_3"])

            all_groups_str = html.unescape(" | ".join(all_groups))
            self.chapters.setdefault(num, {})
            self.chapters[num][all_groups_str] = {"ch_id": chapter,
                                                  "title": ch["title"]}
        return True

    def check_groups(self, ch):
        len_cond = len(self.chapters[ch]) == 1

        if "MangaPlus" in self.chapters[ch]:
            if len_cond:
                return "Only Manga Plus releases"
            else:
                del self.chapters["MangaPlus"]

        if len_cond:
            self.chapters[ch] = self.chapters[ch][list(self.chapters[ch])[0]]
            return True

        print(f"Multiple groups for chapter {ch}, select one(1,2,3...):")
        sorted_groups = sorted(self.chapters[ch])
        selections = []
        for n, g in enumerate(sorted_groups, 1):
            print(f"{n}.{g}")
            selections.append(n)
        # Asks for a selection, if too high or not a number asks again
        try:
            in_str = "Enter the number of the group [invalid input will skip chapter]:"
            select = int(input(in_str))
        except ValueError:
            select = len(sorted_groups) + 1
        if select not in selections:
            return "Wrong input, skipping chapter"

        print()
        group = sorted_groups[select - 1]
        self.chapters[ch] = self.chapters[ch][group]
        return True

    @request_exception_handler
    def get_info(self, ch):
        '''Gets the data about the specific chapters using the mangadex API'''

        groups = self.check_groups(ch)

        if groups is not True:
            return groups

        ch_id = self.chapters[ch]["ch_id"]
        r = self.session.get(self.ch_api_url.format(ch_id), timeout=5)
        if r.status_code != 200 and r.status_code != 409:
            raise requests.HTTPError

        data = r.json()
        # Skips chapter if the release is delayed
        if data["status"] == "delayed":
            return "Chapter is a delayed release, ignoring it"

        # Fixes the incomplete link
        if data["server"] == "/data/":
            server = "https://mangadex.org/data/"
        else:
            server = data["server"]

        url = f"{server}{data['hash']}/"
        pages = [f"{url}{page}" for page in data['page_array']]
        self.chapters[ch]["pages"] = pages

        return True
