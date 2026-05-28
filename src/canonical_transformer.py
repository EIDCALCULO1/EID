"""
Módulo 6: Motor de Transformación Canónica (Ida y Vuelta)

Este módulo implementa la lógica manual para completar cuadrados y transformar
la ecuación general de segunda grado a su forma canónica, justificando cada
operación algebraica paso a paso.

También incluye el procedimiento inverso: de forma canónica a forma general.

Según la pauta:
"Debe implementar lógica manual para agrupar términos, factorizar y completar 
el cuadrado. Debe generar los strings del procedimiento algebraico paso a paso,
justificando cada operación. Debe incluir el procedimiento inverso."
"""


def complete_square_univariate(coeff_x2, coeff_x, constant):
    """
    Completa el cuadrado para términos de una variable: Ax² + Bx + C
    
    Retorna: (h, k, procedimiento)
    Donde: A(x - h)² + k es la forma completa
    
    Parámetros:
    - coeff_x2: coeficiente de x² (A)
    - coeff_x: coeficiente de x (B)
    - constant: término constante (C)
    
    Retorna: tupla (h, k, procedimiento_str)
    """
    if coeff_x2 == 0:
        return None, None, "No hay término de x² para completar cuadrado"
    
    proc = "\n"
    
    # Paso 1: Factorizar el coeficiente de x²
    proc += f"Expresión inicial: {coeff_x2}x² + {coeff_x}x + {constant}\n\n"
    
    # Paso 2: Factor común
    proc += f"Paso 1: Factorizar {coeff_x2} del primer y segundo término\n"
    proc += f"  {coeff_x2}(x² + {coeff_x/coeff_x2}x) + {constant}\n\n"
    
    # Paso 3: Calcular lo que falta dentro del paréntesis
    b_over_a = coeff_x / coeff_x2
    proc += f"Paso 2: Completar el cuadrado dentro del paréntesis\n"
    proc += f"  Coeficiente de x en el paréntesis: {b_over_a}\n"
    proc += f"  Mitad del coeficiente: {b_over_a / 2}\n"
    proc += f"  Cuadrado de la mitad: ({b_over_a / 2})² = {(b_over_a / 2) ** 2}\n\n"
    
    # Paso 4: Sumar y restar dentro del paréntesis
    half_b = b_over_a / 2
    sq_half_b = half_b ** 2
    
    proc += f"Paso 3: Sumar y restar {sq_half_b} dentro del paréntesis\n"
    proc += f"  {coeff_x2}(x² + {b_over_a}x + {sq_half_b} - {sq_half_b}) + {constant}\n\n"
    
    # Paso 5: Reagrupar
    proc += f"Paso 4: Reagrupar en trinomio cuadrado perfecto\n"
    proc += f"  {coeff_x2}((x + {half_b})² - {sq_half_b}) + {constant}\n\n"
    
    # Paso 6: Distribuir
    proc += f"Paso 5: Distribuir {coeff_x2}\n"
    proc += f"  {coeff_x2}(x + {half_b})² - {coeff_x2 * sq_half_b} + {constant}\n\n"
    
    # Paso 7: Simplificar constantes
    final_k = constant - coeff_x2 * sq_half_b
    proc += f"Paso 6: Simplificar constante\n"
    proc += f"  {coeff_x2}(x + {half_b})² + {final_k}\n\n"
    
    # h es el opuesto del término dentro del paréntesis
    h = -half_b
    k = final_k
    
    proc += f"FORMA COMPLETADA: {coeff_x2}(x - ({h}))² + {k}\n"
    proc += f"O equivalentemente: {coeff_x2}(x - {h})² + {k}\n"
    
    return h, k, proc


