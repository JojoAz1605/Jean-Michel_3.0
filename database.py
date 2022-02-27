from functions import index_of


class Database:
    def __init__(self, name: str):
        self.name = name
        self.keys = []
        self.__readKeys()

    def __readKeys(self) -> None:
        """Lit les clés de la base de données"""
        file = open(self.name, 'r')
        lines = file.readlines()
        file.close()
        for line in lines:
            key = ''
            for char in line:
                if char == '=':
                    break
                key += char
            self.keys.append(key)

    def get_value(self, key: str) -> str:
        """Retourne la valeure de la clé donnée, ou rien si elle n'existe pas
        :param key: La clé de la valeur
        :return: La valeur de la clé
        """
        if key not in self.keys:
            return ""
        else:
            file = open(self.name, 'r')
            thing_to_return = file.readlines()[index_of(key, self.keys)]
            file.close()
            return thing_to_return[len(key)+1:]

    def set_value(self, key: str, value: str) -> None:
        """Ecrit une valeur dans la base de donnée
        :param key: La clé de la valeur
        :param value: La valeur à écrire
        """
        if key not in self.keys:
            file = open(self.name, 'a')
            self.keys.append(key)
            file.write(f"{key}={value}\n")
        else:
            file = open(self.name, 'r+')
            lines = file.readlines()
            lines[index_of(key, self.keys)] = f"{key}={value}\n"
            file.close()
            file = open(self.name, 'w')
            for line in lines:
                file.write(line)
        file.close()
