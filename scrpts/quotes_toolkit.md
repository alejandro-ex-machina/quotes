# Quotes Toolkit

Este repositorio incluye utilidades para gestionar y mantener una colección de citas en formato JSON.

---

## Scripts incluidos

### 1. `getquote.py`

Muestra citas desde `quotes.json`.

Uso básico:

    python getquote.py

Filtros habituales:

    python getquote.py --author "Séneca"
    python getquote.py --category "Filosofía"
    python getquote.py --theme "ética"
    python getquote.py --quality high

Opciones útiles:

- `--all` muestra todas las citas filtradas
- `--paged` muestra las citas por bloques con pausa
- `--list_authors`
- `--list_categories`
- `--list_themes`

Además, el filtro por categoría admite jerarquía blanda. Ejemplos:

- `--category Ingeniería` incluye categorías como Ingeniería, Ingeniería Aeroespacial, Ingeniería Aeronáutica e Ingeniería Automotriz
- `--category Automotriz` filtra solo Ingeniería Automotriz

---

### 2. `merge_quotes.py`

Incorpora citas desde otro JSON a `quotes.json`.

Uso básico:

    python merge_quotes.py nuevas.json

Opciones:

- `--dry-run` no escribe cambios
- `--replace` reemplaza duplicados
- `--sort` ordena el resultado
- `--strict-theme` exige clave `theme`
- `--no-backup` desactiva la copia de seguridad

Comportamiento:

- deduplica por `author + quote`
- normaliza campos
- añade `theme` si falta
- crea backup automático antes de escribir

Ejemplo real:

    python .\scrpts\merge_quotes.py .\unamuno.json --target .\quotes.json

Salida típica:

    Destino:  C:\Users\asant\src\quotes\quotes.json
    Entrada:  C:\Users\asant\src\quotes\unamuno.json
    Inicial:  444
    Nuevas:   1
    Añadidas: 1
    Saltadas: 0
    Reemplaz.: 0
    Final:    445
    Backup:   C:\Users\asant\src\quotes\quotes.json.bak.20260414-003904
    Escrito:  C:\Users\asant\src\quotes\quotes.json

---

### 3. `review_quotes.py`

Analiza calidad y consistencia del archivo.

Uso básico:

    python review_quotes.py --quotes-file quotes.json

Generar informe:

    python review_quotes.py --report review.md

Qué detecta:

- campos obligatorios incompletos
- citas sin referencia (`ref`)
- themes vacíos o inválidos
- duplicados exactos
- duplicados semánticos por similitud
- distribución por calidad
- autores con varias citas de calidad baja

---

### 4. `quotes_toolkit.bat`

Helper para Windows con comandos rápidos.

Ejemplos:

    quotes_toolkit.bat random
    quotes_toolkit.bat review
    quotes_toolkit.bat report
    quotes_toolkit.bat merge nuevas.json
    quotes_toolkit.bat list themes
    quotes_toolkit.bat theme "ética"

Nota: si tu carpeta se llama `scripts` y no `scrpts`, ajusta las rutas internas del `.bat`.

---

### 5. `quotes_toolkit.sh`

Helper para Termux o Linux con el mismo flujo básico.

Ejemplos:

    chmod +x quotes_toolkit.sh
    ./quotes_toolkit.sh random
    ./quotes_toolkit.sh review
    ./quotes_toolkit.sh report
    ./quotes_toolkit.sh merge nuevas.json
    ./quotes_toolkit.sh list themes
    ./quotes_toolkit.sh author "Unamuno"

También acepta la variable `PYTHON_BIN` para elegir intérprete:

    PYTHON_BIN=python3 ./quotes_toolkit.sh review

Nota: igual que en Windows, si tu carpeta real es `scripts` y no `scrpts`, ajusta las rutas internas.

---

## Filosofía del sistema

Este proyecto prioriza:

- fiabilidad sobre popularidad
- citas verificables sobre frases virales
- consistencia estructural
- simplicidad operativa

---

## Estructura de una cita

Ejemplo:

    {
      "author": "Miguel de Unamuno",
      "quote": "El dolor es la sustancia de la vida y la raíz de la personalidad.",
      "ref": "Del sentimiento trágico de la vida",
      "category": "Filosofía",
      "theme": "carácter",
      "source_quality": "high"
    }

Campos habituales:

- `author`
- `quote`
- `ref`
- `category`
- `theme`
- `source_quality`

Recomendación:

- `author`, `quote` y `category` deben tener contenido
- `theme` debe existir siempre, aunque sea `""`
- `ref` conviene rellenarlo siempre que sea posible
- `source_quality` ayuda mucho a mantener criterio

---

## Flujo recomendado

1. Preparar nuevas citas en JSON
2. Integrar:

    python merge_quotes.py nuevas.json

3. Revisar:

    python review_quotes.py

4. Corregir y consolidar

---

## Notas

- Evita citas sin fuente clara cuando puedas
- Prefiere texto original frente a versiones populares o redondeadas
- Mantén los themes dentro del conjunto canónico
- Muchas citas famosas son paráfrasis, mezclas o atribuciones erróneas

---

## Estado actual

- colección en crecimiento y ya utilizable como corpus curado
- taxonomía temática unificada
- deduplicación automática
- revisión de calidad incorporada

---

## Futuras mejoras

- lint automático previo a commit
- detección más avanzada de duplicados
- metadatos adicionales como `source_type` o notas editoriales

---

Fin.