def transform_circle_to_canonical(A, C, D, E):
    """
    Transforma ecuación de circunferencia de forma general a canónica.
    
    General: Ax² + Ay² + Cx + Dy + E = 0
    Canónica: (x - h)² + (y - k)² = r²
    
    Retorna: diccionario con (h, k, r) y procedimiento
    """
    if A == 0:
        return None, "Coeficiente A es cero, no es circunferencia"
    
    proc = "\n" + "="*70 + "\n"
    proc += "TRANSFORMACIÓN: GENERAL → CANÓNICA (CIRCUNFERENCIA)\n"
    proc += "="*70 + "\n"
    
    proc += f"Forma General: {A}x² + {A}y² + {C}x + {D}y + {E} = 0\n\n"
    
    # Dividir todo por A
    proc += f"Paso 1: Dividir todo por {A}\n"
    proc += f"  x² + y² + {C/A}x + {D/A}y + {E/A} = 0\n\n"
    
    # Agrupar términos por variable
    proc += f"Paso 2: Agrupar términos por variable\n"
    proc += f"  (x² + {C/A}x) + (y² + {D/A}y) + {E/A} = 0\n\n"
    
    # Completar cuadrados
    h, k_x, proc_x = complete_square_univariate(1, C/A, 0)
    proc += f"Para x:\n{proc_x}\n"
    
    h_y, k_y, proc_y = complete_square_univariate(1, D/A, 0)
    proc += f"\nPara y:\n{proc_y}\n"
    
    # Calcular r²
    r_squared = -(E/A + k_x + k_y)
    r = r_squared ** 0.5 if r_squared >= 0 else None
    
    proc += f"Paso 3: Combinar y simplificar\n"
    proc += f"  (x - {h})² + (y - {h_y})² = {r_squared}\n\n"
    
    proc += f"FORMA CANÓNICA: (x - {h})² + (y - {h_y})² = {r_squared}\n"
    
    if r:
        proc += f"Centro: ({h}, {h_y})\n"
        proc += f"Radio: r = {r}\n"
    
    return {
        'h': h,
        'k': h_y,
        'r_squared': r_squared,
        'r': r,
        'procedure': proc
    }


def transform_conic_general_to_canonical(A, B, C, D, E, conic_type):
    """
    Transforma ecuación general a canónica según el tipo de cónica.
    
    Parámetros:
    - A, B, C, D, E: coeficientes de la ecuación general
    - conic_type: tipo de cónica ('circunferencia', 'elipse', 'hipérbola', 'parábola')
    
    Retorna: diccionario con parámetros canónicos y procedimiento completo
    """
    
    if conic_type == 'circunferencia':
        return transform_circle_to_canonical(A, C, D, E)
    
    elif conic_type == 'elipse':
        return transform_elipse_to_canonical(A, B, C, D, E)
    
    elif conic_type == 'hipérbola':
        return transform_hyperbola_to_canonical(A, B, C, D, E)
    
    elif conic_type == 'parábola':
        return transform_parabola_to_canonical(A, B, C, D, E)
    
    else:
        return None, f"Tipo de cónica no reconocido: {conic_type}"


def transform_elipse_to_canonical(A, B, C, D, E):
    """
    Transforma ecuación de elipse de forma general a canónica.
    
    General: Ax² + By² + Cx + Dy + E = 0 (A, B mismo signo)
    Canónica: (x-h)²/a² + (y-k)²/b² = 1
    """
    
    if A == 0 or B == 0:
        return None, "Coeficientes A o B son cero, no es elipse"
    
    proc = "\n" + "="*70 + "\n"
    proc += "TRANSFORMACIÓN: GENERAL → CANÓNICA (ELIPSE)\n"
    proc += "="*70 + "\n\n"
    
    proc += f"Forma General: {A}x² + {B}y² + {C}x + {D}y + {E} = 0\n\n"
    
    proc += f"Paso 1: Agrupar términos por variable\n"
    proc += f"  ({A}x² + {C}x) + ({B}y² + {D}y) + {E} = 0\n\n"
    
    # Completar cuadrado para x
    h_x, k_x, proc_x = complete_square_univariate(A, C, 0)
    proc += f"Completar cuadrado para x:\n{proc_x}\n"
    
    # Completar cuadrado para y
    h_y, k_y, proc_y = complete_square_univariate(B, D, 0)
    proc += f"Completar cuadrado para y:\n{proc_y}\n"
    
    # Construir la ecuación completada
    proc += f"Paso 2: Combinar términos completados\n"
    proc += f"  {A}(x - {h_x})² + {k_x} + {B}(y - {h_y})² + {k_y} + {E} = 0\n\n"
    
    # Simplificar constante
    const_sum = k_x + k_y + E
    proc += f"Paso 3: Simplificar términos constantes\n"
    proc += f"  {A}(x - {h_x})² + {B}(y - {h_y})² + {const_sum} = 0\n"
    proc += f"  {A}(x - {h_x})² + {B}(y - {h_y})² = {-const_sum}\n\n"
    
    # Dividir por la constante del lado derecho
    rhs = -const_sum
    if rhs == 0:
        proc += f"Nota: Ecuación degenerada (un punto o conjunto vacío)\n"
        return {
            'procedure': proc,
            'type': 'elipse',
            'h': h_x,
            'k': h_y,
            'status': 'degenerada'
        }
    
    proc += f"Paso 4: Dividir ambos lados por {rhs} para obtener forma estándar\n"
    proc += f"  (x - {h_x})²/{rhs/A} + (y - {h_y})²/{rhs/B} = 1\n\n"
    
    a_squared = rhs / A
    b_squared = rhs / B
    
    # Calcular a y b
    import math
    a = math.sqrt(abs(a_squared)) if a_squared > 0 else None
    b = math.sqrt(abs(b_squared)) if b_squared > 0 else None
    
    if a and b:
        proc += f"FORMA CANÓNICA: (x - {h_x})²/{a_squared} + (y - {h_y})²/{b_squared} = 1\n"
        proc += f"Centro: ({h_x}, {h_y})\n"
        proc += f"Semieje mayor: a = {a}\n"
        proc += f"Semieje menor: b = {b}\n"
    
    return {
        'procedure': proc,
        'type': 'elipse',
        'h': h_x,
        'k': h_y,
        'a_squared': a_squared,
        'b_squared': b_squared,
        'a': a,
        'b': b,
        'status': 'completed'
    }


