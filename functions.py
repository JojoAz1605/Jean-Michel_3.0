def contain_bad_word(msg: str, liste_insultes: list[str]) -> bool:
    for bad_word in liste_insultes:
        if bad_word in msg.lower():
            return True
    return False

def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)
