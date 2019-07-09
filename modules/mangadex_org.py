import cfscrape
import sys
import html


class Mangadex():
    def __init__(self, link, directory):
        # Initializes the data
        self.cloud_flare = True
        self.site = "mangadex.org"
        self.folder = directory
        self.scraper = cfscrape.create_scraper()
        self.mn_api_url = "https://mangadex.org/api/manga/{}"
        self.ch_api_url = "https://mangadex.org/api/chapter/{}"
        self.id = self.get_id(link)
        self.get_chapters()

    def get_id(self, link):
        if "/" in link:
            ID = link.split("/")[4]
        else:
            ID = link
        return ID

    def get_chapters(self):
        '''Gets the manga data using the mangadex API'''

        # Gets the json
        r = self.scraper.get(self.mn_api_url.format(self.id))
        try:
            r.raise_for_status()
        except Exception as e:
            sys.exit(e)
        data = r.json()
        self.series_title = html.unescape(data["manga"]["title"])

        # Series directory
        self.manga_dir = self.folder / self.series_title

        # Checks if chapters exist
        try:
            data["chapter"]
        except KeyError:
            sys.exit("Error!\tNo chapters found.")

        self.chapters = {}

        for chapter, ch in data["chapter"].items():
            # Only English
            if ch["lang_code"] != "gb":
                continue

            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 1 if oneshot
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

            self.chapters.setdefault(num, {})
            self.chapters[num][ch["group_name"]] = ch
            self.chapters[num][ch["group_name"]]["ch_id"] = chapter

    def check_groups(self):
        for ch in self.wanted:
            if len(self.chapters[ch]) == 1:
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
        # The list used by the download function

        ch_id = self.chapters[ch]["ch_id"]
        r = self.scraper.get(self.ch_api_url.format(ch_id)).json()

        # Skips chapter if the release is delayed
        if r["status"] == "delayed":
            print("\tChapter is a delayed release, ignoring it")
            return

        # Fixes the incomplete link
        if r["server"] == "/data/":
            server = "https://mangadex.org/data/"
        else:
            server = r["server"]

        # Creates the list of page urls
        url = f"{server}{r['hash']}/"
        pages = [f"{url}{page}" for page in r['page_array']]

        # Creates chapter info dict
        self.ch_info.append({"pages": pages,
                             "name": f"Chapter {ch}",
                             "title": r["title"]})
