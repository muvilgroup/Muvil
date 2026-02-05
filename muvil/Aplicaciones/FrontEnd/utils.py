import re

def codificar_numeros(texto):
    # Expresión regular para detectar 9 números seguidos
    regex_list = [
        r'\d{9}',  # 9 números seguidos
        r'\d{3}\s?\d{3}\s?\d{3}',  # 9 números seguidos al quitar los espacios entre ellos (de 3 e 3)
        r'\d\s?\d\s?\d\s?\d\s?\d\s?\d\s?\d\s?\d\s?\d', # 9 numeros seguidos quitando los posibles espacios por medio
        r'\d{3}\s?\d{3}\s?\d{3}',
        r'nueve|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve\s?(y\s?)?nueve\s?(y\s?)?nueve',
        # 9 números seguidos escritos como texto de forma individual
        r'\d{3}[\W]?\d{3}[\W]?\d{3}'  # 9 números seguidos al quitar los caracteres especiales
    ]

    # Iterar sobre cada expresión regular y reemplazar con '*'
    for regex in regex_list:
        matches = re.finditer(regex, texto)
        for match in matches:
            texto = texto.replace(match.group(), '*' * len(match.group()))

    return texto
