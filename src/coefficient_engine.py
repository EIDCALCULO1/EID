"""
Módulo 2: Motor de Coeficientes Base
Calcula los coeficientes iniciales A, B, C, D, E a partir del RUT.
Orquesta todos los módulos: 1-6 (cónicas) y 9 (funciones por partes).
"""

from src.conic_rules_adjuster import aplicar_reglas_conicas
from src.conic_classifier import clasificar_conica
from src.text_generator import generar_explicacion_construccion_ecuacion, generar_comparacion_ecuacion_ajustada
from src.canonical_transformer import transformar_conica_general_a_canonica, resumen_transformacion_inversa
from src.piecewise_functions_analyzer import AnalizadorFuncionesPorPartes


def mcd(a, b):
    """Calcula máximo común divisor usando Euclides."""
    while b:
        a, b = b, a % b
    return a


def simplificar_fraccion(numerator, denominator):
    """Simplifica una fracción retornando (num_simplificado, den_simplificado)."""
    if denominator == 0:
        raise ValueError("Denominador no puede ser cero")
    
    factor = mcd(abs(numerator), abs(denominator))
    return numerator // factor, denominator // factor


def calcular_v(dv):
    """
    Calcula variable v basada en el dígito verificador.
    - Si DV = 'K', v = 10
    - Si DV = '0', v = 11
    - Sino, v = int(DV)
    """
    if dv == 'K':
        return 10
    elif dv == '0':
        return 11
    else:
        return int(dv)


def redondear_a_2_decimales(value):
    """
    Redondea un número a máximo 2 decimales.
    Si el resultado es un número entero, lo muestra sin decimales.
    
    Parámetros:
    - value: número a redondear
    
    Retorna el número redondeado o formateado correctamente
    """
    rounded = round(value, 2)
    # Si el resultado es un número entero, retorna sin decimales
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def construir_ecuacion_general(A, B, C, D, E, A_frac=None, B_frac=None, use_fractions=False):
    """
    Construye la ecuación general en formato matemático correcto.
    
    Respeta los signos: valores negativos se muestran como resta,
    no como suma de negativos.
    
    Parámetros:
    - A, B, C, D, E: coeficientes (decimales)
    - A_frac, B_frac: fracciones (num, den) - opcional
    - use_fractions: si True, usa fracciones para A y B; si False, usa decimales redondeados
    
    Retorna string con la ecuación formateada
    """
    terms = []
    
    # Formatear A
    if use_fractions and A_frac:
        A_str = f"{A_frac[0]}/{A_frac[1]}"
    else:
        A_val = redondear_a_2_decimales(A)
        A_str = str(A_val)
    
    if A >= 0:
        terms.append(f"{A_str}x²")
    else:
        terms.append(f"-{A_str}x²")
    
    # Formatear B
    if use_fractions and B_frac:
        B_str = f"{B_frac[0]}/{B_frac[1]}"
    else:
        B_val = redondear_a_2_decimales(B)
        B_str = str(B_val)
    
    if B >= 0:
        terms.append(f"+ {B_str}y²")
    else:        
        terms.append(f"- {B_str}y²")
    
    # C, D, E son siempre enteros
    terms.append(("+" if C >= 0 else "-") + f" {abs(C)}x")
    terms.append(("+" if D >= 0 else "-") + f" {abs(D)}y")
    terms.append(("+" if E >= 0 else "-") + f" {abs(E)}")
    
    equation = " ".join(terms) + " = 0"
    return equation


