"""
Script de testing para Módulos 1, 2, 3, 4 y 5
"""

from src.rut_validator import validate_rut, show_validation_procedure
from src.coefficient_engine import calculate_coefficients, show_coefficient_procedure
from src.conic_rules_adjuster import get_adjustment_rules
from src.conic_classifier import get_conic_classification_rules


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
            
            # Mostrar procedimiento paso a paso de validación
            print(f"\n{'='*70}")
            print("PROCEDIMIENTO PASO A PASO - ALGORITMO MÓDULO 11")
            print(f"{'='*70}")
            procedure = show_validation_procedure(rut)
            if procedure:
                print(procedure)
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
    
    # Mostrar reglas de ajuste de cónicas (Módulo 3)
    print(f"\n{'='*70}")
    print("MÓDULO 3: REGLAS DE AJUSTE DE CÓNICAS")
    print(f"{'='*70}")
    print(get_adjustment_rules())
    
    # Mostrar ajustes aplicados si hay
    if coeff['adjustments']:
        print(f"\n{'='*70}")
        print("AJUSTES APLICADOS")
        print(f"{'='*70}")
        for adjustment in coeff['adjustments']:
            print(f"  ✓ {adjustment}")
    
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
    
    # Mostrar explicación completa de construcción (Módulo 5)
    print(f"\n{'='*70}")
    print("MÓDULO 5: GENERADOR DE DESARROLLO TEXTUAL")
    print(f"{'='*70}")
    
    if use_fractions:
        print(coeff['explanation_fraction'])
    else:
        print(coeff['explanation_decimal'])
    
    # Mostrar comparación antes/después de ajustes si hay
    if coeff['adjustments']:
        print(coeff['adjusted_comparison'])
    
    # Mostrar reglas de clasificación de cónicas (Módulo 4)
    print(f"\n{'='*70}")
    print("MÓDULO 4: CLASIFICADOR GEOMÉTRICO")
    print(f"{'='*70}")
    print(get_conic_classification_rules())
    
    # Mostrar clasificación de la cónica
    print(f"{'='*70}")
    print("CLASIFICACIÓN DE LA CÓNICA")
    print(f"{'='*70}")
    conic_class = coeff['conic_classification']
    print(f"\nTipo de Cónica: {conic_class['type'].upper()}")
    print(f"\nJustificación:")
    print(conic_class['justification'])
    
    if conic_class['type'] == 'parábola':
        print(f"\n✓ Orientación: {conic_class.get('axis', 'No especificada')}")
    
    # ================================================================
    # MÓDULO 6: TRANSFORMACIÓN A FORMA CANÓNICA
    # ================================================================
    print("\n" + "="*70)
    print("MÓDULO 6: MOTOR DE TRANSFORMACIÓN CANÓNICA")
    print("="*70)
    
    canonical = coeff.get('canonical_transformation')
    if canonical and isinstance(canonical, dict) and 'procedure' in canonical:
        print(canonical['procedure'])
        
        # Mostrar resumen de parámetros canónicos
        print("PARÁMETROS CANÓNICOS EXTRAÍDOS:")
        if conic_class['type'] == 'circunferencia':
            print(f"  Centro: ({canonical['h']}, {canonical['k']})")
            print(f"  Radio: r = {canonical['r']}")
        
        elif conic_class['type'] == 'elipse':
            if canonical.get('status') == 'completed':
                print(f"  Centro: ({canonical['h']}, {canonical['k']})")
                print(f"  Semieje a (mayor): {canonical['a']}")
                print(f"  Semieje b (menor): {canonical['b']}")
        
        elif conic_class['type'] == 'hipérbola':
            if canonical.get('status') == 'completed':
                print(f"  Centro: ({canonical['h']}, {canonical['k']})")
                print(f"  Semieje a (transversal): {canonical['a']}")
                print(f"  Semieje b (conjugado): {canonical['b']}")
        
        elif conic_class['type'] == 'parábola':
            if canonical.get('status') == 'completed':
                print(f"  Vértice: ({canonical['h']}, {canonical['k']})")
                print(f"  Parámetro p: {canonical['p']}")
                print(f"  Eje de simetría: {canonical['axis'].upper()}")
    
    # Mostrar procedimiento inverso
    print(f"\n{'='*70}")
    print("PROCEDIMIENTO INVERSO: CANÓNICA → GENERAL")
    print(f"{'='*70}")
    inverse = coeff.get('inverse_transformation')
    if inverse:
        print(inverse)
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
