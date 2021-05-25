"""The module that handles importing the manga modules and changing their attributes."""
from ..models import BaseManga

# Modules need to be imported so they get registered, order matters
# isort: off
from .mangadex_org import Mangadex
from .mangakakalot_com import Mangakakalot  # noqa: F401
from .manganelo_com import Manganelo  # noqa: F401
from .mangatown_com import Mangatown  # noqa: F401


def match_module(link, title=None):
    """Initialize the proper module"""
    for module in BaseManga._all_modules:
        reg_search = module._site_regex.search(link)
        if reg_search is None:
            continue
        manga_id = reg_search.group("id")
        return module(manga_id, title)
    return None


def set_mangadex_language(lang_code):
    """Changes the mangadex language code for all instances"""
    Mangadex._lang_code = lang_code


def set_data_saver(flag):
    """Sets the data saver setting"""
    Mangadex._data_saver = flag


def toggle_check_only():
    """Toggles check only for all modules"""
    BaseManga._check_only = True


def set_download_directory(path):
    """
    Sets the download directory for all of the modules
    path = pathlib Path object
    """
    BaseManga._base_directory = path
