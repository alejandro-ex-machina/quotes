# Quotes

Script en Python para mostrar una cita aleatoria desde `quotes.json` en consola.

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

```powershell
cd src\quotes
python getquote.py
```

## Salida esperada

- Imprime una cita aleatoria entre comillas.
- Imprime el autor en negrita (si la terminal soporta ANSI).
- Si existe, agrega la referencia entre parentesis.
- Imprime al final el numero total de citas cargadas.

## Notas

- Si `quotes.json` esta vacio, el script termina con error.
- Si ves caracteres raros en consola, revisa la codificacion de terminal/archivo (UTF-8 recomendado).
