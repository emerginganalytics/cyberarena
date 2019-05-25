import hashlib


def md5(password):

    for password in range(len(password)):
        return hashlib.md5(str(password).encode("UTF-8")).hexdigest()