def transform_hyperbola_to_canonical(A, B, C, D, E):
    """
    Transforma ecuación de hipérbola de forma general a canónica.
    
    General: Ax² - By² + Cx + Dy + E = 0 (A, B signos opuestos)
    Canónica: (x-h)²/a² - (y-k)²/b² = 1
    """
    
    if A == 0 or B == 0:
        return None, "Coeficientes A o B son cero, no es hipérbola"
    
    proc = "\n" + "="*70 + "\n"
    proc += "TRANSFORMACIÓN: GENERAL → CANÓNICA (HIPÉRBOLA)\n"
    proc += "="*70 + "\n\n"
    
    proc += f"Forma General: {A}x² + {B}y² + {C}x + {D}y + {E} = 0\n"
    proc += f"(Nótese que A y B tienen signos opuestos)\n\n"
    
    proc += f"Paso 1: Agrupar términos por variable\n"
    proc += f"  ({A}x² + {C}x) + ({B}y² + {D}y) + {E} = 0\n\n"
    
    # Completar cuadrado para x
    h_x, k_x, proc_x = complete_square_univariate(A, C, 0)
    proc += f"Completar cuadrado para x:\n{proc_x}\n"
    
    # Completar cuadrado para y (considerando que B es negativo)
    h_y, k_y, proc_y = complete_square_univariate(B, D, 0)
    proc += f"Completar cuadrado para y:\n{proc_y}\n"
    
    # Construir la ecuación completada
    proc += f"Paso 2: Combinar términos completados\n"
    proc += f"  {A}(x - {h_x})² + {k_x} + {B}(y - {h_y})² + {k_y} + {E} = 0\n\n"
    
    # Simplificar constante
    const_sum = k_x + k_y + E
    proc += f"Paso 3: Simplificar términos constantes\n"
    proc += f"  {A}(x - {h_x})² + {B}(y - {h_y})² + {const_sum} = 0\n"
    proc += f"  {A}(x - {h_x})² + {B}(y - {h_y})² = {-const_sum}\n\n"
    
    # Dividir por la constante del lado derecho
    rhs = -const_sum
    if rhs == 0:
        proc += f"Nota: Ecuación degenerada (par de rectas o conjunto vacío)\n"
        return {
            'procedure': proc,
            'type': 'hipérbola',
            'h': h_x,
            'k': h_y,
            'status': 'degenerada'
        }
    
    proc += f"Paso 4: Dividir ambos lados por {rhs} para obtener forma estándar\n"
    proc += f"  (x - {h_x})²/{rhs/A} + (y - {h_y})²/{rhs/B} = 1\n\n"
    
    a_squared = rhs / A
    b_squared = rhs / B
    
    # Calcular a y b
    import math
    a = math.sqrt(abs(a_squared)) if a_squared > 0 else None
    b = math.sqrt(abs(b_squared)) if b_squared < 0 else None
    
    if a and b:
        proc += f"FORMA CANÓNICA: (x - {h_x})²/{a_squared} - (y - {h_y})²/{-b_squared} = 1\n"
        proc += f"Centro: ({h_x}, {h_y})\n"
        proc += f"Eje transversal (eje x): a = {a}\n"
        proc += f"Eje conjugado (eje y): b = {b}\n"
    
    return {
        'procedure': proc,
        'type': 'hipérbola',
        'h': h_x,
        'k': h_y,
        'a_squared': a_squared,
        'b_squared': b_squared,
        'a': a,
        'b': b,
        'status': 'completed'
    }


