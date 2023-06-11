import win32security


class Roles:
    FULL_ACCESS = "FULL"
    READ_WRITE = "READ_WRITE"
    READ_ONLY = "READ_ONLY"


class PrivilegeChecker:
    class Masks:
        FILE_READ_DATA = 0x0001
        FILE_WRITE_DATA = 0x0002
        FILE_EXECUTE = 0x0020

    def __init__(self, role, access_mask):
        self.role = role
        self.access_mask = access_mask

    def check_permissions(self):
        if self.role == Roles.FULL_ACCESS:
            return self._has_full()
        elif self.role == Roles.READ_WRITE:
            return self._has_read() and self._has_write() and not self._has_full()
        elif self.role == Roles.READ_ONLY:
            return self._has_read() and not self._has_write()

    def _has_read(self):
        return self.access_mask & self.Masks.FILE_READ_DATA != 0

    def _has_write(self):
        return self.access_mask & self.Masks.FILE_WRITE_DATA != 0

    def _has_full(self):
        return self.access_mask == 2032127
