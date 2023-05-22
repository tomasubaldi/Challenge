title = "disney is in florida"
search_phrase = "disney florida"

# Dividir la frase de búsqueda en palabras
words = search_phrase.lower().split()

# Contar las ocurrencias de cada palabra en el título
phrase_count = sum(title.lower().count(word) for word in words)

print(phrase_count)