from html import unescape


class BaseManga:
    """The base class for the manga modules
    directory = manga dowload directory, has to be changed into a actual
    path before downloading
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

    def clean_up_string(self, string):
        """Replaces html escape codes and replaces / with ╱"""
        return unescape(string).replace("/", "╱")
