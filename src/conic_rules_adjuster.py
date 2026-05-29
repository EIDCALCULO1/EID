"""
Módulo 3: Ajustador de Reglas de Cónicas

Este módulo implementa los ajustes secuenciales descritos en la pauta para
garantizar variedad en los tipos de cónicas generados a partir del RUT.

Ajustes aplicados (según pauta):
1. Si d8 es impar → B = -B (fuerza Hipérbola)
2. Si d1 = d2 → B = A (fuerza Circunferencia) 
3. Si (d5+d6) múltiplo de 3 → Parábola:
   - Si d7 es par → B = 0 (eje vertical)
   - Si d7 es impar → A = 0 (eje horizontal)

Estas reglas se aplican SECUENCIALMENTE, por lo que el orden es importante.
"""


def aplicar_reglas_conicas(A, B, A_frac, B_frac, digits):
    """
    Aplica las reglas de ajuste de cónicas según la pauta oficial.
    
    Los ajustes se aplican secuencialmente en el orden especificado,
    modificando los coeficientes A y B cuando corresponda.
    
    Parámetros:
    - A: coeficiente A (float)
    - B: coeficiente B (float)
    - A_frac: tupla (numerador, denominador) de A
    - B_frac: tupla (numerador, denominador) de B
    - digits: tupla de 8 dígitos (d1, d2, d3, d4, d5, d6, d7, d8)
    
    Retorna:
    - A_adjusted: coeficiente A después de ajustes
    - B_adjusted: coeficiente B después de ajustes
    - A_frac_adjusted: fracción de A ajustada
    - B_frac_adjusted: fracción de B ajustada
    - adjustments: lista de strings describiendo los ajustes aplicados
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digits
    
    A_adjusted = A
    B_adjusted = B
    A_frac_adjusted = A_frac
    B_frac_adjusted = B_frac
    
    adjustments = []
    
    # ============================================================
    # AJUSTE 1: Si d8 es impar, entonces B = -B (Hipérbola)
    # ============================================================
    if d8 % 2 == 1:
        B_adjusted = -B_adjusted
        B_frac_adjusted = (-B_frac_adjusted[0], B_frac_adjusted[1])
        adjustments.append(
            f"Ajuste 1: d8 = {d8} es impar → Se invierte B a {B_frac_adjusted[0]}/{B_frac_adjusted[1]} "
            f"(fuerza Hipérbola)"
        )
    
    # ============================================================
    # AJUSTE 2: Si d1 = d2, entonces B = A (Circunferencia)
    # ============================================================
    if d1 == d2:
        B_adjusted = A_adjusted
        B_frac_adjusted = A_frac_adjusted
        adjustments.append(
            f"Ajuste 2: d1 = d2 = {d1} → Se impone B = A = {A_frac_adjusted[0]}/{A_frac_adjusted[1]} "
            f"(fuerza Circunferencia)"
        )
    
    # ============================================================
    # AJUSTE 3: Si (d5+d6) es múltiplo de 3 → Parábola
    # ============================================================
    sum_d5_d6 = d5 + d6
    if sum_d5_d6 % 3 == 0:
        if d7 % 2 == 0:
            # d7 es par → B = 0 (Parábola eje vertical)
            B_adjusted = 0
            B_frac_adjusted = (0, 1)
            adjustments.append(
                f"Ajuste 3a: (d5+d6) = {sum_d5_d6} es múltiplo de 3 y d7 = {d7} es par → "
                f"B = 0 (Parábola eje vertical)"
            )
        else:
            # d7 es impar → A = 0 (Parábola eje horizontal)
            A_adjusted = 0
            A_frac_adjusted = (0, 1)
            adjustments.append(
                f"Ajuste 3b: (d5+d6) = {sum_d5_d6} es múltiplo de 3 y d7 = {d7} es impar → "
                f"A = 0 (Parábola eje horizontal)"
            )
    
    return A_adjusted, B_adjusted, A_frac_adjusted, B_frac_adjusted, adjustments


def obtener_reglas_ajuste_conicas():
    """
    Retorna una descripción legible de las reglas de ajuste de cónicas.
    
    Útil para mostrar en la interfaz o para documentación.
    """
    rules = """
REGLAS DE AJUSTE DE CÓNICAS (Aplicadas secuencialmente):

1. Si d8 es impar:
   → Se invierte el coeficiente B (B = -B)
   → Genera Hipérbola

2. Si d1 = d2:
   → Se igualan los coeficientes (B = A)
   → Genera Circunferencia

3. Si (d5 + d6) es múltiplo de 3:
   → Se genera una Parábola diferenciando su orientación:
      • Si d7 es par:   B = 0  (Eje vertical)
      • Si d7 es impar: A = 0  (Eje horizontal)

Nota: Estos ajustes se aplican en el orden especificado.
"""
    return rules
