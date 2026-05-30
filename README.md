# Analizador Integral de Cónicas desde RUT Chileno

Sistema completo de 9 módulos para validar RUTs chilenos, generar ecuaciones de cónicas, transformarlas a forma canónica, renderizar gráficos y analizar funciones por partes con discontinuidades.

## Descripción General

Este proyecto implementa un **sistema completo de 9 módulos** que procesa un RUT chileno y realiza:

1. **Validación del RUT** con algoritmo Módulo 11
2. **Cálculo de coeficientes** (A, B, C, D, E) para ecuación general de cónicas
3. **Ajustes automáticos** para generar variedad de cónicas
4. **Clasificación automática** del tipo de cónica
5. **Explicaciones detalladas** de la construcción de ecuaciones
6. **Transformación a forma canónica** con completamiento de cuadrados
7. **Interfaz gráfica** intuitiva (GUI con Tkinter)
8. **Renderizado de gráficos** de cónicas en plano cartesiano
9. **Análisis de funciones por partes** con discontinuidades

## Estructura del Proyecto

```
├── main.py                              # Orquestador principal (CLI + GUI)
├── README.md                            # Este archivo
├── .gitignore
│
└── src/
    ├── __init__.py
    ├── rut_validator.py                # Módulo 1: Validación RUT (Módulo 11)
    ├── coefficient_engine.py           # Módulo 2: Orquestador (invoca M3-M6, M9)
    ├── conic_rules_adjuster.py         # Módulo 3: 3 ajustes específicos
    ├── conic_classifier.py             # Módulo 4: Clasificación de 4 tipos
    ├── text_generator.py               # Módulo 5: Explicaciones paso a paso
    ├── canonical_transformer.py        # Módulo 6: General → Canónica
    ├── gui_interface.py                # Módulo 7: GUI Tkinter profesional
    ├── graphics_renderer.py            # Módulo 8: Renderizado Matplotlib (sin numpy)
    └── piecewise_functions_analyzer.py # Módulo 9: Funciones por partes
```

## Especificación Detallada de Módulos

### Módulo 1: Validador RUT 🆔
**Archivo:** `src/rut_validator.py`

Valida RUTs chilenos usando **algoritmo Módulo 11**:
- Formato: XX.XXX.XXX-X o XX.XXX.XXXx
- Soporta K/k como dígito verificador  
- Multiplicadores: 2-7 (derecha a izquierda)
- Procedimiento paso a paso con justificaciones
- Manejo de errores con mensajes descriptivos

### Módulo 2: Motor de Coeficientes 🔢
**Archivo:** `src/coefficient_engine.py`

Orquestador central que coordina módulos:
- Calcula variable v según dígito verificador
- Computa coeficientes: A, B, C, D, E
- Invoca Módulos 3, 4, 5, 6, 9 automáticamente
- Retorna diccionario completo con todos los resultados

### Módulo 3: Ajustes de Cónicas ⚙️
**Archivo:** `src/conic_rules_adjuster.py`

**3 reglas de ajuste secuenciales:**
- Hipérbolas (d₈ impar): B = -B
- Circunferencias (d₁ = d₂): B = A
- Parábolas ((d₅+d₆) % 3 = 0): A=0 o B=0

### Módulo 4: Clasificador Geométrico 📐
**Archivo:** `src/conic_classifier.py`

Clasifica **4 tipos de cónicas** automáticamente:
- Circunferencia: A = B ≠ 0, A·B > 0
- Elipse: A ≠ B, A·B > 0
- Hipérbola: A·B < 0
- Parábola: A = 0 ∨ B = 0

### Módulo 5: Generador de Explicaciones 📝
**Archivo:** `src/text_generator.py`

Genera **5 pasos detallados** de construcción de ecuación:
- Cálculo de v y coeficientes
- Aplicación de ajustes
- Comparación antes/después
- Ecuación final en fracciones y decimales

### Módulo 6: Transformación Canónica ✨
**Archivo:** `src/canonical_transformer.py`

