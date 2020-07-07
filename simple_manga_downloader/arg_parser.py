import argparse


def parse_arguments():
    """Parses the arguments
    Returns the arguments object
    """

    class SetAction(argparse.Action):
        """Action for argparse that creates a set"""
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, set(values))

    class NoDupesOrderedListAction(argparse.Action):
        """Action for argparse that creates a list with no dupes and preserved order"""
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, list(dict.fromkeys(values)))

    desc = ("SMD is a command line manga downloader. For more information "
            "read the README file in the GitHub repo.\n"
            "https://github.com/Kanjirito/simple-manga-downloader/blob/master/README.md")
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-c", "--custom",
                        dest="custom_cfg",
                        metavar="PATH/TO/CONFIG",
                        help="Sets a custom config to use",
                        default=None)

    # Sub-parsers for the different modes
    subparsers = parser.add_subparsers(dest="subparser_name",
                                       metavar="mode",
                                       required=True)
    parser_conf = subparsers.add_parser("conf",
                                        help="Downloader will be in config edit mode",
                                        description="Changes the settings")
    parser_down = subparsers.add_parser("down",
                                        help="Downloader will be in download mode",
                                        description=("Downloads the given manga. "
                                                     "Supports multiple links at once."))
    parser_update = subparsers.add_parser("update",
                                          help="Downloader will be in update mode",
                                          description="Download new chapters from tracked list")
    parser_version = subparsers.add_parser("version",
                                           help="Downloader will be in version mode",
                                           description="Prints the downloader version")

    # Parser for download mode
    parser_down.add_argument("input", nargs="+",
                             metavar="manga url",
                             action=NoDupesOrderedListAction,
                             help="URL or tracked manga index to download")
    parser_down.add_argument("-d", "--directory",
                             dest="custom_down_dire",
                             metavar="PATH/TO/DIRECTORY",
                             default=None,
                             help="Custom path for manga download")
    parser_down.add_argument("-e", "--exclude",
                             help="Chapters to exclude \"1 5 10 15\"",
                             metavar="NUMBER",
                             nargs="+",
                             type=float,
                             action=SetAction,
                             default=set())
    parser_down.add_argument("-n", "--name",
                             default=None,
                             metavar="NEW NAME",
                             nargs="+",
                             help=("Download the manga with a custom name. "
                                   "Not recommended to use with multiple "
                                   "downloads at once."))
    input_group_down = parser_down.add_mutually_exclusive_group()
    input_group_down.add_argument("-c", "--check",
                                  help=("Only check for new chapters "
                                        "without downloading and asking for any input"),
                                  action="store_true",
                                  dest="check_only")
    input_group_down.add_argument("-i", "--ignore_input",
                                  help="Downloads without asking for any input",
                                  action="store_true",
                                  dest="ignore_input")
    selection_group = parser_down.add_mutually_exclusive_group()
    selection_group.add_argument("-r", "--range",
                                 help=("Specifies the range of chapters to download, "
                                       "both ends are inclusive. \"1 15\""),
                                 metavar="NUMBER",
                                 nargs=2,
                                 type=float)
    selection_group.add_argument("-s", "--selection",
                                 help=("Specifies which chapters to download. "
                                       "Accepts multiple chapters \"2 10 25\""),
                                 metavar="NUMBER",
                                 nargs="+",
                                 action=SetAction,
                                 type=float)
    selection_group.add_argument("-l", "--latest",
                                 help="Download only the latest chapter",
                                 action='store_true')

    # Parser for config mode
    tracked_edit_group = parser_conf.add_mutually_exclusive_group()
    tracked_edit_group.add_argument("-a", "--add-tracked",
                                    help="Adds manga to the tracked list",
                                    dest="add_to_tracked",
                                    metavar="MANGA URL",
                                    nargs="+",
                                    action=NoDupesOrderedListAction)
    tracked_edit_group.add_argument("-r", "--remove-tracked",
                                    help=("Removes manga from tracked. "
                                          "Supports deletion by url, title or tracked index"),
                                    dest="remove_from_tracked",
                                    metavar="MANGA URL|MANGA TITLE|NUMBER",
                                    nargs="+",
                                    action=SetAction)
    parser_conf.add_argument("-t", "--clear-tracked",
                             help="Clears the tracked list",
                             action="store_true")
    parser_conf.add_argument("-s", "--save-directory",
                             help="Changes the manga download directory",
                             metavar="PATH/TO/DIRECTORY",
                             dest="manga_down_directory")
    parser_conf.add_argument("-d", "--default",
                             help="Resets the config to defaults",
                             action="store_true")
    parser_conf.add_argument("-l", "--list-tracked",
                             help="Lists all of the tracked shows",
                             action="store_true")
    parser_conf.add_argument("-m", "--modify-position",
                             help="Changes the position of tracked manga",
                             action="store_true",
                             dest="modify_tracked_position")
    parser_conf.add_argument("-v", "--verbose",
                             help="Used with -l or -m to also print links",
                             action="store_true",
                             dest="verbose")
    parser_conf.add_argument("-p", "--print_conf",
                             help="Print config settings",
                             action="store_true",
                             dest="print_config")
    parser_conf.add_argument("-c", "--covers",
                             help="Toggles the cover download setting",
                             action="store_true",
                             dest="toggle_covers")
    parser_conf.add_argument("--change_lang",
                             help="Changes the mangadex language code",
                             metavar="LANGUAGE CODE")
    parser_conf.add_argument("--list_lang",
                             help="Lists all of the mangadex language codes",
                             action="store_true")
    parser_conf.add_argument("--timeout",
                             help="Change the download timeout",
                             metavar="SECONDS",
                             type=int,
                             dest="timeout")

    # Update options
    input_group_update = parser_update.add_mutually_exclusive_group()
    input_group_update.add_argument("-c", "--check",
                                    help=("Only check for new chapters "
                                          "without downloading and asking for any input"),
                                    action="store_true",
                                    dest="check_only")
    input_group_update.add_argument("-i", "--ignore_input",
                                    help="Downloads without asking for any input",
                                    action="store_true",
                                    dest="ignore_input")
    parser_update.add_argument("-d", "--directory",
                               dest="custom_down_dire",
                               metavar="PATH/TO/DIRECTORY",
                               default=None,
                               help="Custom path for manga download")

    # Version options
    parser_version.add_argument("-c", "--check",
                                help="Checks if there is a new version available",
                                action="store_true",
                                dest="version_check")

    return parser.parse_args()
