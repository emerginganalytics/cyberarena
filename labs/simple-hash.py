import hashlib

cont = "y"
while cont == "y":
    password = input("\nPassword: ")
    hashed_password_md5 = hashlib.md5(str(password).encode("UTF-8")).hexdigest()
    print("md5:\t", hashed_password_md5)
    cont = input("\nContinue? (y/n): ")
