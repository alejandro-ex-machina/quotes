# Quotes

Script en Python para mostrar una cita aleatoria en consola desde `quotes.json`. Probado en Windows y Termux.

## Requisitos

- Python 3.8 o superior
- Archivo `quotes.json` en el mismo directorio que `getquote.py`

## Archivos

- `getquote.py`: carga el JSON y muestra una cita aleatoria.
- `quotes.json`: lista de citas con autor y referencia opcional.

## Formato de `quotes.json`

El script espera una lista de objetos con estas claves:

- `author` (string)
- `quote` (string)
- `ref` (string, opcional o vacio)

Ejemplo:

```json
[
  {
    "author": "Arthur Schopenhauer",
    "quote": "La vida es un pendulo que oscila entre el dolor y el aburrimiento",
    "ref": "El mundo como voluntad y representacion"
  }
]
```

## Uso desde consola

### Clonar el repositorio

```shell
cd ~/src
git clone https://github.com/alejandro-ex-machina/quotes.git
```

### Uso

```shell
python ~/src/quotes/getquote.py
python ~/src/quotes/getquote.py --category=Filosofía
python ~/src/quotes/getquote.py --author=Epicteto
python ~/src/quotes/getquote.py --category=Informática --author=Donald\ E.\ Knuth
python ~/src/quotes/getquote.py --list-autors
python ~/src/quotes/getquote.py --list_categories
```

## Salida esperada

- Imprime una cita aleatoria entre comillas.
- Imprime el autor en negrita (si la terminal soporta ANSI).
- Si existe, agrega la referencia entre parentesis.
- Imprime al final el numero total de citas cargadas.

```shell
«En matemáticas no se entienden las cosas, simplemente uno se acostumbra a ellas».

John von Neumann

258 quotes
```

## Citas

`quotes.json` incluye citas de:

- Alan Turing (10)
- Arnold J. Toynbee (10)
- Arthur Schopenhauer (17)
- Carl Jung (15)
- Carl von Clausewitz (14)
- Cicerón (14)
- David Lane (8)
- Dennis Ritchie (15)
- Donald E. Knuth (17)
- Edsger W. Dijkstra (14)
- Epicteto (14)
- Ernst Jünger (14)
- Federico II de Prusia (8)
- Ferdinand Porsche (3)
- Friedrich Nietzsche (14)
- Henry Ford (12)
- Hugo Junkers (3)
- Immanuel Kant (12)
- John von Neumann (12)
- Marco Aurelio (14)
- Mark Twain (12)
- Miyamoto Musashi (12)
- Oswald Spengler (14)
- Otto Skorzeny (20)
- Otto von Bismarck (8)
- Richard Feynman (14)
- Séneca (10)
- Ted Kaczynski (14)
- Wernher von Braun (4)
- Willy Messerschmitt (3)

## Notas

- Si `quotes.json` esta vacio, el script termina con error.
- Si ves caracteres raros en consola, revisa la codificacion de terminal/archivo (UTF-8 recomendado).
