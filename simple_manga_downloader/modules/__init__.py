"""The module that handles importing the manga modules and changing their attributes."""
from .manga import BaseManga
from .mangadex_org import Mangadex
from .mangakakalot_com import Mangakakalot
from .manganelo_com import Manganelo
from .mangatown_com import Mangatown

"""
List of all the modules, order matters if multiple modules support the
same same URL. New modules must be added to it.
"""
ALL_MODULES = [Mangadex,
               Mangatown,
               Mangakakalot,
               Manganelo,
               ]


def set_mangadex_language(lang_code):
    """Changes the mangadex language code for all instances"""
    Mangadex.lang_code = lang_code


def toggle_check_only():
    """Toggles check_only for all modules"""
    BaseManga.check_only = True


def set_download_directory(path):
    """
    Sets the download directory for all of the modules
    path = pathlib Path object
    """
    BaseManga.directory = path
