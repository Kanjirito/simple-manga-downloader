"""Modules that contains all of the model classes used in the downloader"""
from abc import ABC, abstractmethod

from .utils import ask_number, request_exception_handler


class BaseManga(ABC):
    """The base class for the manga modules
    directory = manga download directory Path object
    check_only if True will cause all of the manga modules to not ask for
    user input
    """

    # These should not be set/changed in manga subclasses
    _all_modules = []
    _base_directory = None
    _check_only = False

    def __init_subclass__(cls, **kwargs):
        BaseManga._all_modules.append(cls)
        super().__init_subclass__(**kwargs)

    def __init__(self, manga_id, title=None):
        self._id = manga_id
        self._title = title
        self._covers = {}
        self._chapters = {}

    @property
    def chapters(self):
        """The chapters for a given manga

        TODO: describe the structure
        """
        return self._chapters

    @chapters.setter
    def chapters(self, chapters):
        self._chapters = chapters

    @property
    def covers(self):
        """A dictionary of covers for the manga

        They keys are the filenames used for the cover and the value is the url.
        """
        return self._covers

    @abstractmethod
    def manga_url(self):
        """Returns a clean link to the manga

        This link should be cleaned of any useless parts and should work if copied into
        a browser. Most of the time this is just the base url + id.
        Needs to be decorated as a property when implemented.
        """
        raise NotImplementedError

    @property
    def title(self):
        """The tile of the manga"""
        return self._title

    @property
    def id(self):
        """The identifier of the manga"""
        return self._id

    @property
    def manga_dir(self):
        """The Path object of where the manga should be downloaded"""
        return self._base_directory / self.title

    @property
    def session(self):
        """The request Session object for the site"""
        return self._session

    def __bool__(self):
        return True

    def __len__(self):
        return len(self._chapters)

    @request_exception_handler
    def get_main(self, *args, **kwargs):
        """Gets the main manga info like title, cover url and chapter links

        title_return=True will only get the title and return
        """
        return self._get_main(*args, **kwargs)

    @abstractmethod
    def _get_main(self):
        # Error raised to prevent super()
        raise NotImplementedError

    def get_chapters(self, *args, **kwargs):
        """Handles the chapter data by assigning chapter numbers"""
        return self._get_chapters(*args, **kwargs)

    @abstractmethod
    def _get_chapters(self):
        # Error raised to prevent super()
        raise NotImplementedError

    @request_exception_handler
    def get_info(self, *args, **kwargs):
        """Gets the needed data abut the chapters from the site"""
        return self._get_info(*args, **kwargs)

    @abstractmethod
    def _get_info(self):
        # Error raised to prevent super()
        raise NotImplementedError

    def ask_for_chapter_number(self, title, taken=False, num=None):
        """Asks for user input to get a chapter number

        title = the title of the chapter
        taken = Default False, prints a different output if the chapter already
        exists
        num = Default None, the chapter number. Only needed when taken = True

        Returns False if the input is invalid otherwise returns the input as
        either float or int.
        """
        if self.check_only:
            return False

        if taken:
            if title:
                print(f'Chapter number already taken for Chapter {num}, "{title}"')
            else:
                print(f"Chapter number already taken for Chapter {num}")
        else:
            print(f'No chapter number for: "{title}"')
        inp = ask_number(
            "Assign a chapter number to it \n"
            "(invalid input will ignore this chapter, will override existing chapter with same number)",
            min_=0,
            num_type=float,
        )
        print()
        if inp is False:
            return False
        elif inp.is_integer():
            return int(inp)
        else:
            return inp
