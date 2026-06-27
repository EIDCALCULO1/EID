"""
Módulo 9: Analizador de Funciones por Partes con Discontinuidades

Genera y analiza funciones por partes con 3 tipos de discontinuidades:
1. Removible: (x-a)(x+d1)/(x-a) - factor común que se cancela
2. De salto: dos ramas lineales con salto discontinuo
3. Infinita: x/(x-a) - asíntota vertical

La selección del caso se determina por: d8 % 3
- d8 % 3 == 0 → Caso 1 (Discontinuidad Removible)
- d8 % 3 == 1 → Caso 2 (Discontinuidad de Salto)
- d8 % 3 == 2 → Caso 3 (Discontinuidad Infinita)
"""

from typing import Dict, Any, List, Tuple
from fractions import Fraction


class AnalizadorFuncionesPorPartes:
    """Analizador de funciones por partes con análisis de discontinuidades."""

    def __init__(self, digits: List[int], dv: int) -> None:
        """
        Inicializa el analizador.
        
        Parámetros:
        - digits: lista de 8 dígitos del RUT
        - dv: dígito verificador (como número: K→10, 0→11, 1-9→su valor)
        """
        self.digits = digits
        self.dv = dv
        self.d8 = digits[7]
        self.case = self.d8 % 3  # 0, 1, 2
        self.discontinuity_point = None
        self.function_definition = None
        self.analysis = {}

    def generate_function(self) -> Dict[str, Any]:
        """
        Genera la función por partes según el caso asignado.
        
        Retorna un diccionario con:
        - case: tipo de discontinuidad (0/1/2)
        - case_name: nombre descriptivo
        - discontinuity_point: punto de discontinuidad
        - function_definition: definición matemática de la función
        - procedure: procedimiento paso a paso
        - analysis: análisis de límites y continuidad
        """

        if self.case == 0:
            return self._generate_removable()
        elif self.case == 1:
            return self._generate_jump()
        else:  # case == 2
            return self._generate_infinite()

    def _generate_removable(self) -> Dict[str, Any]:
        """Genera función con discontinuidad removible."""
        # Discontinuidad removible: (x-a)(x+d1)/(x-a) = x+d1 (excepto en x=a)
        # Punto de discontinuidad: x = d1
        a = self.digits[0]  # d1
        self.discontinuity_point = a

        procedure = (
            f"CASO 1: DISCONTINUIDAD REMOVIBLE\n"
            f"{'='*70}\n\n"
            f"Ecuación Base:\n"
            f"  f(x) = (x - {a})(x + {a}) / (x - {a})\n\n"
            f"Paso 1: Factorización\n"
            f"  El numerador tiene factor común (x - {a}) con el denominador\n\n"
            f"Paso 2: Cancelación de términos\n"
            f"  f(x) = (x - {a})(x + {a}) / (x - {a})\n"
            f"  f(x) = x + {a}  ,  x ≠ {a}\n\n"
            f"Paso 3: Punto de discontinuidad\n"
            f"  Punto de ruptura: x = {a}\n"
            f"  Tipo: Discontinuidad removible (agujero)\n\n"
            f"Paso 4: Límites laterales\n"
            f"  lim(x→{a}⁻) f(x) = {a} + {a} = {2*a}\n"
            f"  lim(x→{a}⁺) f(x) = {a} + {a} = {2*a}\n\n"
            f"Paso 5: Análisis de continuidad\n"
            f"  La función tiende a {2*a} cuando x → {a}\n"
            f"  PERO f({a}) no está definida (función indefinida en x = {a})\n"
            f"  La discontinuidad PUEDE removerse redefiniendo f({a}) = {2*a}\n"
        )

        analysis = self._analyze_removable(a)

        return {
            'case': 0,
            'case_name': 'Discontinuidad Removible',
            'discontinuity_point': a,
            'function_definition': f"f(x) = (x - {a})(x + {a}) / (x - {a})  ,  x ≠ {a}",
            'simplified_form': f"f(x) = x + {a}  (excepto en x = {a})",
            'point_of_discontinuity': f"x = {a}",
            'procedure': procedure,
            'analysis': analysis,
            'table': self._generate_values_table_removable(a)
        }

    def _analyze_removable(self, a: int) -> Dict[str, Any]:
        """Análisis detallado para discontinuidad removible."""
        left_limit = 2 * a
        right_limit = 2 * a
        value_at_point = "indefinida"

        return {
            'discontinuity_type': 'Removible (Agujero)',
            'discontinuity_definition': (
                f"Existe un agujero en el punto ({a}, {left_limit}) porque "
                f"el factor (x - {a}) se cancela en numerador y denominador."
            ),
            'left_limit': left_limit,
            'right_limit': right_limit,
            'limits_equal': True,
            'value_at_discontinuity': value_at_point,
            'is_continuous': False,
            'reason': (
                f"Aunque lim(x→{a}) f(x) = {left_limit}, la función no está definida "
                f"en x = {a}, por lo que hay discontinuidad removible."
            ),
            'removal_method': f"Redefinir f({a}) = {left_limit} eliminaría la discontinuidad."
        }

    def _generate_values_table_removable(self, a: int) -> str:
        """Genera tabla de valores para función removible."""
        table = f"\nTABLA DE VALORES - f(x) = x + {a}  (excepto en x = {a}):\n"
        table += f"{'x':<8} | {'f(x)':<12}\n"
        table += f"{'-'*28}\n"

        # Valores antes del punto
        for x in range(a - 3, a):
            fx = x + a
            table += f"{x:<8} | {fx:<12}\n"

        # El punto de discontinuidad
        table += f"{a:<8} | {'INDEFINIDA':<12}\n"

        # Valores después del punto
        for x in range(a + 1, a + 4):
            fx = x + a
            table += f"{x:<8} | {fx:<12}\n"

        return table

    def _generate_jump(self) -> Dict[str, Any]:
        """Genera función con continuidad o salto finito según los parámetros."""
        # Función por partes con dos ramas lineales
        # f(x) = { x + d2   si x < d3
        #        { x + d4   si x ≥ d3
        d2, d3, d4 = self.digits[1], self.digits[2], self.digits[3]
        a = d3
        self.discontinuity_point = a

        # Calcular límites laterales y valor en el punto
        left_limit = a + d2
        right_limit = a + d4
        f_at_point = a + d4
        is_continuous = left_limit == right_limit and f_at_point == right_limit
        salto = abs(right_limit - left_limit)

        if is_continuous:
            case_name = 'Función Continua'
            conclusion = (
                f"  No hay salto en x = {a}: los límites laterales coinciden y "
                f"f({a}) = {f_at_point}.\n"
                f"  La función es CONTINUA en x = {a}."
            )
        else:
            case_name = 'Discontinuidad de Salto'
            conclusion = (
                f"  Existe una discontinuidad de salto en x = {a}.\n"
                f"  La función salta de {left_limit} a {right_limit}.\n"
                f"  f({a}) = {f_at_point}  (definida por tramo derecho)\n"
            )

        procedure = (
            f"CASO 2: {case_name.upper()}\n"
            f"{'='*70}\n\n"
            f"Definición de función por partes:\n"
            f"       ⎧ x + {d2}   si x < {a}\n"
            f"f(x) = ⎨\n"
            f"       ⎩ x + {d4}   si x ≥ {a}\n\n"
            f"Paso 1: Evaluación en rama izquierda (x < {a})\n"
            f"  lim(x→{a}⁻) f(x) = {a} + {d2} = {left_limit}\n\n"
            f"Paso 2: Evaluación en rama derecha (x ≥ {a})\n"
            f"  lim(x→{a}⁺) f(x) = {a} + {d4} = {right_limit}\n\n"
            f"Paso 3: Cálculo del salto\n"
            f"  Magnitud del salto: |{right_limit} - {left_limit}| = {salto}\n\n"
            f"Paso 4: Punto crítico\n"
            f"  Punto de análisis: x = {a}\n"
            f"{conclusion}\n"
            f"Paso 5: Análisis de continuidad\n"
            f"  f({a}) = {f_at_point}\n"
        )

        analysis = self._analyze_jump(a, left_limit, right_limit, f_at_point)

        return {
            'case': 1,
            'case_name': case_name,
            'discontinuity_point': a,
            'function_definition': (
                f"f(x) = {{x + {d2} si x < {a}; x + {d4} si x ≥ {a}}}"
            ),
            'left_branch': f"x + {d2}",
            'right_branch': f"x + {d4}",
            'point_of_discontinuity': f"x = {a}",
            'procedure': procedure,
            'analysis': analysis,
            'table': self._generate_values_table_jump(a, d2, d4)
        }

    def _analyze_jump(self, point: int, left_lim: int, right_lim: int, value_at_point: int) -> Dict[str, Any]:
        """Análisis detallado para discontinuidad de salto."""
        is_continuous = left_lim == right_lim and value_at_point == right_lim
        if is_continuous:
            return {
                'discontinuity_type': 'Continua',
                'discontinuity_definition': (
                    f"La función por tramos es continua en x = {point} porque "
                    f"los límites laterales coinciden y f({point}) = {value_at_point}."
                ),
                'left_limit': left_lim,
                'right_limit': right_lim,
                'limits_equal': True,
                'value_at_discontinuity': value_at_point,
                'is_continuous': True,
                'reason': (
                    f"lim(x→{point}⁻) f(x) = {left_lim} = {right_lim} = lim(x→{point}⁺) f(x) "
                    f"y f({point}) = {value_at_point}."
                ),
                'removal_method': 'No aplica: la función ya es continua.'
            }

        return {
            'discontinuity_type': 'Salto (Finito)',
            'discontinuity_definition': (
                f"La función presenta un salto discontinuo en x = {point} porque "
                f"los límites laterales existen pero no son iguales."
            ),
            'left_limit': left_lim,
            'right_limit': right_lim,
            'limits_equal': False,
            'value_at_discontinuity': value_at_point,
            'is_continuous': False,
            'jump_magnitude': abs(right_lim - left_lim),
            'reason': (
                f"lim(x→{point}⁻) f(x) = {left_lim} ≠ {right_lim} = lim(x→{point}⁺) f(x)\n"
                f"Existe un salto de magnitud {abs(right_lim - left_lim)} en x = {point}."
            ),
            'removal_method': "Esta discontinuidad NO puede removerse (es no removible)."
        }

    def _generate_values_table_jump(self, point: int, d2: int, d4: int) -> str:
        """Genera tabla de valores para función de salto."""
        table = f"\nTABLA DE VALORES:\n"
        table += f"{'x':<8} | {'f(x)':<12} | {'Descripción':<20}\n"
        table += f"{'-'*50}\n"

        # Valores antes del punto
        for x in range(point - 3, point):
            fx = x + d2
            table += f"{x:<8} | {fx:<12} | Rama izquierda\n"

        # El punto de discontinuidad
        fx_at_point = point + d4
        table += f"{point:<8} | {fx_at_point:<12} | Definida (rama derecha)\n"

        # Valores después del punto
        for x in range(point + 1, point + 4):
            fx = x + d4
            table += f"{x:<8} | {fx:<12} | Rama derecha\n"

        return table

    def _generate_infinite(self) -> Dict[str, Any]:
        """Genera función con discontinuidad infinita."""
        # Función racional: f(x) = x / (x - a)
        # Asíntota vertical en x = a
        a = self.digits[0]  # d1
        self.discontinuity_point = a

        procedure = (
            f"CASO 3: DISCONTINUIDAD INFINITA\n"
            f"{'='*70}\n\n"
            f"Ecuación Base:\n"
            f"  f(x) = x / (x - {a})\n\n"
            f"Paso 1: Identificación del denominador\n"
            f"  Denominador: x - {a} = 0\n"
            f"  Punto crítico: x = {a}\n\n"
            f"Paso 2: Análisis del límite lateral izquierdo\n"
            f"  lim(x→{a}⁻) f(x) = lim(x→{a}⁻) x / (x - {a})\n"
            f"  Cuando x → {a}⁻: numerador → {a}⁻\n"
            f"                   denominador → 0⁻ (negativo cercano a 0)\n"
            f"  lim(x→{a}⁻) f(x) = +∞\n\n"
            f"Paso 3: Análisis del límite lateral derecho\n"
            f"  lim(x→{a}⁺) f(x) = lim(x→{a}⁺) x / (x - {a})\n"
            f"  Cuando x → {a}⁺: numerador → {a}⁺\n"
            f"                   denominador → 0⁺ (positivo cercano a 0)\n"
            f"  lim(x→{a}⁺) f(x) = +∞\n\n"
            f"Paso 4: Punto crítico y tipo de discontinuidad\n"
            f"  Punto de discontinuidad: x = {a}\n"
            f"  Tipo: Discontinuidad infinita (asíntota vertical)\n"
            f"  f({a}) no está definida (división por cero)\n\n"
            f"Paso 5: Caracterización\n"
            f"  • Asíntota vertical: x = {a}\n"
            f"  • Límites laterales: ambos tienden a infinito\n"
            f"  • Discontinuidad NO removible\n"
            f"  • Dominio: ℝ \\ {{{a}}}\n"
        )

        analysis = self._analyze_infinite(a)

        return {
            'case': 2,
            'case_name': 'Discontinuidad Infinita',
            'discontinuity_point': a,
            'function_definition': f"f(x) = x / (x - {a})  ,  x ≠ {a}",
            'point_of_discontinuity': f"x = {a}",
            'vertical_asymptote': f"x = {a}",
            'procedure': procedure,
            'analysis': analysis,
            'table': self._generate_values_table_infinite(a)
        }

    def _analyze_infinite(self, a: int) -> Dict[str, Any]:
        """Análisis detallado para discontinuidad infinita."""
        return {
            'discontinuity_type': 'Infinita (Asíntota Vertical)',
            'discontinuity_definition': (
                f"Existe una asíntota vertical en x = {a} porque el denominador "
                f"se anula mientras el numerador se aproxima a un valor no nulo."
            ),
            'left_limit': '+∞',
            'right_limit': '+∞',
            'limits_equal': False,
            'value_at_discontinuity': 'indefinida',
            'is_continuous': False,
            'asymptote': f"x = {a}",
            'reason': (
                f"lim(x→{a}⁻) f(x) = +∞ y lim(x→{a}⁺) f(x) = +∞\n"
                f"La función diverge a infinito en x = {a}"
            ),
            'removal_method': "Esta discontinuidad NO puede removerse."
        }

    def _generate_values_table_infinite(self, a: int) -> str:
        """Genera tabla de valores para función con asíntota vertical."""
        table = f"\nTABLA DE VALORES - f(x) = x / (x - {a}):\n"
        table += f"{'x':<8} | {'f(x)':<15} | {'Tendencia':<15}\n"
        table += f"{'-'*45}\n"

        # Valores antes del punto (izquierda)
        for x in range(a - 3, a):
            if x - a != 0:
                fx = x / (x - a)
                # Formatear valores extremadamente grandes como palabras 'mas infinito' / 'menos infinito'
                if abs(fx) > 1e8:
                    fx_display = 'menos infinito' if fx < 0 else 'mas infinito'
                else:
                    fx_display = f"{fx:.4f}"
                table += f"{x:<8} | {fx_display:<15} | Acerca a menos infinito\n"

        # El punto de discontinuidad
        table += f"{a:<8} | {'INDEFINIDA':<15} | ASÍNTOTA\n"

        # Valores después del punto (derecha)
        for x in range(a + 1, a + 4):
            if x - a != 0:
                fx = x / (x - a)
                if abs(fx) > 1e8:
                    fx_display = 'menos infinito' if fx < 0 else 'mas infinito'
                else:
                    fx_display = f"{fx:.4f}"
                table += f"{x:<8} | {fx_display:<15} | Acerca a mas infinito\n"

        return table

    def get_full_analysis(self) -> Dict[str, Any]:
        """Retorna el análisis completo del Módulo 9."""
        function_data = self.generate_function()
        
        return {
            'case_number': self.case,
            'case_name': function_data['case_name'],
            'digits': self.digits,
            'dv': self.dv,
            'd8': self.d8,
            'selection_criterion': f"d8 % 3 = {self.d8} % 3 = {self.case}",
            **function_data
        }
