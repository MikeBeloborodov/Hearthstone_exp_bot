class MaxTriesReached(Exception):
    """
    Raised when the maximum tries of finding a target on the screen is reached.
    """
    pass


class MissingAbilityButton(Exception):
    """
    Raised when battle sequence method could not find an ability icon.
    """
    pass


class MissingEnemyButton(Exception):
    """
    Raised when battle sequence method could not find an enemy icon.
    """
    pass


class MissingFightButton(Exception):
    """
    Raised when battle sequence method could not find the fight button.
    """
    pass