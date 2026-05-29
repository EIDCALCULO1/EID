"""
Módulo 4: Clasificador Geométrico

Este módulo implementa la clasificación automática de cónicas según los
criterios especificados en la pauta oficial.

Criterios de clasificación (según pauta):
- Circunferencia: Si A = B (ambos ≠ 0)
- Elipse: Si A y B tienen el MISMO signo y A ≠ B
- Hipérbola: Si A y B tienen SIGNOS OPUESTOS
- Parábola: Si EXACTAMENTE UNO de {A, B} es cero
"""


def tienen_mismo_signo(a, b):
    """
    Verifica si dos números tienen el mismo signo.
    
    Retorna True si ambos son positivos o ambos son negativos.
    """
    return (a > 0 and b > 0) or (a < 0 and b < 0)


def tienen_signos_opuestos(a, b):
    """
    Verifica si dos números tienen signos opuestos.
    
    Retorna True si uno es positivo y otro es negativo.
    """
    return (a > 0 and b < 0) or (a < 0 and b > 0)


def clasificar_conica(A, B, C, D, E):
    """
    Clasifica automáticamente el tipo de cónica según los criterios de la pauta.
    
    Parámetros:
    - A, B, C, D, E: coeficientes de la ecuación general Ax² + By² + Cx + Dy + E = 0
    
    Retorna diccionario con:
    - type: 'circunferencia', 'elipse', 'hipérbola', o 'parábola'
    - justification: explicación clara y rigurosa del criterio aplicado
    - is_valid: True si la clasificación es válida
    - error: mensaje de error si no es válida (None si no hay error)
    """
    
    # ================================================================
    # CRITERIO 1: PARÁBOLA
    # Si exactamente UNO de {A, B} es igual a cero
    # ================================================================
    exactly_one_is_zero = (A == 0 and B != 0) or (A != 0 and B == 0)
    
    if exactly_one_is_zero:
        if A == 0:
            axis = "horizontal (eje X)"
        else:
            axis = "vertical (eje Y)"
        
        return {
            'type': 'parábola',
            'axis': axis,
            'justification': (
                f"Exactamente uno de {{A, B}} es cero:\n"
                f"  A = {A}\n"
                f"  B = {B}\n"
                f"  Criterio: Si A = 0 O B = 0 (solo uno) → PARÁBOLA\n"
                f"  Orientación: Eje {axis}"
            ),
            'is_valid': True,
            'error': None
        }
    
    # ================================================================
    # CRITERIO 2: CIRCUNFERENCIA
    # Si A = B (ambos distintos de cero)
    # ================================================================
    if A == B and A != 0 and B != 0:
        return {
            'type': 'circunferencia',
            'justification': (
                f"Coeficientes A y B son iguales y distintos de cero:\n"
                f"  A = {A}\n"
                f"  B = {B}\n"
                f"  Criterio: Si A = B (ambos ≠ 0) → CIRCUNFERENCIA"
            ),
            'is_valid': True,
            'error': None
        }
    
    # ================================================================
    # CRITERIO 3: HIPÉRBOLA
    # Si A y B tienen signos opuestos
    # ================================================================
    if tienen_signos_opuestos(A, B):
        return {
            'type': 'hipérbola',
            'justification': (
                f"Los coeficientes A y B tienen signos opuestos:\n"
                f"  A = {A} ({('positivo' if A > 0 else 'negativo')})\n"
                f"  B = {B} ({('positivo' if B > 0 else 'negativo')})\n"
                f"  Criterio: Si A y B tienen signos opuestos → HIPÉRBOLA"
            ),
            'is_valid': True,
            'error': None
        }
    
    # ================================================================
    # CRITERIO 4: ELIPSE
    # Si A y B tienen el MISMO signo y A ≠ B
    # ================================================================
    if tienen_mismo_signo(A, B) and A != B:
        return {
            'type': 'elipse',
            'justification': (
                f"Los coeficientes A y B tienen el mismo signo y son distintos:\n"
                f"  A = {A} ({('positivo' if A > 0 else 'negativo')})\n"
                f"  B = {B} ({('positivo' if B > 0 else 'negativo')})\n"
                f"  Mismo signo: Sí\n"
                f"  A ≠ B: Sí\n"
                f"  Criterio: Si A y B tienen el mismo signo y A ≠ B → ELIPSE"
            ),
            'is_valid': True,
            'error': None
        }
    
    # ================================================================
    # CASO ESPECIAL: Ambos A y B son cero (degenerado)
    # ================================================================
    if A == 0 and B == 0:
        return {
            'type': 'degenerado',
            'justification': (
                f"Ambos coeficientes A y B son cero:\n"
                f"  A = {A}\n"
                f"  B = {B}\n"
                f"  Nota: Esta ecuación no representa una cónica válida.\n"
                f"  Se reduce a una ecuación lineal: Cx + Dy + E = 0"
            ),
            'is_valid': False,
            'error': "No es una cónica: ambos A y B son cero"
        }
    
    # ================================================================
    # CASO NO CLASIFICABLE (no debería ocurrir si la lógica es completa)
    # ================================================================
    return {
        'type': 'no clasificada',
        'justification': "No se pudo clasificar la cónica con los criterios especificados.",
        'is_valid': False,
        'error': f"Combinación inesperada: A={A}, B={B}"
    }


def obtener_reglas_clasificacion_conicas():
    """
    Retorna una descripción clara de las reglas de clasificación de cónicas.
    
    Útil para mostrar en la interfaz o para documentación.
    """
    rules = """
CRITERIOS DE CLASIFICACIÓN DE CÓNICAS (según pauta):

1. CIRCUNFERENCIA:
   Condición: A = B (ambos ≠ 0)
   Ejemplo: Si A = 3 y B = 3

2. ELIPSE:
   Condición: A y B tienen el MISMO signo y A ≠ B
   Ejemplo: Si A = 2 y B = 5 (ambos positivos)
   Ejemplo: Si A = -2 y B = -5 (ambos negativos)

3. HIPÉRBOLA:
   Condición: A y B tienen SIGNOS OPUESTOS
   Ejemplo: Si A = 3 y B = -2

4. PARÁBOLA:
   Condición: Exactamente UNO de {A, B} es cero
   Si A = 0: Parábola de eje horizontal
   Si B = 0: Parábola de eje vertical
   Ejemplo: Si A = 0 y B = 2 (eje horizontal)
   Ejemplo: Si A = 2 y B = 0 (eje vertical)

Nota: Los criterios son mutuamente excluyentes y exhaustivos.
"""
    return rules
