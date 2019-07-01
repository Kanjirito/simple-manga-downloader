import cfscrape
import sys
import html


class Mangadex():
    def __init__(self, link, directory):
        # Initializes the data
        self.cloud_flare = True
        self.folder = directory
        self.scraper = cfscrape.create_scraper()
        self.ch_api_url = "https://mangadex.org/api/chapter/{}"
        self.mn_api_url = "https://mangadex.org/api/manga/{}"
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

        # Creates the chapters info dict
        self.chapters = {}

        for chapter in data["chapter"]:
            ch = data["chapter"][chapter]
            # Only English
            if ch["lang_code"] != "gb":
                continue

            # Creates the number of the chapter
            # Uses chapter number if present
            # Sets to 1 if oneshot
            # Slices title if "Chapter XX"
            if ch["chapter"] != "":
                num = float(ch["chapter"])
            elif ch["title"].lower() == "oneshot":
                num = 0.0
            elif ch["title"].lower().startswith("chapter"):
                num = float(ch["chapter"].split()[-1])

            if num.is_integer():
                num = int(num)

            self.chapters.setdefault(num, {})
            self.chapters[num][ch["group_name"]] = ch
            self.chapters[num][ch["group_name"]]["ch_id"] = chapter

        print("\n------------------------\n" + f"Found {len(self.chapters)} uploaded chapter(s) for {self.series_title}\n" + "------------------------")

    def get_info(self):
        '''Gets the data about the specific chapters using the mangadex API'''
        # The dict used by the download function
        self.ch_info = []

        # Goes over every chapter
        for ch in self.wanted:

            # Creates the chapter name and path
            chapter_name = f"Chapter {ch}"
            print(f"Checking: {chapter_name}")

            # Checks if chapter has multiple groups, if yes asks which you want
            if len(self.chapters[ch]) == 1:
                group = list(self.chapters[ch])[0]
            else:
                print(f"\nMultiple groups for chapter {ch}, select one(1,2,3...):")
                sorted_groups = sorted(self.chapters[ch])
                for n, g in enumerate(sorted_groups):
                    print(f"{n+1}.{g}")
                select = int(input("Enter the number of the group: "))
                while select > len(sorted_groups):
                    select = int(input("\nWrong number, try again: "))
                select -= 1
                print()
                group = sorted_groups[select]
                del select
                del sorted_groups

            ch_id = self.chapters[ch][group]["ch_id"]
            r = self.scraper.get(self.ch_api_url.format(ch_id)).json()

            # Skips chapter if the release is delayed
            if r["status"] == "delayed":
                print("Chapter is a delayed release skipping")
                continue

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
                                 "name": chapter_name,
                                 "title": r["title"]})
