"""
Módulo 2: Motor de Coeficientes Base
Calcula los coeficientes iniciales A, B, C, D, E a partir del RUT.
"""

def gcd(a, b):
    """Calcula máximo común divisor usando Euclides."""
    while b:
        a, b = b, a % b
    return a


def simplify_fraction(numerator, denominator):
    """Simplifica una fracción retornando (num_simplificado, den_simplificado)."""
    if denominator == 0:
        raise ValueError("Denominador no puede ser cero")
    
    factor = gcd(abs(numerator), abs(denominator))
    return numerator // factor, denominator // factor


def calculate_v(dv):
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


def round_to_2_decimals(value):
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


def build_general_equation(A, B, C, D, E, A_frac=None, B_frac=None, use_fractions=False):
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
        A_val = round_to_2_decimals(A)
        A_str = str(A_val)
    
    if A >= 0:
        terms.append(f"{A_str}x²")
    else:
        terms.append(f"-{A_str}x²")
    
    # Formatear B
    if use_fractions and B_frac:
        B_str = f"{B_frac[0]}/{B_frac[1]}"
    else:
        B_val = round_to_2_decimals(B)
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


def show_coefficient_procedure(digits, dv, use_fractions=True):
    """
    Genera el procedimiento paso a paso para el cálculo de coeficientes.
    
    Parámetros:
    - digits: tupla de 8 dígitos
    - dv: dígito verificador
    - use_fractions: si True muestra fracciones, si False muestra decimales
    
    Retorna string con el procedimiento detallado
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digits
    v = calculate_v(dv)
    
    # Calcular valores
    sum_d1_d2 = d1 + d2
    sum_d3_d4 = d3 + d4
    A_num, A_den = simplify_fraction(sum_d1_d2, v)
    B_num, B_den = simplify_fraction(sum_d3_d4, v)
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
        procedure += f"  Resultado: A = {round_to_2_decimals(A)}\n"
    
    # Procedimiento para B
    procedure += f"\nCoeficiente B:\n"
    procedure += f"  Formula: B = (d3 + d4) / v\n"
    procedure += f"  Sustitucion: B = ({d3} + {d4}) / {v}\n"
    procedure += f"  Suma: B = {sum_d3_d4} / {v}\n"
    if use_fractions:
        procedure += f"  Simplificacion: B = {B_num}/{B_den}\n"
    else:
        procedure += f"  Resultado: B = {round_to_2_decimals(B)}\n"
    
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


def calculate_coefficients(digits, dv):
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
    
    v = calculate_v(dv)
    
    # Calcular valores iniciales
    sum_d1_d2 = d1 + d2
    A_num, A_den = simplify_fraction(sum_d1_d2, v)
    A = sum_d1_d2 / v
    
    # Calcular B = (d_3 + d_4) / v
    sum_d3_d4 = d3 + d4
    B_num, B_den = simplify_fraction(sum_d3_d4, v)
    B = sum_d3_d4 / v
    
    # Calcular C = -(d_5 + d_6)
    C = -(d5 + d6)
    
    # Calcular D = -(d_7 + d_8)
    D = -(d7 + d8)
    
    # Calcular E = d_1 + d_3 + d_5 + d_7
    E = d1 + d3 + d5 + d7
    
    # Lista para registrar ajustes aplicados
    adjustments = []
    
    # AJUSTES PARA OBTENER DISTINTAS CÓNICAS
    
    # Ajuste 1: Si d8 es impar, reemplazar B por -B (hipérbolas)
    if d8 % 2 == 1:
        B = -B
        B_num = -B_num
        adjustments.append(f"Ajuste 1: d8 = {d8} es impar -> Se reemplaza B por -B (hiperbola)")
    
    # Ajuste 2: Si d1 = d2, imponer B = A (circunferencias)
    if d1 == d2:
        B = A
        B_num = A_num
        B_den = A_den
        adjustments.append(f"Ajuste 2: d1 = d2 = {d1} -> Se impone B = A (circunferencia)")
    
    # Ajuste 3: Si d5 + d6 es múltiplo de 3, generar parábola
    sum_d5_d6 = d5 + d6
    if sum_d5_d6 % 3 == 0:
        if d7 % 2 == 0:
            # d7 es par -> B = 0 (parábola de eje vertical)
            B = 0
            B_num = 0
            B_den = 1
            adjustments.append(f"Ajuste 3a: (d5 + d6) = {sum_d5_d6} es multiplo de 3 y d7 = {d7} es par -> B = 0 (parabola eje vertical)")
        else:
            # d7 es impar -> A = 0 (parábola de eje horizontal)
            A = 0
            A_num = 0
            A_den = 1
            adjustments.append(f"Ajuste 3b: (d5 + d6) = {sum_d5_d6} es multiplo de 3 y d7 = {d7} es impar -> A = 0 (parabola eje horizontal)")
    
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
        'equation_fraction': build_general_equation(A, B, C, D, E, A_frac=(A_num, A_den), B_frac=(B_num, B_den), use_fractions=True),
        'equation_decimal': build_general_equation(A, B, C, D, E, A_frac=(A_num, A_den), B_frac=(B_num, B_den), use_fractions=False)
    }
