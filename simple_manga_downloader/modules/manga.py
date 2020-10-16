from html import unescape


class BaseManga:
    """The base class for the manga modules
    directory = manga download directory, has to be changed into an actual
    path before downloading
    check_only if True will cause all of the manga modules to not ask for
    user input
    """
    directory = None
    check_only = False
    replacement_rules = None

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
        """Cleans up the given string from unwanted characters"""
        if not type(string) == str:
            return string

        fixed_html = unescape(string)
        new_string_list = []
        for char in fixed_html:
            if char in self.replacement_rules:
                new_string_list.append(self.replacement_rules[char])
            else:
                new_string_list.append(char)
        return "".join(new_string_list)
