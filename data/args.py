from argparse import ArgumentParser


def create_parser() -> ArgumentParser: 
    """
    Use this method to create a new argument parser.

    Returns:
        parser (ArgumentParser): Object to parse CLI arguments.
    """

    parser = ArgumentParser(description="Hearthstone exp farming bot.")

    parser.add_argument(
        "-t",
        "--tg_notification",
        help="Sends a telegram notification when the battle starts.",
        action="store_true"
        )

    parser.add_argument(
        "-p",
        "--pre_run_menu",
        help=(
            'Use this option if you are in mercs mode and looking at "Choose" location button.'
            'Otherwise program will open a new hearthstone window.'
        ),
        action="store_true"
    )

    return parser