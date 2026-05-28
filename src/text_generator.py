"""
Módulo 5: Generador de Desarrollo Textual (General)

Este módulo genera strings formateados que muestran exactamente cómo se
reemplazaron los dígitos del RUT en las fórmulas para llegar a la ecuación
general de segundo grado.

Según la pauta:
"Debe generar strings formateados que muestren al usuario exactamente cómo se
reemplazaron los dígitos del RUT en las fórmulas para llegar a la ecuación
general."
"""


def generate_equation_construction_explanation(digits, dv, A, B, C, D, E, 
                                               A_frac, B_frac, v, adjustments,
                                               conic_type, use_fractions=True):
    """
    Genera una explicación completa y detallada de cómo se construyó la ecuación
    general a partir del RUT, mostrando cada reemplazo de dígito en las fórmulas.
    
    Parámetros:
    - digits: tupla de 8 dígitos (d1, d2, ..., d8)
    - dv: dígito verificador (str)
    - A, B, C, D, E: coeficientes finales
    - A_frac, B_frac: fracciones de A y B
    - v: variable auxiliar
    - adjustments: lista de ajustes aplicados
    - conic_type: tipo de cónica clasificada
    - use_fractions: si True muestra fracciones, si False decimales
    
    Retorna: string con la explicación completa
    """
    d1, d2, d3, d4, d5, d6, d7, d8 = digits
    
    explanation = "\n"
    explanation += "="*70 + "\n"
    explanation += "EXPLICACIÓN COMPLETA: CONSTRUCCIÓN DE LA ECUACIÓN GENERAL\n"
    explanation += "="*70 + "\n\n"
    
    # =====================================================================
    # PASO 1: INTRODUCCIÓN Y DATOS DEL RUT
    # =====================================================================
    explanation += "PASO 1: EXTRACCIÓN DE DÍGITOS DEL RUT\n"
    explanation += "-" * 70 + "\n\n"
    explanation += f"RUTs chileno validado:\n"
    explanation += f"  Dígitos: d₁={d1}, d₂={d2}, d₃={d3}, d₄={d4}, d₅={d5}, d₆={d6}, d₇={d7}, d₈={d8}\n"
    explanation += f"  Dígito Verificador (DV): {dv}\n\n"
    
    # =====================================================================
    # PASO 2: CÁLCULO DE LA VARIABLE v
    # =====================================================================
    explanation += "PASO 2: CÁLCULO DE VARIABLE AUXILIAR 'v'\n"
    explanation += "-" * 70 + "\n\n"
    explanation += "Regla para calcular v:\n"
    explanation += "  • Si DV = 'K' → v = 10\n"
    explanation += "  • Si DV = '0' → v = 11\n"
    explanation += "  • Si DV es dígito (1-9) → v = DV\n\n"
    explanation += f"En este caso:\n"
    explanation += f"  DV = {dv}\n"
    
    if dv == 'K':
        explanation += f"  → v = 10 (porque DV = 'K')\n"
    elif dv == '0':
        explanation += f"  → v = 11 (porque DV = '0')\n"
    else:
        explanation += f"  → v = {int(dv)} (porque DV es un dígito)\n"
    
    explanation += f"\n  Valor de v utilizado: {v}\n\n"
    
    # =====================================================================
    # PASO 3: CÁLCULO DE COEFICIENTES (ANTES DE AJUSTES)
    # =====================================================================
    explanation += "PASO 3: CÁLCULO DE COEFICIENTES INICIALES\n"
    explanation += "-" * 70 + "\n\n"
    explanation += "Fórmulas a aplicar:\n"
    explanation += "  A = (d₁ + d₂) / v\n"
    explanation += "  B = (d₃ + d₄) / v\n"
    explanation += "  C = -(d₅ + d₆)\n"
    explanation += "  D = -(d₇ + d₈)\n"
    explanation += "  E = d₁ + d₃ + d₅ + d₇\n\n"
    
    # Coeficiente A
    explanation += "Cálculo de A:\n"
    explanation += f"  A = (d₁ + d₂) / v\n"
    explanation += f"  A = ({d1} + {d2}) / {v}\n"
    explanation += f"  A = {d1 + d2} / {v}\n"
    if use_fractions:
        explanation += f"  A = {A_frac[0]}/{A_frac[1]} (fracción simplificada)\n"
    explanation += f"  A ≈ {A}\n\n"
    
    # Coeficiente B
    explanation += "Cálculo de B:\n"
    explanation += f"  B = (d₃ + d₄) / v\n"
    explanation += f"  B = ({d3} + {d4}) / {v}\n"
    explanation += f"  B = {d3 + d4} / {v}\n"
    if use_fractions:
        explanation += f"  B = {B_frac[0]}/{B_frac[1]} (fracción simplificada)\n"
    explanation += f"  B ≈ {B}\n\n"
    
    # Coeficiente C
    explanation += "Cálculo de C:\n"
    explanation += f"  C = -(d₅ + d₆)\n"
    explanation += f"  C = -({d5} + {d6})\n"
    explanation += f"  C = -{d5 + d6}\n"
    explanation += f"  C = {C}\n\n"
    
    # Coeficiente D
    explanation += "Cálculo de D:\n"
    explanation += f"  D = -(d₇ + d₈)\n"
    explanation += f"  D = -({d7} + {d8})\n"
    explanation += f"  D = -{d7 + d8}\n"
    explanation += f"  D = {D}\n\n"
    
    # Coeficiente E
    explanation += "Cálculo de E:\n"
    explanation += f"  E = d₁ + d₃ + d₅ + d₇\n"
    explanation += f"  E = {d1} + {d3} + {d5} + {d7}\n"
    explanation += f"  E = {E}\n\n"
    
    # =====================================================================
    # PASO 4: RESUMEN ANTES DE AJUSTES
    # =====================================================================
    explanation += "Coeficientes calculados (antes de ajustes):\n"
    if use_fractions:
        explanation += f"  A = {A_frac[0]}/{A_frac[1]}\n"
        explanation += f"  B = {B_frac[0]}/{B_frac[1]}\n"
    else:
        explanation += f"  A ≈ {A}\n"
        explanation += f"  B ≈ {B}\n"
    explanation += f"  C = {C}\n"
    explanation += f"  D = {D}\n"
    explanation += f"  E = {E}\n\n"
    
    # =====================================================================
    # PASO 5: AJUSTES APLICADOS (si hay)
    # =====================================================================
    if adjustments:
        explanation += "PASO 4: AJUSTES DE CÓNICAS APLICADOS\n"
        explanation += "-" * 70 + "\n\n"
        for idx, adj in enumerate(adjustments, 1):
            explanation += f"Ajuste {idx}:\n  {adj}\n\n"
    
    # =====================================================================
    # PASO 6: ECUACIÓN GENERAL FINAL
    # =====================================================================
    step_num = 5 if adjustments else 4
    explanation += f"PASO {step_num}: ECUACIÓN GENERAL FINAL\n"
    explanation += "-" * 70 + "\n\n"
    explanation += "Forma general: Ax² + By² + Cx + Dy + E = 0\n\n"
    
    if use_fractions:
        explanation += f"({A_frac[0]}/{A_frac[1]})x² + ({B_frac[0]}/{B_frac[1]})y² + ({C})x + ({D})y + ({E}) = 0\n\n"
    else:
        explanation += f"{A}x² + {B}y² + {C}x + {D}y + {E} = 0\n\n"
    
    # =====================================================================
    # PASO 7: CLASIFICACIÓN Y RESUMEN
    # =====================================================================
    step_num += 1
    explanation += f"PASO {step_num}: CLASIFICACIÓN DE LA CÓNICA\n"
    explanation += "-" * 70 + "\n\n"
    explanation += f"Tipo de cónica: {conic_type.upper()}\n\n"
    
    if conic_type == "circunferencia":
        explanation += "Justificación: A = B (ambos ≠ 0)\n"
        explanation += f"  Verificación: A = {A}, B = {B} → A = B ✓\n"
    elif conic_type == "elipse":
        explanation += "Justificación: A y B tienen el mismo signo y A ≠ B\n"
        sign_a = "positivo" if A > 0 else "negativo"
        sign_b = "positivo" if B > 0 else "negativo"
        explanation += f"  A = {A} ({sign_a})\n"
        explanation += f"  B = {B} ({sign_b})\n"
        explanation += f"  Mismo signo: Sí ✓\n"
        explanation += f"  A ≠ B: Sí ✓\n"
    elif conic_type == "hipérbola":
        explanation += "Justificación: A y B tienen signos opuestos\n"
        sign_a = "positivo" if A > 0 else "negativo"
        sign_b = "positivo" if B > 0 else "negativo"
        explanation += f"  A = {A} ({sign_a})\n"
        explanation += f"  B = {B} ({sign_b})\n"
        explanation += f"  Signos opuestos: Sí ✓\n"
    elif conic_type == "parábola":
        explanation += "Justificación: Exactamente uno de {A, B} es cero\n"
        if A == 0:
            explanation += f"  A = 0 ✓\n"
            explanation += f"  B = {B} ≠ 0 ✓\n"
            explanation += f"  Orientación: Eje horizontal (eje X)\n"
        else:
            explanation += f"  A = {A} ≠ 0 ✓\n"
            explanation += f"  B = 0 ✓\n"
            explanation += f"  Orientación: Eje vertical (eje Y)\n"
    
    explanation += "\n" + "="*70 + "\n"
    
    return explanation


