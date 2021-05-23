"""The module that handles importing the manga modules and changing their attributes."""
from .manga import BaseManga

# Modules need to be imported so they get registered, order matters
# isort: off
from .mangadex_org import Mangadex
from .mangakakalot_com import Mangakakalot  # noqa: F401
from .manganelo_com import Manganelo  # noqa: F401
from .mangatown_com import Mangatown  # noqa: F401


def match_module(link, title):
    """Initialize the proper module"""
    module = BaseManga.find_matching_module(link)
    if module is False:
        return False
    else:
        return module(link, title=title)


def set_mangadex_language(lang_code):
    """Changes the mangadex language code for all instances"""
    Mangadex.lang_code = lang_code


def set_data_saver(flag):
    """Sets the data saver setting"""
    Mangadex.data_saver = flag


def toggle_check_only():
    """Toggles check_only for all modules"""
    BaseManga.check_only = True


def set_download_directory(path):
    """
    Sets the download directory for all of the modules
    path = pathlib Path object
    """
    BaseManga.directory = path
