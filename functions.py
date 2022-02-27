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

def index_of(thing, list_of_things):
    for i in range(len(list_of_things)):
        if list_of_things[i] == thing:
            return i
    else:
        return False
