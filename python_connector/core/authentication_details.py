class IAuthenticationDetails:

    def __init__(self):
        pass


class BasicAuthenticationDetails(IAuthenticationDetails):

    def __init__(self, user: str, password: str):
        self._user = user
        self._password = password
        super().__init__()


class NoAuthenticationDetails(IAuthenticationDetails):

    def __init__(self):
        super().__init__()
