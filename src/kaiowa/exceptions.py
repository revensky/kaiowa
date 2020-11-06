class KaiowaError(Exception):
    """
    Base class for exceptions that may be thrown in the execution of Kaiowá.

    :param message: Error message.
    :type message: str
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)

        self.message = message
