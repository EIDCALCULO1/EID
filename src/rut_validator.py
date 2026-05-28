"""
Módulo 1: Validador y Parser de RUT
Implementa el algoritmo Módulo 11 para validar RUTs chilenos.
"""

import re


def clean_rut(rut_input):
    """Limpia el RUT removiendo puntos, guiones y espacios."""
    return rut_input.replace(".", "").replace("-", "").replace(" ", "").upper()


def validate_format(rut_input):
    """
    Valida el formato del RUT.
    El formato correcto es: XX.XXX.XXX-X donde X son dígitos y el último puede ser K (mayúscula o minúscula).
    
    Retorna una tupla (es_valido, mensaje_error)
    """
    # Convertir a mayúsculas para la validación de patrón
    rut_upper = rut_input.upper()
    
    # Patrón: 1-2 dígitos, punto, 3 dígitos, punto, 3 dígitos, guión, 1 dígito o K
    pattern = r'^\d{1,2}\.\d{3}\.\d{3}-[0-9K]$'
    
    if not re.match(pattern, rut_upper):
        # Validaciones específicas y ordenadas (de más crítico a menos)
        
        # Verificar si contiene caracteres especiales no permitidos
        allowed_chars = set('0123456789./-Kk')
        if not all(c in allowed_chars for c in rut_input):
            # Verificar si contiene letras (excepto K)
            if re.search(r'[A-JL-Za-jl-z]', rut_input):
                return False, "Error de validación: Los RUT chilenos no permiten letras en los dígitos. Solo se permite la letra 'K' como dígito verificador."
            else:
                return False, "Error de validación: Contiene caracteres no permitidos. Solo use dígitos, puntos, guión y la letra K. Formato: XX.XXX.XXX-X"
        
        # Verificar si usa comas en lugar de puntos
        if ',' in rut_input:
            return False, "Error de validación: Use puntos (.) como separadores, no comas (,). Formato correcto: XX.XXX.XXX-X"
        
        # Verificar si usa espacios
        if ' ' in rut_input:
            return False, "Error de validación: No se permiten espacios. Use el formato: XX.XXX.XXX-X"
        
        # Verificar si falta el guión
        if '-' not in rut_input:
            return False, "Error de validación: Falta el guión (-) antes del dígito verificador. Formato correcto: XX.XXX.XXX-X"
        
        # Verificar si falta los puntos
        if rut_input.count('.') < 2:
            return False, "Error de validación: Faltan puntos (.) separadores. Deben existir dos puntos. Formato correcto: XX.XXX.XXX-X"
        
        # Verificar si tiene demasiados puntos o guiones
        if rut_input.count('.') > 2:
            return False, "Error de validación: Demasiados puntos (.). Use exactamente dos. Formato correcto: XX.XXX.XXX-X"
        
        if rut_input.count('-') > 1:
            return False, "Error de validación: Demasiados guiones (-). Use exactamente uno. Formato correcto: XX.XXX.XXX-X"
        
        # Error genérico de formato
        return False, "Error de validación: Formato incorrecto. Use el formato: XX.XXX.XXX-X"
    
    return True, None


def validate_rut(rut_input):
    """
    Valida un RUT chileno usando algoritmo Módulo 11.
    
    Retorna un diccionario con:
    - is_valid: bool
    - digits: tuple de 8 dígitos
    - dv: dígito verificador (str)
    - rut_clean: RUT sin caracteres especiales
    - error: mensaje de error si aplica
    """
    # Primero validar el formato
    format_valid, format_error = validate_format(rut_input)
    if not format_valid:
        return {
            'is_valid': False,
            'error': format_error
        }
    
    rut_clean = clean_rut(rut_input)
    
    # Validar que tenga exactamente 9 caracteres después de limpiar
    if len(rut_clean) != 9:
        return {
            'is_valid': False,
            'error': f'Error de validación: El RUT debe contener exactamente 9 caracteres, se recibieron {len(rut_clean)}.'
        }
    
    # Validar que primeros 8 sean dígitos
    if not rut_clean[:8].isdigit():
        return {
            'is_valid': False,
            'error': 'Error de validación: Los primeros 8 caracteres deben ser dígitos. No se permiten letras en la parte numérica del RUT.'
        }
    
    # Validar DV
    last_char = rut_clean[8]
    if not (last_char.isdigit() or last_char == 'K'):
        return {
            'is_valid': False,
            'error': f'Error de validación: El dígito verificador debe ser un dígito (0-9) o la letra K. Se recibió: {last_char}'
        }
    
    # Extraer dígitos
    digits = tuple(int(d) for d in rut_clean[:8])
    provided_dv = last_char
    
    # Calcular DV esperado usando Módulo 11
    # Los multiplicadores se aplican de DERECHA a IZQUIERDA
    multiplicadores = [2, 3, 4, 5, 6, 7, 2, 3]
    suma = 0
    
    for i, digit in enumerate(digits):
        # multiplicadores[7-i] aplica de derecha a izquierda
        suma += digit * multiplicadores[7 - i]
    
    remainder = suma % 11
    expected_dv_value = 11 - remainder
    
    if expected_dv_value == 11:
        expected_dv = '0'
    elif expected_dv_value == 10:
        expected_dv = 'K'
    else:
        expected_dv = str(expected_dv_value)
    
    # Comparar DVs
    if provided_dv != expected_dv:
        return {
            'is_valid': False,
            'error': f'Error de validación: Dígito verificador inválido. Según el algoritmo Módulo 11, el dígito verificador correcto es {expected_dv}, pero se recibió {provided_dv}.'
        }
    
    return {
        'is_valid': True,
        'rut_clean': rut_clean,
        'digits': digits,
        'dv': expected_dv
    }


