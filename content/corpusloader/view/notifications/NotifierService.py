import panel


class NotifierService:
    """
    Provides an object to handle GUI notifications as an indirection from the Panel library notifications.
    """
    def __init__(self):
        panel.config.notifications = True

    def notify_error(self, error_msg: str):
        """
        Renders the provided error message. The notification will last indefinitely until the user dismisses it.
        :param error_msg: The error message to be displayed as a string
        """
        panel.state.notifications.error(error_msg, duration=0)

    def notify_success(self, success_msg: str):
        """
        Renders the provided success message. The notification will last for 3 seconds or until the user dismisses it.
        :param success_msg: The success message to be displayed as a string
        """
        panel.state.notifications.success(success_msg, duration=3000)