def mostrar_procedimiento_coeficientes(digits, dv, use_fractions=True):
    """
    Genera el procedimiento paso a paso para el cálculo de coeficientes.
    
    Parámetros:
    - digits: tupla de 8 dígitos
    - dv: dígito verificador
    - use_fractions: si True muestra fracciones, si False muestra decimales
    
    Retorna string con el procedimiento detallado
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digits
    v = calcular_v(dv)
    
    # Calcular valores
    sum_d1_d2 = d1 + d2
    sum_d3_d4 = d3 + d4
    A_num, A_den = simplificar_fraccion(sum_d1_d2, v)
    B_num, B_den = simplificar_fraccion(sum_d3_d4, v)
    A = sum_d1_d2 / v
    B = sum_d3_d4 / v
    C = -(d5 + d6)
    D = -(d7 + d8)
    E = d1 + d3 + d5 + d7
    
    procedure = "\n"
    
    # Procedimiento para A
    procedure += f"Coeficiente A:\n"
    procedure += f"  Formula: A = (d1 + d2) / v\n"
    procedure += f"  Sustitucion: A = ({d1} + {d2}) / {v}\n"
    procedure += f"  Suma: A = {sum_d1_d2} / {v}\n"
    if use_fractions:
        procedure += f"  Simplificacion: A = {A_num}/{A_den}\n"
    else:
        procedure += f"  Resultado: A = {redondear_a_2_decimales(A)}\n"
    
    # Procedimiento para B
    procedure += f"\nCoeficiente B:\n"
    procedure += f"  Formula: B = (d3 + d4) / v\n"
    procedure += f"  Sustitucion: B = ({d3} + {d4}) / {v}\n"
    procedure += f"  Suma: B = {sum_d3_d4} / {v}\n"
    if use_fractions:
        procedure += f"  Simplificacion: B = {B_num}/{B_den}\n"
    else:
        procedure += f"  Resultado: B = {redondear_a_2_decimales(B)}\n"
    
    # Procedimiento para C
    procedure += f"\nCoeficiente C:\n"
    procedure += f"  Formula: C = -(d5 + d6)\n"
    procedure += f"  Sustitucion: C = -({d5} + {d6})\n"
    procedure += f"  Resultado: C = {C}\n"
    
    # Procedimiento para D
    procedure += f"\nCoeficiente D:\n"
    procedure += f"  Formula: D = -(d7 + d8)\n"
    procedure += f"  Sustitucion: D = -({d7} + {d8})\n"
    procedure += f"  Resultado: D = {D}\n"
    
    # Procedimiento para E
    procedure += f"\nCoeficiente E:\n"
    procedure += f"  Formula: E = d1 + d3 + d5 + d7\n"
    procedure += f"  Sustitucion: E = {d1} + {d3} + {d5} + {d7}\n"
    procedure += f"  Resultado: E = {E}\n"
    
    return procedure


def calcular_coeficientes(digits, dv):
    """
    Calcula los coeficientes A, B, C, D, E.
    
    Parámetros:
    - digits: tupla de 8 dígitos (d_1 a d_8)
    - dv: dígito verificador (str)
    
    Retorna diccionario con:
    - A, B, C, D, E: valores decimales
    - A_frac, B_frac: fracciones (num, den)
    - equation_fraction: ecuación con fracciones
    - equation_decimal: ecuación con decimales redondeados
    - adjustments: lista de ajustes aplicados
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digits
    
    v = calcular_v(dv)
    
    # Calcular valores iniciales
    sum_d1_d2 = d1 + d2
    A_num, A_den = simplificar_fraccion(sum_d1_d2, v)
    A = sum_d1_d2 / v
    
    # Calcular B = (d_3 + d_4) / v
    sum_d3_d4 = d3 + d4
    B_num, B_den = simplificar_fraccion(sum_d3_d4, v)
    B = sum_d3_d4 / v
    
    # Calcular C = -(d_5 + d_6)
    C = -(d5 + d6)
    
    # Calcular D = -(d_7 + d_8)
    D = -(d7 + d8)
    
    # Calcular E = d_1 + d_3 + d_5 + d_7
    E = d1 + d3 + d5 + d7
    
    # Calcular valores iniciales ANTES de ajustes (para comparación del Módulo 5)
    A_before_adjustments = sum_d1_d2 / v
    B_before_adjustments = sum_d3_d4 / v
    B_num_before = B_num
    B_den_before = B_den
    if d8 % 2 == 1:  # Simulación del primer ajuste
        B_num_before = -B_num_before
    
    # ================================================================
    # APLICAR AJUSTES DE CÓNICAS (Módulo 3)
    # ================================================================
    A, B, (A_num, A_den), (B_num, B_den), adjustments = aplicar_reglas_conicas(
        A, B, (A_num, A_den), (B_num, B_den), digits
    )
    
    # ================================================================
    # CLASIFICAR CÓNICA (Módulo 4)
    # ================================================================
    conic_classification = clasificar_conica(A, B, C, D, E)
    
    # ================================================================
    # GENERAR EXPLICACIONES TEXTUALES (Módulo 5)
    # ================================================================
    explanation_fraction = generar_explicacion_construccion_ecuacion(
        digits, dv, A, B, C, D, E, 
        (A_num, A_den), (B_num, B_den), v, adjustments,
        conic_classification['type'], use_fractions=True
    )
    
    explanation_decimal = generar_explicacion_construccion_ecuacion(
        digits, dv, A, B, C, D, E, 
        (A_num, A_den), (B_num, B_den), v, adjustments,
        conic_classification['type'], use_fractions=False
    )
    
    adjusted_comparison = generar_comparacion_ecuacion_ajustada(
        A_before_adjustments, B_before_adjustments, A, B, adjustments
    )
    
    # ================================================================
    # TRANSFORMACIÓN A FORMA CANÓNICA (Módulo 6)
    # ================================================================
    canonical_result = transformar_conica_general_a_canonica(
        A, B, C, D, E, conic_classification['type']
    )
    
    # Generar procedimiento inverso
    inverse_proc = resumen_transformacion_inversa(
        A, B, C, D, E, conic_classification['type']
    )
    
    # ================================================================
    # ANÁLISIS DE FUNCIONES POR PARTES (Módulo 9)
    # ================================================================
    piecewise_analyzer = AnalizadorFuncionesPorPartes(digits, dv)
    piecewise_analysis = piecewise_analyzer.get_full_analysis()
    
    return {
        'A': A,
        'B': B,
        'C': C,
        'D': D,
        'E': E,
        'A_frac': (A_num, A_den),
        'B_frac': (B_num, B_den),
        'v': v,
        'adjustments': adjustments,
        'conic_type': conic_classification['type'],
        'conic_classification': conic_classification,
        'equation_fraction': construir_ecuacion_general(A, B, C, D, E, A_frac=(A_num, A_den), B_frac=(B_num, B_den), use_fractions=True),
        'equation_decimal': construir_ecuacion_general(A, B, C, D, E, A_frac=(A_num, A_den), B_frac=(B_num, B_den), use_fractions=False),
        'explanation_fraction': explanation_fraction,
        'explanation_decimal': explanation_decimal,
        'adjusted_comparison': adjusted_comparison,
        'canonical_transformation': canonical_result,
        'inverse_transformation': inverse_proc,
        'piecewise_analysis': piecewise_analysis
    }