def generate_adjusted_equation_comparison(A_before, B_before, A_after, B_after, 
                                          adjustments):
    """
    Genera una comparación visual de los coeficientes antes y después de ajustes.
    
    Parámetros:
    - A_before, B_before: coeficientes antes de ajustes
    - A_after, B_after: coeficientes después de ajustes
    - adjustments: lista de ajustes aplicados
    
    Retorna: string con la comparación formateada
    """
    if not adjustments:
        return ""
    
    comparison = "\n"
    comparison += "="*70 + "\n"
    comparison += "COMPARACIÓN: COEFICIENTES ANTES Y DESPUÉS DE AJUSTES\n"
    comparison += "="*70 + "\n\n"
    
    comparison += "┌─────────────────────────────────────────────────────────────────┐\n"
    comparison += "│ ANTES DE AJUSTES                  │ DESPUÉS DE AJUSTES          │\n"
    comparison += "├──────────────────────────────────┼────────────────────────────┤\n"
    comparison += f"│ A = {str(A_before):30} │ A = {str(A_after):24} │\n"
    comparison += f"│ B = {str(B_before):30} │ B = {str(B_after):24} │\n"
    comparison += "└──────────────────────────────────┴────────────────────────────┘\n\n"
    
    comparison += "Ajustes aplicados:\n"
    for idx, adj in enumerate(adjustments, 1):
        comparison += f"  {idx}. {adj}\n"
    
    comparison += "\n" + "="*70 + "\n"
    
    return comparison
