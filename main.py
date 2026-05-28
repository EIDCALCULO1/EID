"""
Script de testing para Módulos 1 y 2
"""

from src.rut_validator import validate_rut
from src.coefficient_engine import calculate_coefficients, show_coefficient_procedure


def main():
    print("\n" + "="*70)
    print("TESTING MÓDULO 1: VALIDADOR RUT")
    print("="*70)
    
    # Solicitar RUT al usuario con reintentos
    result = None
    while result is None:
        rut = input("\nIngrese el RUT a validar (formato: XX.XXX.XXX-X): ")
        print(f"\nRUT a validar: {rut}")
        
        result = validate_rut(rut)
        
        if result['is_valid']:
            print("[OK] RUT valido")
            print(f"  RUT limpio: {result['rut_clean']}")
            print(f"  Dígitos: {result['digits']}")
            print(f"  DV: {result['dv']}")
        else:
            print(f"[ERROR] RUT invalido: {result['error']}")
            result = None  # Permitir reintentar
    
    # Testing Module 2
    print("\n" + "="*70)
    print("TESTING MÓDULO 2: COEFICIENTES")
    print("="*70)
    
    # Preguntar formato de salida
    while True:
        formato = input("\n¿Desea ver los resultados en fracción (f) o decimales (d)? (f/d): ").lower().strip()
        if formato in ['f', 'd']:
            break
        print("Opción inválida. Ingrese 'f' para fracción o 'd' para decimales.")
    
    use_fractions = (formato == 'f')
    
    digits = result['digits']
    dv = result['dv']
    
    coeff = calculate_coefficients(digits, dv)
    
    print(f"\nVariable v: {coeff['v']}")
    
    # Mostrar ajustes aplicados si hay
    if coeff['adjustments']:
        print(f"\n{'='*70}")
        print("AJUSTES APLICADOS (para obtener distintas conicas)")
        print(f"{'='*70}")
        for adjustment in coeff['adjustments']:
            print(f"  * {adjustment}")
    
    # Mostrar procedimiento paso a paso
    print(f"\n{'='*70}")
    print("PROCEDIMIENTO PASO A PASO")
    print(f"{'='*70}")
    procedure = show_coefficient_procedure(digits, dv, use_fractions=use_fractions)
    print(procedure)
    
    # Mostrar resumen de coeficientes
    print(f"{'='*70}")
    print("RESUMEN DE COEFICIENTES")
    print(f"{'='*70}")
    print(f"\nCoeficientes calculados:")
    
    if use_fractions:
        print(f"  A = {coeff['A_frac'][0]}/{coeff['A_frac'][1]}")
        print(f"  B = {coeff['B_frac'][0]}/{coeff['B_frac'][1]}")
    else:
        from src.coefficient_engine import round_to_2_decimals
        print(f"  A = {round_to_2_decimals(coeff['A'])}")
        print(f"  B = {round_to_2_decimals(coeff['B'])}")
    
    print(f"  C = {coeff['C']}")
    print(f"  D = {coeff['D']}")
    print(f"  E = {coeff['E']}")
    
    print(f"\nEcuación General:")
    if use_fractions:
        print(f"  {coeff['equation_fraction']}")
    else:
        print(f"  {coeff['equation_decimal']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
