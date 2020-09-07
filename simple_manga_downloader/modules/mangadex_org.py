import requests
import html
import re
from ..decorators import request_exception_handler
from .manga import BaseManga


class Mangadex(BaseManga):
    base_link = "https://mangadex.org"
    lang_code = "gb"
    session = requests.Session()
    site_re = re.compile(r"""(?x)https?://(?:www\.)?mangadex\.
                         (?:(?:org)|(?:cc))/title/(\d+)""")

    def __init__(self, link):
        self.mn_api_url = f"{self.base_link}/api/manga/"
        self.ch_api_url = f"{self.base_link}/api/chapter/"
        self.id = self.get_id(link)
        self.manga_link = f"{self.base_link}/title/{self.id}"
        self.cover_url = None
        self.chapters = {}

    def get_id(self, link):
        return self.site_re.search(link).group(1)

    @request_exception_handler
    def get_main(self, title_return=False):
        """
        Gets the main manga info like title, cover url and chapter links
        using the mangadex API
        title_return=True will only get the title and return
        """
        r = self.session.get(f"{self.mn_api_url}{self.id}", timeout=5)
        r.raise_for_status()
        data = r.json()
        self.series_title = self.clean_up_string(data["manga"]["title"])
        if title_return:
            return True
        cover = data["manga"].get("cover_url")
        if cover:
            self.cover_url = f"{self.base_link}{cover}"

        # Checks if chapters exist
        try:
            data["chapter"]
        except KeyError:
            return "No chapters found!"

        self.data = data
        return True

    def get_chapters(self):
        """
        Handles the chapter data by assigning chapter numbers
        """

        for chapter, ch in self.data["chapter"].items():
            if ch["lang_code"].lower() != self.lang_code.lower():
                continue

            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 0 if oneshot
            # Checks for chapter number in title
            # Asks for number if title present
            # Else skips the chapter
            if ch["chapter"]:
                num = float(ch["chapter"])
            elif ch["title"].lower() == "oneshot":
                num = 0.0
            elif ch["title"].lower().startswith("chapter"):
                num = float(ch["chapter"].split()[-1])
            elif ch["title"]:
                if self.check_only:
                    continue
                print(f"No chapter number for: \"{ch['title']}\"")
                inp = input("Assign a unused chapter number to it "
                            "(invalid input will ignore this chapter): ")
                try:
                    num = float(inp)
                except ValueError:
                    print("Skipping\n")
                    continue
                print()
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
        if data["server"] == "/data/":
            server = f"{self.base_link}/data/"
        else:
            server = data["server"]

        url = f"{server}{data['hash']}/"
        pages = [f"{url}{page}" for page in data['page_array']]
        self.chapters[ch]["pages"] = pages

        return True