Transforma **Ecuación General → Forma Canónica** para **4 cónicas**:
- Circunferencia: (x-h)² + (y-k)² = r²
- Elipse: (x-h)²/a² + (y-k)²/b² = 1
- Hipérbola: (x-h)²/a² - (y-k)²/b² = 1
- Parábola: (y-k)² = 4p(x-h)

Incluye completamiento de cuadrados paso a paso y procedimiento inverso.

### Módulo 7: Interfaz Gráfica (GUI) 🖥️
**Archivo:** `src/gui_interface.py`

**Interfaz Tkinter profesional:**
- Campo entrada para RUT
- Selector formato (fracción/decimal)
- Panel izquierdo: desarrollo paso a paso
- Panel derecho: gráfico en tiempo real
- Footer: parámetros canónicos
- Tema moderno con paleta azul corporativa

### Módulo 8: Renderizado de Gráficos 📊
**Archivo:** `src/graphics_renderer.py`

**Dibuja cónicas en plano cartesiano** usando Matplotlib:
- Circunferencia: Centro + perímetro
- Elipse: Semiejes + focos
- Hipérbola: Dos ramas + centro
- Parábola: Curva + vértice + directriz

**SIN numpy/scipy/sympy:** Implementación pura en Python con métodos auxiliares.

### Módulo 9: Análisis de Funciones por Partes 🔄
**Archivo:** `src/piecewise_functions_analyzer.py`

Analiza **3 tipos de discontinuidades** (determinados por **d8 % 3**):

- **Caso 0:** Discontinuidad Removible (agujero)
- **Caso 1:** Discontinuidad de Salto (finito)
- **Caso 2:** Discontinuidad Infinita (asíntota vertical)

Para cada caso genera: función, procedimiento 5-6 pasos, análisis de límites, tabla de valores, tipo de discontinuidad.

## Modo de Uso

### Modo GUI (Default - Recomendado)
```bash
python main.py
```
Abre interfaz gráfica Tkinter interactiva.

### Modo CLI
```bash
python main.py --cli
# o
python main.py cli
```
Interfaz de línea de comandos con prompts.

## Flujo de Ejecución  

```
RUT Input (Módulo 1)
    ↓
Validación 
    ↓
Cálculo Coeficientes (Módulo 2)
    ├→ Ajustes (Módulo 3)
    ├→ Clasificación (Módulo 4)  
    ├→ Explicaciones (Módulo 5)
    ├→ Transformación (Módulo 6)
    └→ Función por Partes (Módulo 9)
    ↓
Salida Resultados
    ├→ GUI (Módulo 7)
    ├→ Gráfico (Módulo 8)
    └→ Análisis (Módulo 9)
```

## Conformidad con Pauta

### Algoritmos Matemáticos ✅
- Validación RUT Módulo 11
- Cálculo correcto de coeficientes
- 3 ajustes específicos
- Clasificación automática 4 tipos
- Completamiento de cuadrados
- Transformación a canónica
- Análisis de funciones por partes

### Requerimientos Funcionales ✅
- Validador con procedimiento paso a paso
- Ecuación general con coeficientes A, B, C, D, E
- 3 Ajustes de cónicas
- Clasificación automática
- Explicaciones paso a paso
- Transformación a forma canónica
- Parámetros canónicos extraídos
- Procedimiento inverso
- Función por partes (3 casos)
- Análisis de límites y discontinuidades
- Gráficos en plano cartesiano
- Interfaz gráfica profesional
- Todo integrado en un programa

### Código Profesional ✅
- GitHub usage
- 3+ commits por persona  
- Organización modular
- Nombres descriptivos
- Comentarios necesarios
- Manejo de errores
- Código limpio y legible

## Requisitos

- Python 3.7+
- Tkinter (incluido en Python)
- Matplotlib
- Sin numpy, scipy, sympy, pandas

## Notas Técnicas

- Coeficientes simplificados automáticamente
- Decimales redondeados a 2 lugares
- Todo en Python puro (sin librerías prohibidas)
- Compatible Windows, MacOS, Linux

## Asignatura

MAT1186 - Introducción al Cálculo - Semestre 3, 2026