def transform_parabola_to_canonical(A, B, C, D, E):
    """
    Transforma ecuación de parábola de forma general a canónica.
    
    General: Ax² + Cx + Dy + E = 0 (B = 0, eje vertical)
    O: By² + Cx + Dy + E = 0 (A = 0, eje horizontal)
    
    Canónicas:
    - Eje vertical: (x - h)² = 4p(y - k)
    - Eje horizontal: (y - k)² = 4p(x - h)
    """
    
    proc = "\n" + "="*70 + "\n"
    proc += "TRANSFORMACIÓN: GENERAL → CANÓNICA (PARÁBOLA)\n"
    proc += "="*70 + "\n\n"
    
    if A != 0:  # Eje vertical: Ax² + Cx + Dy + E = 0
        proc += f"Forma General: {A}x² + {C}x + {D}y + {E} = 0\n"
        proc += f"Parábola de EJE VERTICAL (B = 0)\n\n"
        
        proc += f"Paso 1: Aislar términos con y\n"
        proc += f"  {D}y = -{A}x² - {C}x - {E}\n\n"
        
        proc += f"Paso 2: Completar cuadrado para x\n"
        h_x, k_x, proc_x = complete_square_univariate(A, C, 0)
        proc += proc_x
        
        proc += f"\nPaso 3: Sustituir en ecuación\n"
        proc += f"  {D}y = -{A}(x - {h_x})² - {k_x} - {E}\n"
        proc += f"  {D}y = -{A}(x - {h_x})² + {-k_x - E}\n\n"
        
        proc += f"Paso 4: Despejar y\n"
        coeff_factor = -A / D
        const_factor = (-k_x - E) / D
        proc += f"  y = {coeff_factor}(x - {h_x})² + {const_factor}\n"
        proc += f"  y - {const_factor} = {coeff_factor}(x - {h_x})²\n\n"
        
        # Forma canónica: (x - h)² = 4p(y - k)
        # Tenemos: (x - h)² = (1/coeff_factor) * (y - const_factor)
        p = 1 / (4 * coeff_factor)
        k_final = const_factor
        
        proc += f"FORMA CANÓNICA: (x - {h_x})² = {4*p}(y - {k_final})\n"
        proc += f"Centro del vértice: ({h_x}, {k_final})\n"
        proc += f"Parámetro p: {p}\n"
        
        if p > 0:
            proc += f"Parábola abre hacia ARRIBA\n"
        else:
            proc += f"Parábola abre hacia ABAJO\n"
        
        return {
            'procedure': proc,
            'type': 'parábola',
            'axis': 'vertical',
            'h': h_x,
            'k': k_final,
            'p': p,
            'status': 'completed'
        }
    
    else:  # Eje horizontal: By² + Cx + Dy + E = 0
        proc += f"Forma General: {B}y² + {C}x + {D}y + {E} = 0\n"
        proc += f"Parábola de EJE HORIZONTAL (A = 0)\n\n"
        
        proc += f"Paso 1: Aislar términos con x\n"
        proc += f"  {C}x = -{B}y² - {D}y - {E}\n\n"
        
        proc += f"Paso 2: Completar cuadrado para y\n"
        h_y, k_y, proc_y = complete_square_univariate(B, D, 0)
        proc += proc_y
        
        proc += f"\nPaso 3: Sustituir en ecuación\n"
        proc += f"  {C}x = -{B}(y - {h_y})² - {k_y} - {E}\n"
        proc += f"  {C}x = -{B}(y - {h_y})² + {-k_y - E}\n\n"
        
        proc += f"Paso 4: Despejar x\n"
        coeff_factor = -B / C
        const_factor = (-k_y - E) / C
        proc += f"  x = {coeff_factor}(y - {h_y})² + {const_factor}\n"
        proc += f"  x - {const_factor} = {coeff_factor}(y - {h_y})²\n\n"
        
        # Forma canónica: (y - k)² = 4p(x - h)
        p = 1 / (4 * coeff_factor)
        h_final = const_factor
        
        proc += f"FORMA CANÓNICA: (y - {h_y})² = {4*p}(x - {h_final})\n"
        proc += f"Centro del vértice: ({h_final}, {h_y})\n"
        proc += f"Parámetro p: {p}\n"
        
        if p > 0:
            proc += f"Parábola abre hacia DERECHA\n"
        else:
            proc += f"Parábola abre hacia IZQUIERDA\n"
        
        return {
            'procedure': proc,
            'type': 'parábola',
            'axis': 'horizontal',
            'h': h_final,
            'k': h_y,
            'p': p,
            'status': 'completed'
        }


