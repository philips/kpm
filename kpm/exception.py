class KpmException(Exception):
    status_code = 500
    errorcode = "internal-error"

    def __init__(self, message, payload=None):
        Exception.__init__(self)
        self.payload = dict(payload or ())
        self.message = message

    def to_dict(self):
        r = {"code": self.errorcode,
             "message": self.message,
             "details": self.payload}
        return r

    def __str__(self):
        return self.message


class InvalidUsage(KpmException):
    status_code = 400
    errorcode = "invalid-usage"


class InvalidVersion(KpmException):
    status_code = 422
    errorcode = "invalid-version"


class PackageAlreadyExists(KpmException):
    status_code = 409
    errorcode = "package-exists"


class PackageNotFound(KpmException):
    status_code = 404
    errorcode = "package-not-found"


class PackageVersionNotFound(KpmException):
    status_code = 404
    errorcode = "package-version-not-found"


class UnauthorizedAccess(KpmException):
    status_code = 401
    errorcode = "unauthorized-access"
