from ..utils import ask_number


class BaseManga:
    """The base class for the manga modules
    directory = manga download directory Path object
    check_only if True will cause all of the manga modules to not ask for
    user input
    """
    directory = None
    check_only = False

    @property
    def manga_dir(self):
        return self.directory / self.series_title

    def __bool__(self):
        return True

    def __len__(self):
        return len(self.chapters)

    @classmethod
    def check_if_link_matches(cls, link):
        """Checks if given url is valid for given module"""
        return cls.site_re.search(link)

    def ask_for_chapter_number(self, title, taken=False, num=None):
        """Asks for user input to get a chapter number
        title = the title of the chapter
        taken = Default False, prints a different output if the chapter already
        exists
        num = Default None, the chapter number. Only needed when taken = True

        Returns False if the input is invalid otherwise returns the input as either
        float or int.
        """
        if taken:
            if title:
                print(f"Chapter number already taken for Chapter {num}, \"{title}\"")
            else:
                print(f"Chapter number already taken for Chapter {num}")
        else:
            print(f"No chapter number for: \"{title}\"")
        inp = ask_number("Assign a chapter number to it "
                         "\n(invalid input will ignore this chapter, "
                         "will override existing chapter with same number)",
                         min_=0, num_type=float)
        print()
        if inp is False:
            return False
        elif inp.is_integer():
            return int(inp)
        else:
            return inp
