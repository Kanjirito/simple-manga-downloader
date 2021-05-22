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

    parser = argparse.ArgumentParser(
        description=(
            "SMD is a command line manga downloader. For more information read the README file in the GitHub repo.\n"
            "https://github.com/Kanjirito/simple-manga-downloader/blob/master/README.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--custom",
        dest="custom_cfg",
        metavar="PATH/TO/CONFIG",
        help="Sets a custom config to use",
        default=None,
    )

    # Sub-parsers for the different modes
    subparsers = parser.add_subparsers(dest="subparser_name", metavar="mode")
    # Has to be this way for python 3.6 support
    subparsers.required = True

    parser_conf = subparsers.add_parser(
        "conf",
        help="Downloader will be in config edit mode",
        description="Changes the settings",
    )
    parser_down = subparsers.add_parser(
        "down",
        help="Downloader will be in download mode",
        description="Downloads the given manga. Supports multiple links at once.",
    )
    parser_update = subparsers.add_parser(
        "update",
        help="Downloader will be in update mode",
        description="Download new chapters from tracked list",
    )
    parser_version = subparsers.add_parser(
        "version",
        help="Downloader will be in version mode",
        description="Prints the downloader version",
    )

    # Parser for download mode
    parser_down.add_argument(
        "input",
        nargs="+",
        metavar="target [another_target]",
        action=NoDupesOrderedListAction,
        help="Manga URL, tracked index or tracked title to download",
    )
    parser_down.add_argument(
        "-d",
        "--directory",
        dest="custom_down_dire",
        metavar="PATH/TO/DIRECTORY",
        default=None,
        help="Custom path for manga download",
    )
    parser_down.add_argument(
        "-e",
        "--exclude",
        help="Chapters to exclude",
        metavar="NUMBER",
        nargs="+",
        type=float,
        action=SetAction,
        default=set(),
    )
    parser_down.add_argument(
        "-n",
        "--name",
        default=None,
        metavar="CUSTOM NAME",
        nargs="+",
        help="Download the manga with a custom name. Not recommended to use with multiple downloads at once.",
    )
    parser_down.add_argument(
        "--data-saver",
        help="Toggle the Mangadex data saver option. Takes priority over config file.",
        choices=["y", "yes", "n", "no"],
        metavar=r"{yes(y),no(n)}",
        dest="data_saver",
    )
    parser_down.add_argument(
        "--language",
        help="Overwrite the Mangadex language setting",
        dest="langauge_code",
    )

    input_group_down = parser_down.add_mutually_exclusive_group()
    input_group_down.add_argument(
        "-c",
        "--check",
        help="Only check for new chapters without downloading and asking for any input",
        action="store_true",
        dest="check_only",
    )
    input_group_down.add_argument(
        "-i",
        "--ignore-input",
        help="Downloads without asking for any input in case of group conflict the alphabetically first group will be chosen)",
        action="store_true",
        dest="ignore_input",
    )

    selection_group = parser_down.add_mutually_exclusive_group()
    selection_group.add_argument(
        "-r",
        "--range",
        help="Specifies the range of chapters to download, both ends are inclusive.",
        metavar=("START", "END"),
        nargs=2,
        type=float,
    )
    selection_group.add_argument(
        "-s",
        "--selection",
        help='Specifies which chapters to download. Accepts multiple chapters "2 10 25"',
        metavar="NUMBER",
        nargs="+",
        action=SetAction,
        type=float,
    )
    selection_group.add_argument(
        "-l", "--latest", help="Download only the latest chapter", action="store_true"
    )

    # Parser for config mode
    tracked_edit_group = parser_conf.add_mutually_exclusive_group()
    tracked_edit_group.add_argument(
        "-a",
        "--add-tracked",
        help="Adds manga to the tracked list",
        dest="add_to_tracked",
        metavar="MANGA_URL",
        nargs="+",
        action=NoDupesOrderedListAction,
    )
    tracked_edit_group.add_argument(
        "-r",
        "--remove-tracked",
        help="Removes manga from tracked. Supports deletion by url, title or tracked index",
        dest="remove_from_tracked",
        metavar="{MANGA_URL,MANGA_TITLE,NUMBER}",
        nargs="+",
        action=SetAction,
    )

    parser_conf.add_argument(
        "-n",
        "--name",
        help="When adding manga give it a custom name (do not use when adding multiple at once)",
        dest="name",
        default=None,
        nargs="+",
        metavar="CUSTOM NAME",
    )
    parser_conf.add_argument(
        "-t", "--clear-tracked", help="Clears the tracked list", action="store_true"
    )
    parser_conf.add_argument(
        "-s",
        "--save-directory",
        help="Changes the manga download directory",
        metavar="PATH/TO/DIRECTORY",
        dest="manga_down_directory",
    )
    parser_conf.add_argument(
        "-d", "--default", help="Resets the config to defaults", action="store_true"
    )
    parser_conf.add_argument(
        "-l",
        "--list-tracked",
        help="Lists all of the tracked manga",
        action="store_true",
    )
    parser_conf.add_argument(
        "-m",
        "--modify-position",
        help="Changes the position of tracked manga",
        action="store_true",
        dest="modify_tracked_position",
    )
    parser_conf.add_argument(
        "-v",
        "--verbose",
        help="Used with -l or -m to also print links",
        action="store_true",
        dest="verbose",
    )
    parser_conf.add_argument(
        "--change-name",
        help="Change the name of a tracked manga",
        action="store_true",
        dest="change_name",
    )
    parser_conf.add_argument(
        "-p",
        "--print-conf",
        help="Print all config settings",
        action="store_true",
        dest="print_config",
    )
    parser_conf.add_argument(
        "-c",
        "--covers",
        help="Toggles the cover download setting",
        action="store_true",
        dest="toggle_covers",
    )
    parser_conf.add_argument(
        "--change-lang",
        help="Changes the mangadex language code",
        metavar="LANGUAGE CODE",
    )
    parser_conf.add_argument(
        "--list-lang",
        help="Lists all of the mangadex language codes",
        action="store_true",
    )
    parser_conf.add_argument(
        "--timeout",
        help="Change the download timeout",
        metavar="SECONDS",
        type=int,
        dest="timeout",
    )
    parser_conf.add_argument(
        "--rule-reset",
        help="Resets the replacement rules to the default",
        action="store_true",
        dest="replacement_reset",
    )
    parser_conf.add_argument(
        "--rule-print",
        help="Prints the current replacement rules",
        action="store_true",
        dest="rule_print",
    )
    parser_conf.add_argument(
        "--data-saver",
        help="Toggles the date saving setting",
        action="store_true",
        dest="data_saver",
    )

    replacement_rules_group = parser_conf.add_mutually_exclusive_group()
    replacement_rules_group.add_argument(
        "--rule-add",
        help="Adds a new replacement rule for a character. If no replacement given it will default to removing it.",
        nargs="+",
        metavar=("CHARACTER", "REPLACEMENT"),
        dest="rule_add",
    )
    replacement_rules_group.add_argument(
        "--rule-remove",
        help="Removes a replacement rule for a character",
        metavar="CHARACTER",
        dest="rule_remove",
    )

    # Update options
    input_group_update = parser_update.add_mutually_exclusive_group()
    input_group_update.add_argument(
        "-c",
        "--check",
        help="Only check for new chapters without downloading and asking for any input",
        action="store_true",
        dest="check_only",
    )
    input_group_update.add_argument(
        "-i",
        "--ignore-input",
        help="Downloads without asking for any input (in case of group conflict the alphabetically first group will be chosen)",
        action="store_true",
        dest="ignore_input",
    )

    parser_update.add_argument(
        "-d",
        "--directory",
        dest="custom_down_dire",
        metavar="PATH/TO/DIRECTORY",
        default=None,
        help="Custom path for manga download",
    )
    parser_update.add_argument(
        "--language",
        help="Overwrite the Mangadex language setting",
        dest="langauge_code",
    )
    parser_update.add_argument(
        "--data-saver",
        help="Toggle the Mangadex data saver option. Takes priority over config file.",
        choices=["y", "yes", "n", "no"],
        metavar=r"{yes(y),no(n)}",
        dest="data_saver",
    )

    # Version options
    parser_version.add_argument(
        "-c",
        "--check",
        help="Checks if there is a new version available",
        action="store_true",
        dest="version_check",
    )

    return parser.parse_args()
