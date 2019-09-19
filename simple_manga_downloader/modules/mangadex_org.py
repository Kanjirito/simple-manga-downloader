import cfscrape
import requests.exceptions
import html
import re


class Mangadex():
    def __init__(self, link, directory):
        # Initializes the data
        self.scraper = cfscrape.create_scraper()
        self.site = "mangadex.org"
        self.folder = directory
        self.manga_link = link.split("/chapters")[0].rstrip("/")
        self.mn_api_url = "https://mangadex.org/api/manga/{}"
        self.ch_api_url = "https://mangadex.org/api/chapter/{}"
        self.id = self.get_id(link)

    def get_id(self, link):
        reg = re.compile(r"title/(\d*)/")
        return reg.search(link).group(1)

    def get_chapters(self, title_return):
        '''Gets the manga data using the mangadex API
        title_return=True will not create the chapters dict,
        used if only title is needed'''

        r = self.scraper.get(self.mn_api_url.format(self.id), timeout=5)
        r.raise_for_status()
        data = r.json()
        self.series_title = html.unescape(data["manga"]["title"])
        if title_return:
            return True
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

            all_groups_str = " | ".join(all_groups)
            self.chapters.setdefault(num, {})
            self.chapters[num][all_groups_str] = {"ch_id": chapter,
                                                  "title": ch["title"]}
        return True

    def check_groups(self):
        for ch in list(self.chapters):
            len_cond = len(self.chapters[ch]) == 1

            if "MangaPlus" in self.chapters[ch]:
                if len_cond:
                    del self.chapters[ch]
                    print(f"Chapter {ch} only Manga Plus")
                    continue
                else:
                    del self.chapters["MangaPlus"]

            if len_cond:
                self.chapters[ch] = self.chapters[ch][list(self.chapters[ch])[0]]
                continue

            print(f"\nMultiple groups for chapter {ch}, select one(1,2,3...):")
            sorted_groups = sorted(self.chapters[ch])
            selections = []
            for n, g in enumerate(sorted_groups, 1):
                print(f"{n}.{g}")
                selections.append(n)
            # Asks for a selection, if too high or not a number asks again
            try:
                select = int(input("Enter the number of the group: "))
            except ValueError:
                select = len(sorted_groups) + 1
            while select not in selections:
                try:
                    select = int(input("Wrong input, try again: "))
                except ValueError:
                    select = len(sorted_groups) + 1
            group = sorted_groups[select - 1]
            self.chapters[ch] = self.chapters[ch][group]

    def get_info(self, ch):
        '''Gets the data about the specific chapters using the mangadex API'''

        ch_id = self.chapters[ch]["ch_id"]
        r = self.scraper.get(self.ch_api_url.format(ch_id), timeout=5)
        if r.status_code != 200 and r.status_code != 409:
            raise requests.HTTPError

        data = r.json()
        # Skips chapter if the release is delayed
        if data["status"] == "delayed":
            return "\tChapter is a delayed release, ignoring it"

        # Fixes the incomplete link
        if data["server"] == "/data/":
            server = "https://mangadex.org/data/"
        else:
            server = data["server"]

        url = f"{server}{data['hash']}/"
        pages = [f"{url}{page}" for page in data['page_array']]
        self.chapters[ch]["pages"] = pages

        return True
