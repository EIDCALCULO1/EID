# Validador de RUT y Generador de Ecuaciones de Cónicas

Aplicación Python para validar RUTs chilenos y generar ecuaciones de cónicas a partir de los dígitos del RUT.

## Descripción

Este proyecto implementa un sistema que:

1. **Valida RUTs chilenos** usando el algoritmo Módulo 11
2. **Calcula coeficientes** (A, B, C, D, E) para una ecuación general de cónicas a partir de los 8 dígitos del RUT
3. **Aplica ajustes específicos** para generar distintos tipos de cónicas:
   - Hipérbolas (si d₈ es impar)
   - Circunferencias (si d₁ = d₂)
   - Parábolas (si (d₅ + d₆) es múltiplo de 3)
4. **Muestra el procedimiento paso a paso** para cada coeficiente
5. **Presenta la ecuación resultante** en formato de fracciones o decimales

## Estructura del Proyecto

```
├── main.py                        # Programa principal (interfaz de usuario)
├── src/
│   ├── rut_validator.py          # Módulo de validación de RUTs
│   └── coefficient_engine.py     # Motor de cálculo de coeficientes

## Uso

Ejecutar el programa principal:

```bash
python main.py
```

### Ejemplo de Interacción

```
Ingrese el RUT a validar (formato: XX.XXX.XXX-X): 22.303.126-9
¿Desea ver los resultados en fracción (f) o decimales (d)? (f/d): f
```

## Características Principales

### Validación de RUT
- Valida el formato XX.XXX.XXX-X
- Aplica el algoritmo Módulo 11
- Soporta tanto 'K' como 'k' como dígito verificador
- Proporciona mensajes de error detallados

### Cálculo de Coeficientes
- **A** = (d₁ + d₂) / v
- **B** = (d₃ + d₄) / v  
- **C** = -(d₅ + d₆)
- **D** = -(d₇ + d₈)
- **E** = d₁ + d₃ + d₅ + d₇

Donde v = dígito verificador (como número: K→10, 0→11, otros→su valor)

### Ajustes para Cónicas

**Ajuste 1 - Hipérbolas:**
- Si d₈ es impar → B = -B

**Ajuste 2 - Circunferencias:**
- Si d₁ = d₂ → B = A

**Ajuste 3 - Parábolas:**
- Si (d₅ + d₆) es múltiplo de 3:
  - Si d₇ es par → B = 0 (eje vertical)
  - Si d₇ es impar → A = 0 (eje horizontal)

## Ejemplos de Salida

### RUT con Ajuste 2 (Circunferencia)
```
RUT: 22.303.126-9
AJUSTES APLICADOS:
  * Ajuste 2: d1 = d2 = 2 -> Se impone B = A (circunferencia)

RESUMEN DE COEFICIENTES:
  A = 4/9
  B = 4/9
  C = -4
  D = -8
  E = 10

Ecuación General: 4/9x² + 4/9y² - 4x - 8y + 10 = 0
```

### RUT sin Ajustes
```
RUT: 12.345.678-5
No hay ajustes especiales

RESUMEN DE COEFICIENTES:
  A = 3/5
  B = 7/5
  C = -11
  D = -15
  E = 16

Ecuación General: 3/5x² + 7/5y² - 11x - 15y + 16 = 0
```

## Requisitos

- Python 3.7+

## Notas Técnicas

- Los coeficientes se simplifican automáticamente usando el máximo común divisor con la funcion "gdc"
- Los decimales se redondean a 2 lugares
- La ecuación respeta correctamente los signos (no usa "+ -" notation)
- La aplicación maneja correctamente caracteres especiales y acentos en terminal Windows

## Asignatura

MAT1186 - Introducción al Cálculo - Semestre 3, 2026