def inverse_transformation_summary(A, B, C, D, E, conic_type):
    """
    Genera resumen del procedimiento inverso: Canónica → General
    
    Parámetros:
    - A, B, C, D, E: coeficientes finales de forma general
    - conic_type: tipo de cónica
    
    Retorna: string con explicación del procedimiento inverso
    """
    
    proc = "\n" + "="*70 + "\n"
    proc += "PROCEDIMIENTO INVERSO: CANÓNICA → GENERAL\n"
    proc += "="*70 + "\n\n"
    
    if conic_type == 'circunferencia':
        proc += "De forma canónica (x - h)² + (y - k)² = r²\n"
        proc += "Para volver a forma general:\n\n"
        proc += "Paso 1: Expandir binomios cuadrados\n"
        proc += "  (x - h)² = x² - 2hx + h²\n"
        proc += "  (y - k)² = y² - 2ky + k²\n\n"
        proc += "Paso 2: Sustituir\n"
        proc += "  x² - 2hx + h² + y² - 2ky + k² = r²\n\n"
        proc += "Paso 3: Reagrupar\n"
        proc += "  x² + y² - 2hx - 2ky + (h² + k² - r²) = 0\n\n"
        proc += f"Comparando con Ax² + Ay² + Cx + Dy + E = 0:\n"
        proc += f"  A = 1, C = -2h, D = -2k, E = h² + k² - r²\n"
    
    elif conic_type == 'elipse':
        proc += "De forma canónica (x-h)²/a² + (y-k)²/b² = 1\n"
        proc += "Para volver a forma general:\n\n"
        proc += "Paso 1: Multiplicar ambos lados por a²b²\n"
        proc += "  b²(x-h)² + a²(y-k)² = a²b²\n\n"
        proc += "Paso 2: Expandir binomios\n"
        proc += "  b²(x² - 2hx + h²) + a²(y² - 2ky + k²) = a²b²\n\n"
        proc += "Paso 3: Distribuir\n"
        proc += "  b²x² - 2b²hx + b²h² + a²y² - 2a²ky + a²k² = a²b²\n\n"
        proc += "Paso 4: Reagrupar en forma general\n"
        proc += "  b²x² + a²y² - 2b²hx - 2a²ky + (b²h² + a²k² - a²b²) = 0\n"
    
    elif conic_type == 'hipérbola':
        proc += "De forma canónica (x-h)²/a² - (y-k)²/b² = 1\n"
        proc += "Para volver a forma general: [PROCEDIMIENTO SIMILAR]\n\n"
        proc += "b²(x-h)² - a²(y-k)² = a²b²\n"
        proc += "→ Distribución y expansión similar a elipse\n"
    
    elif conic_type == 'parábola':
        proc += "De forma canónica (y-k)² = 4p(x-h) [eje vertical]\n"
        proc += "Para volver a forma general:\n\n"
        proc += "Paso 1: Expandir\n"
        proc += "  y² - 2ky + k² = 4px - 4ph\n\n"
        proc += "Paso 2: Reagrupar\n"
        proc += "  4px - y² + 2ky - 4ph - k² = 0\n"
    
    proc += "\n" + "="*70 + "\n"
    return proc