def show_validation_procedure(rut_input):
    """
    Genera el procedimiento paso a paso del algoritmo Módulo 11 para validar un RUT.
    
    Parámetros:
    - rut_input: RUT ingresado por el usuario (con formato XX.XXX.XXX-X)
    
    Retorna: string con el procedimiento detallado o None si hay error de formato
    """
    # Validar formato primero
    format_valid, format_error = validate_format(rut_input)
    if not format_valid:
        return None
    
    rut_clean = clean_rut(rut_input)
    
    # Extraer dígitos y DV
    digits = tuple(int(d) for d in rut_clean[:8])
    provided_dv = rut_clean[8]
    
    # Multiplicadores del algoritmo Módulo 11 (de derecha a izquierda)
    multiplicadores = [2, 3, 4, 5, 6, 7, 2, 3]
    
    # Construir el procedimiento
    procedure = "\n"
    procedure += f"RUT ingresado: {rut_input}\n"
    procedure += f"RUT limpio: {rut_clean}\n\n"
    
    # Paso 1: Mostrar dígitos
    procedure += f"Paso 1: Extraer dígitos\n"
    procedure += f"  Dígitos del RUT: {' '.join(map(str, digits))}\n"
    procedure += f"  Dígito verificador proporcionado: {provided_dv}\n\n"
    
    # Paso 2: Mostrar multiplicadores
    procedure += f"Paso 2: Aplicar multiplicadores (de DERECHA a IZQUIERDA)\n"
    procedure += f"  Posición:      d₁ d₂ d₃ d₄ d₅ d₆ d₇ d₈\n"
    procedure += f"  Dígitos:       {' '.join(map(str, digits))}\n"
    procedure += f"  Multiplicador: {' '.join(map(str, multiplicadores[::-1]))}\n\n"
    
    # Paso 3: Calcular productos
    procedure += f"Paso 3: Calcular productos (dígito × multiplicador)\n"
    suma = 0
    for i, digit in enumerate(digits):
        mult = multiplicadores[7 - i]
        producto = digit * mult
        suma += producto
        procedure += f"  d{i+1} × mult: {digit} × {mult} = {producto}\n"
    
    procedure += f"\n"
    
    # Paso 4: Suma total
    procedure += f"Paso 4: Suma total de productos\n"
    procedure += f"  Suma: {suma}\n\n"
    
    # Paso 5: Aplicar módulo 11
    remainder = suma % 11
    procedure += f"Paso 5: Calcular resto al dividir por 11\n"
    procedure += f"  {suma} mod 11 = {remainder}\n\n"
    
    # Paso 6: Calcular DV esperado
    expected_dv_value = 11 - remainder
    procedure += f"Paso 6: Calcular dígito verificador esperado\n"
    procedure += f"  DV_esperado = 11 - {remainder} = {expected_dv_value}\n"
    
    if expected_dv_value == 11:
        expected_dv = '0'
        procedure += f"  Como el resultado es 11, se reemplaza por 0\n"
    elif expected_dv_value == 10:
        expected_dv = 'K'
        procedure += f"  Como el resultado es 10, se reemplaza por K\n"
    else:
        expected_dv = str(expected_dv_value)
    
    procedure += f"  DV esperado: {expected_dv}\n\n"
    
    # Paso 7: Validación final
    procedure += f"Paso 7: Comparación y validación\n"
    procedure += f"  DV esperado: {expected_dv}\n"
    procedure += f"  DV proporcionado: {provided_dv}\n"
    
    if provided_dv == expected_dv:
        procedure += f"  ✓ COINCIDEN - RUT VÁLIDO\n"
    else:
        procedure += f"  ✗ NO COINCIDEN - RUT INVÁLIDO\n"
    
    return procedure
