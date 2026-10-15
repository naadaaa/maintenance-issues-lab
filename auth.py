def check_password(pw):
    if len(pw) > 30:
        return False
    if pw.lower() == "password":
        return False
    if not any(c.isdigit() for c in pw):
        return False
    return True
