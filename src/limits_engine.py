"""
src/limits_engine.py
====================
Módulo de Análisis de Funciones por Tramos y Límites Laterales.
MAT1186 — Universidad Católica de Temuco (UCT)

RESTRICCIÓN CRÍTICA: SIN math, numpy, sympy, scipy, pandas.
Todo cálculo usa aritmética pura de Python.

Reglas de negocio UCT:
  a    = d₃  (tercer dígito del RUT  → índice 2 en Python)
  caso = d₈ % 3  (octavo dígito → índice 7 en Python)

  Caso 0 (d₈%3 == 0) → Discontinuidad Removible
    f(x) = (x−a)(x+d₁) / (x−a)
    Simplificación interna: x+d₁  para x≠a

  Caso 1 (d₈%3 == 1) → Discontinuidad de Salto
    f₁(x) = x+d₂   (x < a)
    f₂(x) = x+d₄   (x ≥ a)

  Caso 2 (d₈%3 == 2) → Discontinuidad Infinita
    f(x) = (d₅+1) / (x−a)

RESTRICCIÓN PANEL DEFENSA:
  Los 7 CTkEntry del panel de defensa NUNCA se auto-rellenan.
  Solo _limpiar_defensa() (botón del estudiante) los borra.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# ── Paleta de colores (consistente con gui_interface.py) ─────────────────────
_C = {
    'primary':      '#0D2137',
    'primary_lt':   '#1565C0',
    'bg':           '#EEF2F7',
    'card':         '#FFFFFF',
    'card_inner':   '#F5F8FF',
    'border':       '#DDE3EC',
    'muted':        '#607D8B',
    'btn_neutral':  '#546E7A',
    'btn_hv':       '#37474F',
    # Defensa Oral
    'def_header':   '#1A2F45',
    'def_warn_bg':  '#FFF3E0',
    'def_warn_brd': '#FFA726',
    'def_accent':   '#E65100',
    'def_clear':    '#4A5568',
    'def_clear_hv': '#2D3748',
    'def_entry_brd':'#90A4C8',
    'def_field_bg': '#F8FAFF',
    'def_field_brd':'#C5D3E8',
    'def_eval':     '#1565C0',
    'def_eval_hv':  '#0D47A1',
    'def_ok':       '#2E7D32',
    'def_bad':      '#C62828',
    'def_neutral':  '#90A4AE',
}

# Colores del gráfico
_CURVE     = '#1565C0'   # azul (curvas)
_ASYMP     = '#E53935'   # rojo (asíntota)
_OPEN_FC   = 'white'     # relleno círculo abierto
_CLOSED_FC = '#1565C0'   # relleno círculo cerrado


# ══════════════════════════════════════════════════════════════════════════════
# Utilidades matemáticas puras  (SIN math / numpy / sympy)
# ══════════════════════════════════════════════════════════════════════════════

_INF = float('inf')


def _abs(x: float) -> float:
    return x if x >= 0 else -x


def _safe_eval(func: Callable, x: float) -> Optional[float]:
    """
    Evalúa func(x) de forma segura.
    · Retorna None si hay ZeroDivisionError / ValueError / OverflowError.
    · Retorna ±inf si el resultado supera 1e15 en magnitud.
    """
    try:
        val = func(x)
        if val != val:        # NaN check (único caso donde NaN != NaN)
            return None
        if val > 1e15:
            return _INF
        if val < -1e15:
            return -_INF
        return float(val)
    except (ZeroDivisionError, ValueError, OverflowError):
        return None


def _linspace(start: float, stop: float, num: int) -> List[float]:
    """Equivalente a numpy.linspace — implementación pura en Python."""
    if num <= 0:
        return []
    if num == 1:
        return [float(start)]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def _fmt(v: Optional[float], dec: int = 5) -> str:
    """Formatea un valor numérico para presentación en pantalla."""
    if v is None:
        return "No definido"
    if v == _INF:
        return "+∞"
    if v == -_INF:
        return "−∞"
    if v != v:
        return "indeterminado"
    # Valores numéricamente muy grandes se muestran como palabras 'mas infinito'/'menos infinito'
    try:
        if abs(float(v)) > 1e8:
            return 'mas infinito' if float(v) > 0 else 'menos infinito'
    except Exception:
        pass
    factor = 10 ** dec
    r = round(v * factor) / factor
    return str(int(r)) if r == int(r) else str(r)


# ══════════════════════════════════════════════════════════════════════════════
# Motor de cálculo analítico-numérico
# ══════════════════════════════════════════════════════════════════════════════

class MotorLimites:
    """
    Motor de análisis de límites y continuidad para funciones por tramos.

    Implementa las reglas UCT MAT1186:
      1. Extrae parámetros del RUT (d₁…d₈)
      2. Determina el punto crítico a = d₃
      3. Selecciona el caso mediante d₈ % 3
      4. Construye la(s) función(es) correspondiente(s)
      5. Genera tabla numérica de 8 puntos de aproximación
      6. Calcula límites laterales, existencia y continuidad
      7. Clasifica el tipo de discontinuidad
      8. Genera justificación matemática textual completa
    """

    def __init__(self, digits: List[int], dv: str) -> None:
        self.digits = list(digits)
        self.dv     = dv
        # Garantizar mínimo 8 dígitos
        while len(self.digits) < 8:
            self.digits.append(0)
        self._extraer_parametros()

    def _extraer_parametros(self) -> None:
        """Extrae dígitos individuales según nomenclatura de la pauta UCT."""
        d = self.digits
        # d₁=d[0], d₂=d[1], d₃=d[2], d₄=d[3], d₅=d[4], d₈=d[7]
        self.d1 = d[0]
        self.d2 = d[1]
        self.d3 = d[2]   # ← punto crítico a = d₃
        self.d4 = d[3]
        self.d5 = d[4]
        self.d8 = d[7]   # ← selector de caso

        self.a    = self.d3       # punto crítico de análisis
        self.caso = self.d8 % 3  # 0 = Removible, 1 = Salto, 2 = Infinita

    def _construir_funciones(self) -> Dict[str, Any]:
        """
        Construye las funciones Python y metadatos textuales
        según el caso detectado.

        Retorna dict con:
          f_izq, f_der, f_en_a,
          expr_orig, expr_izq, expr_der,
          has_tramos (bool)
        """
        a    = self.a
        caso = self.caso

        if caso == 0:
            # ─── CASO 0: Discontinuidad Removible ─────────────────────────
            # f(x) = (x−a)(x+d₁)/(x−a)   →   simplificada: x+d₁  (x ≠ a)
            # IMPORTANTE: la función ORIGINAL no está definida en x=a,
            # pero la simplificación permite calcular el límite.
            d1 = self.d1

            def f_izq(x: float) -> float:
                # Protección explícita contra evaluación en x=a
                if _abs(x - a) < 1e-14:
                    raise ZeroDivisionError(f"f no definida en x={a}")
                # Forma simplificada interna: (x-a)(x+d1)/(x-a) = x+d1
                return float(x + d1)

            f_der    = f_izq
            f_en_a   = None   # NO definida en x=a

            expr_orig  = f"f(x) = (x − {a})(x + {d1}) / (x − {a})"
            expr_izq   = f"f(x) = (x−{a})(x+{d1})/(x−{a})  ≡  x+{d1}   (x ≠ {a})"
            expr_der   = expr_izq
            has_tramos = False

        elif caso == 1:
            # ─── CASO 1: Discontinuidad de Salto / Continuidad ───────────
            # f₁(x) = x + d₂  (x < a)
            # f₂(x) = x + d₄  (x ≥ a)
            d2 = self.d2
            d4 = self.d4

            def f_izq(x: float) -> float:
                return float(x + d2)

            def f_der(x: float) -> float:
                return float(x + d4)

            f_en_a     = float(a + d4)   # f(a) = a+d₄  (tramo derecho incluye a)
            expr_orig  = f"f₁(x)=x+{d2}  |  f₂(x)=x+{d4}"
            expr_izq   = f"f₁(x) = x + {d2}   (x < {a})"
            expr_der   = f"f₂(x) = x + {d4}   (x ≥ {a})"
            has_tramos = True

        else:
            # ─── CASO 2: Discontinuidad Infinita ──────────────────────────
            # f(x) = (d₅+1) / (x−a)
            num = self.d5 + 1
            if num == 0:
                num = 1   # garantizar numerador no nulo

            def f_izq(x: float) -> float:
                if _abs(x - a) < 1e-14:
                    raise ZeroDivisionError(f"Asíntota vertical en x={a}")
                return float(num / (x - a))

            f_der      = f_izq
            f_en_a     = None   # No definida (asíntota)
            expr_orig  = f"f(x) = {num} / (x − {a})"
            expr_izq   = f"f(x) = {num}/(x−{a})   [asíntota vertical en x={a}]"
            expr_der   = expr_izq
            has_tramos = False

        return {
            'f_izq':       f_izq,
            'f_der':       f_der,
            'f_en_a':      f_en_a,
            'expr_orig':   expr_orig,
            'expr_izq':    expr_izq,
            'expr_der':    expr_der,
            'has_tramos':  has_tramos,
        }

    def _calcular_tabla(
        self,
        f_izq: Callable,
        f_der: Callable,
        a: float
    ) -> Tuple[List[Tuple], List[Tuple]]:
        """
        Genera tabla de aproximación numérica con los 8 puntos UCT.

        Izquierda: a−1, a−0.1, a−0.01, a−0.001
        Derecha:   a+0.001, a+0.01, a+0.1, a+1

        Protección automática: _safe_eval() captura división por cero.
        """
        pts_izq = [a - 1, a - 0.1, a - 0.01, a - 0.001]
        pts_der = [a + 0.001, a + 0.01, a + 0.1, a + 1]

        tabla_izq = [(x, _safe_eval(f_izq, x)) for x in pts_izq]
        tabla_der = [(x, _safe_eval(f_der, x)) for x in pts_der]
        return tabla_izq, tabla_der

    def calcular(self) -> Dict[str, Any]:
        """
        Punto de entrada principal. Realiza el análisis completo.

        Retorna diccionario exhaustivo con todos los resultados
        listos para ser visualizados en la interfaz.
        """
        a    = self.a
        caso = self.caso

        # ── 1. Construir funciones ────────────────────────────────────────
        funcs     = self._construir_funciones()
        f_izq     = funcs['f_izq']
        f_der     = funcs['f_der']
        f_en_a    = funcs['f_en_a']
        expr_izq  = funcs['expr_izq']
        expr_der  = funcs['expr_der']
        expr_orig = funcs['expr_orig']

        # ── 2. Tabla numérica ─────────────────────────────────────────────
        tabla_izq, tabla_der = self._calcular_tabla(f_izq, f_der, a)

        # ── 3. Límites laterales (delta muy pequeño) ──────────────────────
        DELTA       = 1e-9
        lim_izq_raw = _safe_eval(f_izq, a - DELTA)
        lim_der_raw = _safe_eval(f_der, a + DELTA)

        def _redondear(v: Optional[float]) -> Optional[float]:
            if v is None or v in (_INF, -_INF):
                return v
            r = round(v)
            return float(r) if _abs(v - r) < 1e-6 else round(v, 6)

        lim_izq = _redondear(lim_izq_raw)
        lim_der = _redondear(lim_der_raw)

        # ── 4. ¿Existe límite bilateral? ──────────────────────────────────
        existe_limite = False
        limite_valor  = None
        if (lim_izq is not None and lim_der is not None
                and lim_izq not in (_INF, -_INF)
                and lim_der not in (_INF, -_INF)
                and _abs(lim_izq - lim_der) < 1e-6):
            existe_limite = True
            limite_valor  = lim_izq

        # ── 5. ¿Es continua en x=a? ───────────────────────────────────────
        es_continua = False
        if existe_limite and f_en_a is not None:
            if _abs(limite_valor - f_en_a) < 1e-9:
                es_continua = True

        # ── 6. Clasificación de la discontinuidad ────────────────────────
        tipo_disc, desc_disc = self._clasificar(
            a, caso, lim_izq, lim_der, existe_limite,
            limite_valor, f_en_a
        )

        # ── 7. Regla del residuo (texto para pantalla) ────────────────────
        nombre_caso = f"Caso {caso + 1} → {tipo_disc}"
        regla_residuo = (
            f"d₈ = {self.d8}   →   {self.d8} % 3 = {caso}   →   {nombre_caso}"
        )

        # ── 8. Justificación completa ─────────────────────────────────────
        justificacion = self._generar_justificacion(
            a, caso, expr_orig, expr_izq, expr_der,
            lim_izq, lim_der, existe_limite,
            limite_valor, f_en_a, es_continua,
            tipo_disc, desc_disc
        )

        return {
            # Parámetros del RUT
            'a': a, 'caso': caso,
            'd1': self.d1, 'd2': self.d2, 'd3': self.d3,
            'd4': self.d4, 'd5': self.d5, 'd8': self.d8,
            # Expresiones textuales
            'expr_orig':     expr_orig,
            'expr_izq':      expr_izq,
            'expr_der':      expr_der,
            'has_tramos':    funcs['has_tramos'],
            'regla_residuo': regla_residuo,
            # Tabla numérica
            'tabla_izq': tabla_izq,
            'tabla_der': tabla_der,
            # Resultados del análisis
            'lim_izq':       lim_izq,
            'lim_der':       lim_der,
            'existe_limite': existe_limite,
            'limite_valor':  limite_valor,
            'f_en_a':        f_en_a,
            'es_continua':   es_continua,
            'tipo_disc':     tipo_disc,
            'desc_disc':     desc_disc,
            'justificacion': justificacion,
            # Funciones Python (para graficar)
            'f_izq': f_izq,
            'f_der': f_der,
        }

    def _clasificar(
        self, a, caso, lim_izq, lim_der, existe_limite,
        limite_valor, f_en_a
    ) -> Tuple[str, str]:
        """Retorna (nombre_tipo, descripción_detallada)."""

        if caso == 0:
            tipo = "Removible"
            lim_txt = _fmt(lim_izq)
            desc = (
                f"La función ORIGINAL f(x) = (x−{a})(x+{self.d1})/(x−{a})\n"
                f"NO está definida en x = {a} (el denominador se anula).\n\n"
                f"El factor (x−{a}) se cancela en numerador y denominador,\n"
                f"simplificándose internamente a f(x) = x + {self.d1}.\n\n"
                f"Esto permite calcular el límite:\n"
                f"  lím_{{x→{a}}} f(x) = {lim_txt}   (finito → límite EXISTE)\n\n"
                f"Discontinuidad REMOVIBLE: se puede 'reparar' definiendo\n"
                f"  f({a}) := {lim_txt}\n\n"
                f"En el gráfico: recta y = x+{self.d1} con un AGUJERO (∘) en x={a}."
            )

        elif caso == 1:
            li  = _fmt(lim_izq)
            ld  = _fmt(lim_der)
            same_limits = (
                lim_izq is not None and lim_der is not None
                and lim_izq not in (_INF, -_INF)
                and lim_der not in (_INF, -_INF)
                and _abs(lim_izq - lim_der) < 1e-9
            )
            same_value_at_point = (
                f_en_a is not None and lim_izq is not None
                and _abs(f_en_a - lim_izq) < 1e-9
            )

            if same_limits and same_value_at_point:
                tipo = "Continua"
                desc = (
                    f"La función tiene dos ramas lineales:\n"
                    f"  f₁(x) = x + {self.d2}   (x < {a})\n"
                    f"  f₂(x) = x + {self.d4}   (x ≥ {a})\n\n"
                    f"Los límites laterales coinciden:\n"
                    f"  lím_{{x→{a}⁻}} f(x) = {li}\n"
                    f"  lím_{{x→{a}⁺}} f(x) = {ld}\n\n"
                    f"Además, f({a}) = {_fmt(f_en_a)} coincide con el límite.\n"
                    f"Por lo tanto, la función es CONTINUA en x = {a}.\n\n"
                    f"Gráfico: ambas ramas se conectan en x = {a} sin salto."
                )
            else:
                tipo = "De Salto"
                if (lim_izq is not None and lim_der is not None
                        and lim_izq not in (_INF, -_INF)
                        and lim_der not in (_INF, -_INF)):
                    salto = _abs(lim_der - lim_izq)
                    salto_txt = _fmt(salto)
                else:
                    salto_txt = "—"
                desc = (
                    f"La función tiene dos ramas lineales distintas:\n"
                    f"  f₁(x) = x + {self.d2}   (x < {a})\n"
                    f"  f₂(x) = x + {self.d4}   (x ≥ {a})\n\n"
                    f"Los límites laterales existen pero son distintos:\n"
                    f"  lím_{{x→{a}⁻}} f(x) = {li}\n"
                    f"  lím_{{x→{a}⁺}} f(x) = {ld}\n\n"
                    f"Como lím⁻ ≠ lím⁺, el límite bilateral NO EXISTE.\n"
                    f"Magnitud del salto: |{ld} − {li}| = {salto_txt}\n\n"
                    f"f({a}) = {_fmt(f_en_a)}   (definida por el tramo f₂)\n\n"
                    f"Gráfico: ∘ en extremo izquierdo, ● en inicio del tramo derecho."
                )

        else:
            tipo = "Infinita (Asintótica)"
            num  = self.d5 + 1
            desc = (
                f"f(x) = {num} / (x − {a})\n\n"
                f"Cuando x → {a}⁻:  (x−{a}) → 0⁻  →  f(x) → {_fmt(lim_izq)}\n"
                f"Cuando x → {a}⁺:  (x−{a}) → 0⁺  →  f(x) → {_fmt(lim_der)}\n\n"
                f"La función diverge sin cota. El límite bilateral NO EXISTE.\n"
                f"ASÍNTOTA VERTICAL en x = {a}.\n\n"
                f"Gráfico: dos ramas hiperbólicas que se escapan hacia ±∞\n"
                f"al aproximarse a la recta vertical x = {a}."
            )

        return tipo, desc

    def _generar_justificacion(
        self, a, caso, expr_orig, expr_izq, expr_der,
        lim_izq, lim_der, existe_limite,
        limite_valor, f_en_a, es_continua,
        tipo_disc, desc_disc
    ) -> str:
        """Genera la justificación matemática completa en texto."""
        SEP  = '═' * 52
        sep  = '─' * 52
        j    = []

        j.append(SEP)
        j.append('  ANÁLISIS COMPLETO DE LÍMITES Y CONTINUIDAD')
        j.append(SEP)
        j.append('')
        j.append(f'  Punto crítico:  x = a = {a}   (a = d₃ del RUT)')
        j.append(f'  Caso:  d₈ % 3 = {self.d8} % 3 = {caso}  →  {tipo_disc}')
        j.append('')

        j.append(sep)
        j.append('  DEFINICIÓN DE LA FUNCIÓN')
        j.append(sep)
        if caso == 1:
            j.append(f'  {expr_izq}')
            j.append(f'  {expr_der}')
        else:
            j.append(f'  Forma original:    {expr_orig}')
            if caso == 0:
                j.append(f'  Simplificación:   x + {self.d1}   (válida para x ≠ {a})')
        j.append('')

        j.append(sep)
        j.append('  TABLA DE APROXIMACIÓN NUMÉRICA')
        j.append(sep)
        j.append(f'  x → {a}⁻   →   lím⁻ ≈ {_fmt(lim_izq)}')
        j.append(f'  x → {a}⁺   →   lím⁺ ≈ {_fmt(lim_der)}')
        j.append('')

        j.append(sep)
        j.append('  LÍMITES LATERALES')
        j.append(sep)
        j.append(f'  lím_{{x→{a}⁻}} f(x)  =  {_fmt(lim_izq)}')
        j.append(f'  lím_{{x→{a}⁺}} f(x)  =  {_fmt(lim_der)}')
        j.append('')
        if existe_limite:
            j.append(f'  ✓  Límite bilateral EXISTE  →  {_fmt(limite_valor)}')
        else:
            j.append('  ✗  Límite bilateral NO EXISTE')
        j.append('')

        j.append(sep)
        j.append('  VALOR DE LA FUNCIÓN EN x = a')
        j.append(sep)
        j.append(f'  f({a})  =  {"No definida" if f_en_a is None else _fmt(f_en_a)}')
        j.append('')

        j.append(sep)
        j.append('  CONTINUIDAD EN x = a')
        j.append(sep)
        if es_continua:
            j.append(f'  ✓  f es CONTINUA en x = {a}')
        else:
            j.append(f'  ✗  f es DISCONTINUA en x = {a}')
            j.append(f'     Tipo: {tipo_disc}')
        j.append('')

        j.append(sep)
        j.append('  CLASIFICACIÓN Y DESCRIPCIÓN')
        j.append(sep)
        for line in desc_disc.split('\n'):
            j.append(f'  {line}')
        j.append('')
        j.append(SEP)

        return '\n'.join(j)


# ══════════════════════════════════════════════════════════════════════════════
# Interfaz CTk  —  Pestaña de Funciones por Tramos
# ══════════════════════════════════════════════════════════════════════════════

class PestanaFuncionesPorTramos:
    """
    Pestaña CustomTkinter 5.x para el análisis de funciones por tramos.

    Layout de 3 columnas (idéntico al patrón de la pestaña de Cónicas):
      Izquierda  : función, regla del residuo, tabla numérica, análisis
      Centro     : gráfico Matplotlib (círculos abiertos/cerrados)
      Derecha    : 7 CTkEntry vacíos para la Defensa Oral

    ═══════════════════════════════════════════════════════════════════
    RESTRICCIÓN PANEL DEFENSA:
    Ningún campo es escrito por el código del sistema.
    Solo _limpiar_defensa() (botón del estudiante) los borra.
    ═══════════════════════════════════════════════════════════════════
    """

    def __init__(self, parent_frame: ctk.CTkFrame) -> None:
        self.parent         = parent_frame
        self._result        = None
        self._fig_canvas    = None
        self._mpl_figure    = None
        self._resize_job    = None
        self._resize_bound  = False
        # CTkEntry / CTkTextbox de defensa (NUNCA escritos desde sistema)
        self._defense_entries: Dict[str, Any] = {}
        self._defense_status_label: Optional[ctk.CTkLabel] = None
        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    # Construcción de la UI
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Layout de 3 columnas dentro del frame padre de la pestaña."""
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=0, minsize=370)
        self.parent.grid_columnconfigure(1, weight=1, minsize=480)
        self.parent.grid_columnconfigure(2, weight=0, minsize=340)

        left_card   = ctk.CTkFrame(self.parent, fg_color=_C['card'], corner_radius=14)
        center_card = ctk.CTkFrame(self.parent, fg_color=_C['card'], corner_radius=14)
        right_card  = ctk.CTkFrame(self.parent, fg_color=_C['card'], corner_radius=14)

        left_card.grid  (row=0, column=0, sticky='nsew', padx=(14, 5), pady=14)
        center_card.grid(row=0, column=1, sticky='nsew', padx=5,       pady=14)
        right_card.grid (row=0, column=2, sticky='nsew', padx=(5, 14), pady=14)

        self._build_left_panel(left_card)
        self._build_center_panel(center_card)
        self._build_defense_panel(right_card)

    # ── Panel izquierdo ───────────────────────────────────────────────────────

    def _build_left_panel(self, parent: ctk.CTkFrame) -> None:
        """Función, regla del residuo, tabla numérica y justificación."""

        ctk.CTkLabel(
            parent,
            text='Análisis de Funciones por Tramos',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=_C['primary'], anchor='w'
        ).pack(fill='x', padx=18, pady=(18, 6))

        # Tarjeta: Función detectada
        info = ctk.CTkFrame(
            parent, fg_color=_C['card_inner'], corner_radius=10,
            border_color=_C['border'], border_width=1
        )
        info.pack(fill='x', padx=14, pady=(0, 8))

        ctk.CTkLabel(
            info,
            text='📌  Función detectada por el RUT',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            text_color=_C['primary'], anchor='w'
        ).pack(fill='x', padx=12, pady=(10, 3))

        self._lbl_funcion = ctk.CTkLabel(
            info,
            text='Procese un RUT para ver la función',
            font=ctk.CTkFont(family='Consolas', size=10),
            text_color=_C['muted'], anchor='w', justify='left',
            wraplength=330
        )
        self._lbl_funcion.pack(fill='x', padx=12, pady=(0, 10))

        # Tarjeta: Regla del residuo
        residuo = ctk.CTkFrame(
            parent, fg_color='#EDE7F6', corner_radius=10,
            border_color='#B39DDB', border_width=1
        )
        residuo.pack(fill='x', padx=14, pady=(0, 8))

        ctk.CTkLabel(
            residuo,
            text='🔢  Regla del Residuo (d₈ % 3)',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            text_color='#4527A0', anchor='w'
        ).pack(fill='x', padx=12, pady=(9, 3))

        self._lbl_residuo = ctk.CTkLabel(
            residuo,
            text='—',
            font=ctk.CTkFont(family='Consolas', size=11),
            text_color='#311B92', anchor='w'
        )
        self._lbl_residuo.pack(fill='x', padx=12, pady=(0, 9))

        # Separador
        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(2, 6)
        )

        # Tabla de aproximación
        ctk.CTkLabel(
            parent,
            text='📊  Tabla de aproximación numérica',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            text_color=_C['primary'], anchor='w'
        ).pack(fill='x', padx=18, pady=(0, 4))

        self._tabla_textbox = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family='Consolas', size=9),
            border_color=_C['border'], border_width=1,
            corner_radius=8, wrap='none',
            state='disabled', height=178,
            activate_scrollbars=True
        )
        self._tabla_textbox.pack(fill='x', padx=14, pady=(0, 6))

        # Separador
        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(2, 6)
        )

        # Análisis y justificación
        ctk.CTkLabel(
            parent,
            text='📝  Análisis automático y justificación',
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            text_color=_C['primary'], anchor='w'
        ).pack(fill='x', padx=18, pady=(0, 4))

        self._analisis_textbox = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family='Consolas', size=9),
            border_color=_C['border'], border_width=1,
            corner_radius=8, wrap='word',
            state='disabled',
            activate_scrollbars=True
        )
        self._analisis_textbox.pack(fill='both', expand=True, padx=14, pady=(0, 14))

    # ── Panel central ─────────────────────────────────────────────────────────

    def _build_center_panel(self, parent: ctk.CTkFrame) -> None:
        """Canvas Matplotlib con círculos abiertos/cerrados."""

        ctk.CTkLabel(
            parent,
            text='Gráfico de la Función por Tramos',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=_C['primary'], anchor='w'
        ).pack(fill='x', padx=18, pady=(18, 4))

        ctk.CTkLabel(
            parent,
            text='∘ = punto excluido (intervalo abierto)       • = punto incluido (intervalo cerrado)',
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=_C['muted'], anchor='w'
        ).pack(fill='x', padx=18, pady=(0, 6))

        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(0, 6)
        )

        outer = ctk.CTkFrame(
            parent, fg_color='#F8F9FA', corner_radius=10,
            border_color=_C['border'], border_width=1
        )
        outer.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        # tk.Frame interno para FigureCanvasTkAgg
        self._graph_container = tk.Frame(outer, bg='#F8F9FA')
        self._graph_container.pack(fill='both', expand=True, padx=2, pady=2)
        self._graph_container.bind('<Configure>', self._on_graph_container_resize)

        self._placeholder = ctk.CTkLabel(
            self._graph_container,
            text='📈\n\nEl gráfico aparecerá\ntras procesar un RUT',
            font=ctk.CTkFont(family='Segoe UI', size=12),
            text_color='#B0BEC5', justify='center',
            bg_color='#F8F9FA'
        )
        self._placeholder.place(relx=0.5, rely=0.5, anchor='center')

    # ── Panel derecho: Defensa Oral ───────────────────────────────────────────

    def _build_defense_panel(self, parent: ctk.CTkFrame) -> None:
        """
        7 CTkEntry/CTkTextbox completamente vacíos para la Defensa Oral.

        ═══════════════════════════════════════════════════════════════
        RESTRICCIÓN ABSOLUTA:
        Ningún método escribe en self._defense_entries.
        Solo _limpiar_defensa() (botón del estudiante) los borra.
        ═══════════════════════════════════════════════════════════════
        """
        # Header
        hdr = ctk.CTkFrame(parent, fg_color=_C['def_header'], corner_radius=10)
        hdr.pack(fill='x', padx=14, pady=(14, 8))

        ctk.CTkLabel(
            hdr,
            text='🎓  Defensa Oral — Límites',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color='#FFFFFF', anchor='w'
        ).pack(fill='x', padx=14, pady=(12, 2))

        ctk.CTkLabel(
            hdr,
            text='UCT  ·  MAT1186  ·  Funciones por Tramos',
            font=ctk.CTkFont(family='Segoe UI', size=9),
            text_color='#90CAF9', anchor='w'
        ).pack(fill='x', padx=14, pady=(0, 12))

        # Instrucción
        warn = ctk.CTkFrame(
            parent, fg_color=_C['def_warn_bg'], corner_radius=8,
            border_color=_C['def_warn_brd'], border_width=1
        )
        warn.pack(fill='x', padx=14, pady=(0, 10))

        ctk.CTkLabel(
            warn,
            text='⚠  Complete durante la defensa',
            font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'),
            text_color=_C['def_accent'], anchor='w'
        ).pack(fill='x', padx=12, pady=(8, 2))

        ctk.CTkLabel(
            warn,
            text='Calcule y escriba cada valor\nmanualmente ante la comisión.',
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color='#BF360C', anchor='w', justify='left'
        ).pack(fill='x', padx=12, pady=(0, 8))

        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(0, 6)
        )

        # Área scrollable con los 7 campos
        scroll = ctk.CTkScrollableFrame(
            parent, fg_color='transparent',
            scrollbar_button_color=_C['border'],
            scrollbar_button_hover_color='#BDBDBD',
            corner_radius=0
        )
        scroll.pack(fill='both', expand=True, padx=8, pady=(0, 4))

        # Definición de los 7 campos de defensa
        # Formato: (clave, icono, etiqueta, placeholder, multilínea)
        CAMPOS = [
            ('lim_izq',  '◀', 'lím_{x→a⁻} f(x) = ?',        'Ej: 5',                    False),
            ('lim_der',  '▶', 'lím_{x→a⁺} f(x) = ?',        'Ej: 7',                    False),
            ('existe',   '?', '¿Existe el límite bilateral?', 'Sí / No',                  False),
            ('f_en_a',   'f', 'Valor de f(a) = ?',           'Ej: 7  /  No definida',    False),
            ('continua', '∞', '¿Es continua en x = a?',      'Sí / No',                  False),
            ('tipo_disc','⚡','Tipo de discontinuidad',       'Removible / Salto / Infinita', False),
            ('justif',   '📝','Justificación escrita',        'Explique analíticamente...', True),
        ]

        for key, icono, etiqueta, placeholder, multilínea in CAMPOS:
            # Tarjeta individual por campo
            card = ctk.CTkFrame(
                scroll, fg_color=_C['def_field_bg'], corner_radius=9,
                border_color=_C['def_field_brd'], border_width=1
            )
            card.pack(fill='x', padx=4, pady=(0, 8))

            # Fila de encabezado
            row = ctk.CTkFrame(card, fg_color='transparent')
            row.pack(fill='x', padx=10, pady=(10, 4))

            ctk.CTkLabel(
                row, text=icono,
                font=ctk.CTkFont(family='Segoe UI', size=13),
                text_color=_C['primary_lt'], width=22, anchor='w'
            ).pack(side='left')

            ctk.CTkLabel(
                row, text=etiqueta,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=_C['primary'], anchor='w'
            ).pack(side='left', fill='x', expand=True)

            # ── Widget de entrada VACÍO — NUNCA se auto-rellena ────────────
            if multilínea:
                widget = ctk.CTkTextbox(
                    card, height=70,
                    font=ctk.CTkFont(family='Consolas', size=10),
                    border_color=_C['def_entry_brd'], border_width=1,
                    corner_radius=7, fg_color='#FFFFFF', wrap='word'
                )
            else:
                widget = ctk.CTkEntry(
                    card, placeholder_text=placeholder, height=36,
                    font=ctk.CTkFont(family='Consolas', size=11),
                    border_color=_C['def_entry_brd'],
                    corner_radius=7, fg_color='#FFFFFF'
                )
            widget.pack(fill='x', padx=10, pady=(0, 10))

            # Registrar widget (solo para _limpiar_defensa())
            self._defense_entries[key] = widget

        # Botón limpiar (solo acción del estudiante)
        ctk.CTkButton(
            parent,
            text='✅  Evaluar defensa',
            command=self._evaluar_defensa,
            height=34,
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            fg_color=_C['def_eval'],
            hover_color=_C['def_eval_hv'],
            corner_radius=8
        ).pack(fill='x', padx=14, pady=(2, 8))

        ctk.CTkButton(
            parent,
            text='🗑  Limpiar campos de defensa',
            command=self._limpiar_defensa,
            height=34,
            font=ctk.CTkFont(family='Segoe UI', size=11),
            fg_color=_C['def_clear'],
            hover_color=_C['def_clear_hv'],
            corner_radius=8
        ).pack(fill='x', padx=14, pady=(0, 8))

        self._defense_status_label = ctk.CTkLabel(
            parent,
            text='Pulsa “Evaluar defensa” para verificar cada campo.',
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=_C['def_neutral'],
            justify='left',
            anchor='w'
        )
        self._defense_status_label.pack(fill='x', padx=14, pady=(0, 14))

    # ─────────────────────────────────────────────────────────────────────────
    # API pública
    # ─────────────────────────────────────────────────────────────────────────

    def actualizar(self, digits: List[int], dv: str) -> None:
        """
        Llamado desde InterfazAnalisisConicas.on_process().
        Ejecuta el motor y refresca todos los paneles visuales.
        Los campos de defensa NO se tocan bajo ninguna condición.
        """
        motor        = MotorLimites(digits, dv)
        self._result = motor.calcular()
        self._actualizar_display(self._result)
        self._dibujar_grafica(self._result)
        self._reset_defense_evaluation()

    # ─────────────────────────────────────────────────────────────────────────
    # Actualización de texto
    # ─────────────────────────────────────────────────────────────────────────

    def _actualizar_display(self, r: Dict[str, Any]) -> None:
        """Actualiza etiquetas, tabla y análisis con los resultados del motor."""
        a    = r['a']
        caso = r['caso']

        # ── Etiqueta de función ──
        if caso == 0:
            d1  = r['d1']
            txt = (
                f"Forma original:   f(x) = (x−{a})(x+{d1}) / (x−{a})\n"
                f"Simplificación:   f(x) = x + {d1}   (x ≠ {a})\n"
                f"f({a}) = No definida   →   límite = {_fmt(r['lim_izq'])}"
            )
        elif caso == 1:
            txt = (
                f"f₁(x) = x + {r['d2']}   (x < {a})\n"
                f"f₂(x) = x + {r['d4']}   (x ≥ {a})\n"
                f"f({a}) = {_fmt(r['f_en_a'])}   (tramo f₂)"
            )
        else:
            num = r['d5'] + 1
            txt = (
                f"f(x) = {num} / (x − {a})\n"
                f"f({a}) = No definida   →   asíntota vertical"
            )
        self._lbl_funcion.configure(text=txt)

        # ── Regla del residuo ──
        self._lbl_residuo.configure(text=r['regla_residuo'])

        # ── Tabla numérica ──
        self._tabla_textbox.configure(state='normal')
        self._tabla_textbox.delete('1.0', 'end')
        self._tabla_textbox.insert('end', self._formatear_tabla(r))
        self._tabla_textbox.configure(state='disabled')

        # ── Análisis y justificación ──
        self._analisis_textbox.configure(state='normal')
        self._analisis_textbox.delete('1.0', 'end')
        self._analisis_textbox.insert('end', r['justificacion'])
        self._analisis_textbox.configure(state='disabled')

    def _formatear_tabla(self, r: Dict[str, Any]) -> str:
        """Construye el texto formateado de la tabla de aproximación numérica."""
        a = r['a']
        W = 12   # ancho columna f(x)

        lines = []
        lines.append(f"{'x':<12}{'f(x)':<{W}}{'Dirección'}")
        lines.append('─' * 42)

        dirs_izq = ['a − 1 →', 'a − 0.1 →', 'a − 0.01 →', 'a − 0.001 →']
        for i, (x, fx) in enumerate(r['tabla_izq']):
            fxs = _fmt(fx) if fx is not None else 'No def.'
            lines.append(f"{x:<12.5g}{fxs:<{W}}{dirs_izq[i]}")

        lines.append(f"  {'─'*8}  x = {a}  (punto crítico)  {'─'*8}")

        dirs_der = ['← a + 0.001', 'a + 0.01', 'a + 0.1', 'a + 1']
        for i, (x, fx) in enumerate(r['tabla_der']):
            fxs = _fmt(fx) if fx is not None else 'No def.'
            lines.append(f"{x:<12.5g}{fxs:<{W}}{dirs_der[i]}")

        lines.append('')
        lines.append(f"lím_{{x→{a}⁻}} = {_fmt(r['lim_izq'])}")
        lines.append(f"lím_{{x→{a}⁺}} = {_fmt(r['lim_der'])}")
        lines.append(f"Límite bilateral: {'EXISTE  →  ' + _fmt(r['limite_valor']) if r['existe_limite'] else 'NO EXISTE'}")

        return '\n'.join(lines)

    # ─────────────────────────────────────────────────────────────────────────
    # Gráfico Matplotlib
    # ─────────────────────────────────────────────────────────────────────────

    def _dibujar_grafica(self, r: Dict[str, Any]) -> None:
        """
        Dibuja la función por tramos con Matplotlib.

        Convenciones visuales:
          ∘  Círculo VACÍO  → punto EXCLUIDO (intervalo abierto)
          ●  Círculo LLENO  → punto INCLUIDO (intervalo cerrado)
        """
        a    = r['a']
        caso = r['caso']

        # Destruir canvas previo
        if self._fig_canvas is not None:
            self._fig_canvas.get_tk_widget().destroy()
            self._fig_canvas = None

        # Ocultar placeholder
        if hasattr(self, '_placeholder'):
            self._placeholder.place_forget()

        # ── Crear figura ──────────────────────────────────────────────────
        fig = Figure(figsize=(5.5, 5), dpi=96, facecolor='#F8F9FA')
        ax  = fig.add_subplot(111)
        fig.set_tight_layout(True)

        ax.set_facecolor('#FAFAFA')
        ax.grid(True, linestyle='--', linewidth=0.5, color='#B0BEC5', alpha=0.7)
        ax.axhline(0, color='#546E7A', linewidth=0.8, zorder=1)
        ax.axvline(0, color='#546E7A', linewidth=0.8, zorder=1)
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('f(x)', fontsize=10)

        # ── Rangos de x (separando el punto a para evitar saltos) ─────────
        MARGEN = 2.5
        GAP    = 0.04   # hueco alrededor de a
        x_min  = a - MARGEN - 0.5
        x_max  = a + MARGEN + 0.5

        x_izq = _linspace(x_min, a - GAP, 400)
        x_der = _linspace(a + GAP, x_max, 400)

        f_izq_fn = r['f_izq']
        f_der_fn = r['f_der']

        y_izq_raw = [_safe_eval(f_izq_fn, x) for x in x_izq]
        y_der_raw = [_safe_eval(f_der_fn, x) for x in x_der]

        # Filtrar infinitos y None
        def _filtrar(xs, ys):
            px, py = [], []
            for x, y in zip(xs, ys):
                if y is not None and y not in (_INF, -_INF) and _abs(y) < 600:
                    px.append(x)
                    py.append(y)
            return px, py

        px_izq, py_izq = _filtrar(x_izq, y_izq_raw)
        px_der, py_der = _filtrar(x_der, y_der_raw)

        # ── Dibujar curvas ────────────────────────────────────────────────
        if px_izq:
            ax.plot(px_izq, py_izq, color=_CURVE, linewidth=2.5, zorder=4)
        if px_der:
            ax.plot(px_der, py_der, color=_CURVE, linewidth=2.5, zorder=4)

        # ── Círculos y marcas específicos por caso ────────────────────────
        lim_izq = r['lim_izq']
        lim_der = r['lim_der']
        f_en_a  = r['f_en_a']

        if caso == 0:
            # ── Caso 0: agujero (∘) en (a, lím) ──────────────────────────
            if lim_izq is not None and lim_izq not in (_INF, -_INF):
                ax.scatter(
                    [a], [lim_izq], s=100,
                    facecolors=_OPEN_FC, edgecolors=_CURVE, linewidths=2.5,
                    zorder=6, label=f'∘ Agujero en ({a}, {_fmt(lim_izq)})'
                )
            titulo = (
                f'Caso 1 — Discontinuidad Removible\n'
                f'f(x) = (x−{a})(x+{r["d1"]})/(x−{a})'
            )

        elif caso == 1:
            # ── Caso 1: ∘ en límite izq,  ● en f(a) ─────────────────────
            if lim_izq is not None and lim_izq not in (_INF, -_INF):
                ax.scatter(
                    [a], [lim_izq], s=100,
                    facecolors=_OPEN_FC, edgecolors=_CURVE, linewidths=2.5,
                    zorder=6, label=f'∘ lím⁻ = {_fmt(lim_izq)} (excluido)'
                )
            if f_en_a is not None:
                ax.scatter(
                    [a], [f_en_a], s=100,
                    facecolors=_CLOSED_FC, edgecolors=_CURVE, linewidths=2.5,
                    zorder=6, label=f'● f({a}) = {_fmt(f_en_a)} (incluido)'
                )
            tipo_disc = r.get('tipo_disc', 'Discontinuidad de Salto')
            titulo = (
                f'Caso 2 — {tipo_disc}\n'
                f'f₁(x)=x+{r["d2"]}  (x<{a})     f₂(x)=x+{r["d4"]}  (x≥{a})'
            )

        else:
            # ── Caso 2: asíntota vertical ─────────────────────────────────
            ax.axvline(
                x=a, color=_ASYMP, linestyle='--', linewidth=2.0,
                zorder=3, label=f'Asíntota vertical  x = {a}'
            )
            titulo = (
                f'Caso 3 — Discontinuidad Infinita\n'
                f'f(x) = {r["d5"]+1} / (x−{a})'
            )

        # Marcar x=a con línea gris suave
        ax.axvline(x=a, color='#90A4AE', linewidth=0.6, linestyle=':', alpha=0.8, zorder=2)

        # Etiqueta de x=a en el eje
        ax.text(
            a, 0.02, f'x={a}',
            transform=ax.get_xaxis_transform(),
            fontsize=8, color='#37474F',
            ha='center', va='bottom'
        )

        ax.set_title(titulo, fontsize=9, pad=8, color=_C['primary'])
        ax.set_xlim(x_min, x_max)
        ax.set_anchor('C')

        # Límites Y automáticos razonables
        all_y = py_izq + py_der
        if all_y:
            y_lo  = min(all_y)
            y_hi  = max(all_y)
            rng   = y_hi - y_lo if y_hi != y_lo else 4.0
            mg    = rng * 0.25
            ax.set_ylim(y_lo - mg, y_hi + mg)
        else:
            ax.set_ylim(-10, 10)

        ax.legend(fontsize=8, loc='upper right', framealpha=0.85)
        fig.tight_layout(pad=1.0)
        fig.subplots_adjust(left=0.10, right=0.96, top=0.93, bottom=0.10)

        self._mpl_figure = fig

        # Incrustar en Tkinter
        self._fig_canvas = FigureCanvasTkAgg(fig, master=self._graph_container)
        self._fig_canvas.draw()
        self._fig_canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self._ajustar_figura_al_contenedor()

    # ─────────────────────────────────────────────────────────────────────────
    # Limpieza
    # ─────────────────────────────────────────────────────────────────────────

    def _limpiar_defensa(self) -> None:
        """
        Limpia los campos de defensa.
        Esta función SOLO puede ser invocada por el botón que acciona
        el propio estudiante — nunca desde lógica automática del sistema.
        """
        for widget in self._defense_entries.values():
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete('1.0', 'end')
            else:
                widget.delete(0, 'end')

        self._reset_defense_evaluation()

    def _evaluar_defensa(self) -> None:
        """Evalúa los campos de defensa oral contra el resultado actual."""
        if self._result is None:
            messagebox.showwarning(
                'Sin resultado',
                'Primero procese un RUT para generar la función por tramos.'
            )
            return

        expectativas = self._construir_expectativas_defensa(self._result)
        correctos = 0
        evaluables = 0
        errores: List[str] = []

        for key, spec in expectativas.items():
            widget = self._defense_entries.get(key)
            if widget is None:
                continue

            evaluables += 1
            respuesta = self._obtener_texto_widget(widget)
            es_correcto = self._comparar_respuesta_defensa(respuesta, spec)
            widget.configure(border_color=_C['def_ok'] if es_correcto else _C['def_bad'])

            if es_correcto:
                correctos += 1
            else:
                errores.append(f"{spec['label']}: se esperaba {spec['expected']}")

        if self._defense_status_label is not None:
            color = _C['def_ok'] if correctos == evaluables else _C['def_bad']
            self._defense_status_label.configure(
                text=f'Defensa: {correctos}/{evaluables} campos correctos.',
                text_color=color
            )

        if correctos == evaluables:
            messagebox.showinfo('Evaluación de defensa', 'Todos los campos evaluables están correctos.')
        else:
            detalle = '\n'.join(f'• {item}' for item in errores[:8])
            if len(errores) > 8:
                detalle += f'\n• ... y {len(errores) - 8} campo(s) más.'
            messagebox.showwarning(
                'Evaluación de defensa',
                f'Hay {evaluables - correctos} campo(s) incorrecto(s).\n\n{detalle}'
            )

    def _reset_defense_evaluation(self) -> None:
        """Restablece el estado visual de la evaluación de defensa."""
        for widget in self._defense_entries.values():
            if isinstance(widget, ctk.CTkTextbox):
                widget.configure(border_color=_C['def_entry_brd'])
            else:
                widget.configure(border_color=_C['def_entry_brd'])

        if self._defense_status_label is not None:
            self._defense_status_label.configure(
                text='Pulsa “Evaluar defensa” para verificar cada campo.',
                text_color=_C['def_neutral']
            )

    def _obtener_texto_widget(self, widget: Any) -> str:
        """Obtiene el texto de un CTkEntry o CTkTextbox."""
        if isinstance(widget, ctk.CTkTextbox):
            return widget.get('1.0', 'end').strip()
        return widget.get().strip()

    def _construir_expectativas_defensa(self, result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Construye respuestas esperadas para el panel de defensa."""
        a = float(result.get('a', 0) or 0)
        caso = int(result.get('caso', 0) or 0)
        lim_izq = result.get('lim_izq')
        lim_der = result.get('lim_der')
        f_en_a = result.get('f_en_a')
        es_continua = bool(result.get('es_continua', False))
        tipo_disc = str(result.get('tipo_disc', '') or '')

        if caso == 0:
            return {
                'lim_izq': {'label': 'Límite lateral izquierdo', 'expected': self._formatear_numero(lim_izq), 'kind': 'number', 'value': lim_izq},
                'lim_der': {'label': 'Límite lateral derecho', 'expected': self._formatear_numero(lim_der), 'kind': 'number', 'value': lim_der},
                'existe': {'label': 'Existe el límite bilateral', 'expected': 'Sí' if result.get('existe_limite') else 'No', 'kind': 'bool', 'value': bool(result.get('existe_limite'))},
                'f_en_a': {'label': 'Valor de f(a)', 'expected': 'No definida' if f_en_a is None else self._formatear_numero(f_en_a), 'kind': 'value_or_text', 'value': f_en_a},
                'continua': {'label': 'Es continua en x = a', 'expected': 'Sí' if es_continua else 'No', 'kind': 'bool', 'value': es_continua},
                'tipo_disc': {'label': 'Tipo de discontinuidad', 'expected': tipo_disc, 'kind': 'text', 'tokens': [tipo_disc]},
                'justif': {'label': 'Justificación escrita', 'expected': 'removible', 'kind': 'text', 'tokens': ['removible']},
            }

        if caso == 1:
            existe_bilateral = 'Sí' if result.get('existe_limite') else 'No'
            justif_tokens = ['salto', self._formatear_numero(lim_izq), self._formatear_numero(lim_der)]
            if es_continua:
                justif_tokens = ['continua', self._formatear_numero(lim_izq), self._formatear_numero(lim_der)]

            return {
                'lim_izq': {'label': 'Límite lateral izquierdo', 'expected': self._formatear_numero(lim_izq), 'kind': 'number', 'value': lim_izq},
                'lim_der': {'label': 'Límite lateral derecho', 'expected': self._formatear_numero(lim_der), 'kind': 'number', 'value': lim_der},
                'existe': {'label': 'Existe el límite bilateral', 'expected': existe_bilateral, 'kind': 'bool', 'value': bool(result.get('existe_limite'))},
                'f_en_a': {'label': 'Valor de f(a)', 'expected': self._formatear_numero(f_en_a), 'kind': 'number', 'value': f_en_a},
                'continua': {'label': 'Es continua en x = a', 'expected': 'Sí' if es_continua else 'No', 'kind': 'bool', 'value': es_continua},
                'tipo_disc': {'label': 'Tipo de discontinuidad', 'expected': tipo_disc, 'kind': 'text', 'tokens': [tipo_disc]},
                'justif': {'label': 'Justificación escrita', 'expected': 'salto' if not es_continua else 'continua', 'kind': 'text', 'tokens': justif_tokens},
            }

        return {
            'lim_izq': {'label': 'Límite lateral izquierdo', 'expected': self._formatear_numero(lim_izq), 'kind': 'number', 'value': lim_izq},
            'lim_der': {'label': 'Límite lateral derecho', 'expected': self._formatear_numero(lim_der), 'kind': 'number', 'value': lim_der},
            'existe': {'label': 'Existe el límite bilateral', 'expected': 'No', 'kind': 'bool', 'value': False},
            'f_en_a': {'label': 'Valor de f(a)', 'expected': 'No definida', 'kind': 'text', 'tokens': ['no definida', 'indefinida']},
            'continua': {'label': 'Es continua en x = a', 'expected': 'No', 'kind': 'bool', 'value': False},
            'tipo_disc': {'label': 'Tipo de discontinuidad', 'expected': tipo_disc, 'kind': 'text', 'tokens': [tipo_disc, 'infinita', 'infinita (asintotica)', 'infinita asintotica', 'asintota', 'asintotica']},
            'justif': {'label': 'Justificación escrita', 'expected': 'asíntota vertical', 'kind': 'text', 'tokens': ['asintota vertical', 'asintota', 'infinita', f'x = {self._formatear_numero(a)}']},
        }

    def _comparar_respuesta_defensa(self, respuesta: str, spec: Dict[str, Any]) -> bool:
        """Compara la respuesta manual con la expectativa calculada."""
        kind = spec.get('kind', 'text')
        respuesta_norm = self._normalizar_texto(respuesta)

        if kind == 'bool':
            esperado = 'si' if bool(spec.get('value', False)) else 'no'
            return esperado in respuesta_norm

        if kind == 'number':
            valor = spec.get('value')
            # Aceptar notación textual para infinitos: "mas infinito", "menos infinito", "infinito positivo/negativo"
            if valor == _INF:
                tokens = ('+infinito', 'masinfinito', 'infinitopositivo', 'positivoinfinito', 'infinito', '+inf', '+infty', 'infty')
                return any(tok in respuesta_norm for tok in tokens)
            if valor == -_INF:
                tokens = ('-infinito', 'menosinfinito', 'infinitonegativo', 'negativoinfinito', '-inf', '-infty', 'infty')
                return any(tok in respuesta_norm for tok in tokens)
            # Aceptar texto 'infinito' cuando el valor numérico es extremadamente grande
            try:
                vnum = float(valor)
            except Exception:
                vnum = None
            if vnum is not None and abs(vnum) > 1e8:
                # si el número es muy grande, aceptar 'infinito' como respuesta equivalente
                if vnum > 0:
                    tokens = ('+infinito', 'masinfinito', 'infinitopositivo', 'positivoinfinito', 'infinito')
                else:
                    tokens = ('-infinito', 'menosinfinito', 'infinitonegativo', 'negativoinfinito', 'infinito')
                return any(tok in respuesta_norm for tok in tokens)
            esperado = self._formatear_numero(valor)
            return esperado in respuesta_norm

        if kind == 'value_or_text':
            valor = spec.get('value')
            if valor is None:
                return any(token in respuesta_norm for token in ('nodefinida', 'indefinida', 'nosedefine'))
            return self._formatear_numero(valor) in respuesta_norm

        # Tokenización tolerante: aceptar si cualquier palabra clave aparece en la respuesta
        raw_tokens = [t for t in spec.get('tokens', []) if t]
        if not raw_tokens:
            return False
        norm_tokens = [self._normalizar_texto(t) for t in raw_tokens]

        # Descomponer cada token en subpalabras (p.ej. 'asintota vertical' -> ['asintota','vertical'])
        subtokens = set()
        for t in raw_tokens:
            # separar por caracteres no alfanuméricos
            parts = ''.join(ch if ch.isalnum() else ' ' for ch in t).split()
            for p in parts:
                subtokens.add(self._normalizar_texto(p))

        # También incluir las formas completas normalizadas
        for t in norm_tokens:
            subtokens.add(t)

        # Aceptar si alguna subpalabra aparece en la respuesta normalizada
        for st in subtokens:
            if not st:
                continue
            if st in respuesta_norm:
                return True

        # Fallback: aceptar si la respuesta contiene alguna de las formas completas (por si hay paréntesis u otros)
        for t in norm_tokens:
            if t in respuesta_norm:
                return True

        return False

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto para comparación tolerante."""
        texto = texto.lower().strip()
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ü': 'u', 'ñ': 'n',
            '−': '-', '–': '-', '×': 'x', '·': '', ' ': '',
        }
        for origen, destino in reemplazos.items():
            texto = texto.replace(origen, destino)
        return ''.join(ch for ch in texto if ch.isalnum() or ch in '().,+-=<>:/')

    def _formatear_numero(self, value: Any) -> str:
        """Formatea números con máximo 2 decimales para la evaluación."""
        if value is None:
            return 'No definido'
        if value == _INF:
            return '+∞'
        if value == -_INF:
            return '−∞'
        value = float(value)
        if _abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        texto = f'{value:.2f}'.rstrip('0').rstrip('.')
        return '0' if texto == '-0' else texto

    def _on_graph_container_resize(self, event) -> None:
        if event.widget is not self._graph_container:
            return
        self._programar_ajuste_tamano()

    def _programar_ajuste_tamano(self) -> None:
        self._cancelar_resize_programado()
        if self._fig_canvas is None:
            return
        self._resize_job = self._graph_container.after(60, self._ajustar_figura_al_contenedor)

    def _cancelar_resize_programado(self) -> None:
        if self._resize_job is not None:
            try:
                self._graph_container.after_cancel(self._resize_job)
            except Exception:
                pass
            self._resize_job = None

    def _ajustar_figura_al_contenedor(self) -> None:
        if self._fig_canvas is None or self._mpl_figure is None:
            return

        widget = self._fig_canvas.get_tk_widget()
        width = widget.winfo_width()
        height = widget.winfo_height()

        if width <= 10 or height <= 10:
            width = max(self._graph_container.winfo_width() - 20, 320)
            height = max(self._graph_container.winfo_height() - 20, 280)

        dpi = self._mpl_figure.dpi
        self._mpl_figure.set_size_inches(max(width, 1) / dpi, max(height, 1) / dpi, forward=True)
        self._mpl_figure.tight_layout(pad=1.0)
        self._fig_canvas.draw_idle()
