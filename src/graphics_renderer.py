"""
Módulo 8: Motor de Renderizado de Gráficos de Cónicas
======================================================
Motor gráfico corregido y completo para renderizar cónicas usando
Matplotlib embebido en Tkinter (FigureCanvasTkAgg).

RESTRICCIÓN CRÍTICA:  SIN math, numpy, sympy, scipy, pandas.
Todas las raíces cuadradas y potencias usan aritmética pura de Python:
    sqrt(x) → x ** 0.5
    abs(x)  → x if x >= 0 else -x
    round(x, n) → round() nativo de Python

Características del motor:
- Rangos de ejes calculados dinámicamente según (h, k, a, b, r, p)
- Aspect ratio 'equal' para no deformar figuras
- Bounding-box para elipse/circunferencia (patches.Ellipse/Circle)
- Parametrización angular para hipérbola (sin despejar y de x)
- Dibujo explícito de: Centro, Vértices, Focos, Ejes de simetría,
  Directriz (parábola), Asíntotas (hipérbola)
"""

from typing import Any, Dict, Optional, List, Tuple

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import matplotlib.lines as mlines


# ---------------------------------------------------------------------------
# Utilidades matemáticas puras (SIN math / numpy / sympy)
# ---------------------------------------------------------------------------

def _sqrt(x: float) -> float:
    """Raíz cuadrada segura. Retorna 0 si x es negativo por error de redondeo."""
    if x < 0:
        x = 0.0
    return x ** 0.5


def _abs(x: float) -> float:
    return x if x >= 0 else -x


def _linspace(start: float, stop: float, num: int) -> List[float]:
    """Equivalente a numpy.linspace, implementación pura."""
    if num <= 0:
        return []
    if num == 1:
        return [float(start)]
    step = (stop - start) / (num - 1)
    return [start + i * step for i in range(num)]


def _arange(start: float, stop: float, step: float) -> List[float]:
    """Equivalente a numpy.arange, implementación pura."""
    result = []
    val = start
    if step > 0:
        while val < stop:
            result.append(val)
            val += step
    else:
        while val > stop:
            result.append(val)
            val += step
    return result


# ---------------------------------------------------------------------------
# Motor de Rangos Dinámicos
# ---------------------------------------------------------------------------

def _calcular_rango_dinamico(
    h: float, k: float,
    radio_x: float, radio_y: float,
    margen_rel: float = 0.35
) -> Tuple[float, float, float, float]:
    """
    Calcula los límites del plano cartesiano de manera dinámica para que la
    figura quede siempre completa y centrada.

    Parámetros:
    - h, k      : centro de la cónica
    - radio_x   : extensión máxima en X desde el centro (ej. semieje a)
    - radio_y   : extensión máxima en Y desde el centro (ej. semieje b)
    - margen_rel: fracción de margen extra sobre el radio (default 35%)

    Retorna: (x_min, x_max, y_min, y_max)
    """
    margen_x = radio_x * margen_rel
    margen_y = radio_y * margen_rel

    # Garantizar un mínimo de 2 unidades de margen para figuras muy pequeñas
    margen_x = max(margen_x, 2.0)
    margen_y = max(margen_y, 2.0)

    x_min = h - radio_x - margen_x
    x_max = h + radio_x + margen_x
    y_min = k - radio_y - margen_y
    y_max = k + radio_y + margen_y

    return x_min, x_max, y_min, y_max


# ---------------------------------------------------------------------------
# Clase Principal
# ---------------------------------------------------------------------------

class RenderizadorGraficosConicas:
    """
    Motor de renderizado de cónicas en un contenedor Tkinter usando Matplotlib.

    Recibe los coeficientes de la ecuación general (A, B, C, D, E),
    el tipo de cónica y los datos canónicos calculados por el Módulo 6.

    Dibuja de forma visualmente explícita y con colores diferenciados:
      • La curva de la cónica
      • Centro
      • Vértices
      • Focos
      • Ejes de simetría (mayor/menor o transverso/conjugado)
      • Directriz (parábolas)
      • Asíntotas (hipérbolas)

    Restricción: SIN math, numpy, sympy, scipy, pandas.
    """

    # Paleta de colores fija para elementos geométricos
    COLOR_CURVA       = '#1565C0'   # azul profundo
    COLOR_CENTRO      = '#E53935'   # rojo
    COLOR_VERTICES    = '#F57C00'   # naranja
    COLOR_FOCOS       = '#2E7D32'   # verde oscuro
    COLOR_EJE_MAY     = '#6A1B9A'   # púrpura (eje mayor / transverso)
    COLOR_EJE_MEN     = '#00838F'   # cian (eje menor / conjugado)
    COLOR_DIRECTRIZ   = '#AD1457'   # rosa oscuro
    COLOR_ASINTOTA    = '#795548'   # marrón

    def __init__(
        self,
        parent,
        coefficients: Dict[str, float],
        conic_type: str,
        canonical_data: Optional[Dict[str, Any]] = None,
        figsize: Tuple[int, int] = (6, 6)
    ) -> None:
        """
        Inicializa el renderer.

        Parámetros:
        - parent        : contenedor Tkinter donde se incrustará el canvas
        - coefficients  : {'A','B','C','D','E'} de la ecuación general
        - conic_type    : 'elipse' | 'hipérbola' | 'parábola' | 'circunferencia'
        - canonical_data: valores canónicos (h, k, a, b, p, r, axis, type, ...)
        - figsize       : tamaño de la figura Matplotlib
        """
        self.parent        = parent
        self.coefficients  = coefficients
        self.conic_type    = conic_type
        self.canonical_data = canonical_data or {}

        self.figure = Figure(figsize=figsize, dpi=100, facecolor='#FAFAFA')
        self.ax     = self.figure.add_subplot(111)
        self.canvas = None
        self._resize_job = None
        self._resize_bound = False

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def render(self) -> None:
        """Renderiza la cónica y la incrusta en el widget Tkinter padre."""
        self._limpiar_contenedor()
        self._configurar_ejes_base()

        tipo = self.conic_type
        if tipo == 'circunferencia':
            self._dibujar_circunferencia()
        elif tipo == 'elipse':
            self._dibujar_elipse()
        elif tipo == 'hipérbola':
            self._dibujar_hiperbola()
        elif tipo == 'parábola':
            self._dibujar_parabola()
        else:
            self._dibujar_mensaje(f"Tipo no reconocido: {tipo}")

        # Leyenda y estética final
        self.ax.legend(
            loc='upper right',
            fontsize=8,
            framealpha=0.85,
            edgecolor='#BDBDBD'
        )
        self.figure.tight_layout()
        self.ax.set_anchor('C')
        self.figure.subplots_adjust(left=0.10, right=0.96, top=0.93, bottom=0.10)

        # Incrustar en Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self._bind_resize_events()
        self._ajustar_figura_al_contenedor()

    def close(self) -> None:
        """Destruye el widget y libera la figura."""
        self._cancelar_resize_programado()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.figure.clf()

    # ------------------------------------------------------------------
    # Configuración de ejes
    # ------------------------------------------------------------------

    def _limpiar_contenedor(self) -> None:
        self._cancelar_resize_programado()
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)

    def _bind_resize_events(self) -> None:
        if self._resize_bound:
            return
        self.parent.bind('<Configure>', self._on_parent_resize)
        self._resize_bound = True

    def _on_parent_resize(self, event) -> None:
        if event.widget is not self.parent:
            return
        self._programar_ajuste_tamano()

    def _programar_ajuste_tamano(self) -> None:
        self._cancelar_resize_programado()
        if self.canvas is None:
            return
        self._resize_job = self.parent.after(60, self._ajustar_figura_al_contenedor)

    def _cancelar_resize_programado(self) -> None:
        if self._resize_job is not None:
            try:
                self.parent.after_cancel(self._resize_job)
            except Exception:
                pass
            self._resize_job = None

    def _ajustar_figura_al_contenedor(self) -> None:
        if self.canvas is None:
            return

        widget = self.canvas.get_tk_widget()
        width = widget.winfo_width()
        height = widget.winfo_height()

        if width <= 10 or height <= 10:
            width = max(self.parent.winfo_width() - 20, 320)
            height = max(self.parent.winfo_height() - 20, 280)

        dpi = self.figure.dpi
        self.figure.set_size_inches(max(width, 1) / dpi, max(height, 1) / dpi, forward=True)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def _configurar_ejes_base(self) -> None:
        """Aplica apariencia base; los límites se ajustan en cada _dibujar_*."""
        ax = self.ax
        ax.set_facecolor('#F8F9FA')
        ax.grid(True, linestyle='--', linewidth=0.5, color='#B0BEC5', alpha=0.7)
        ax.axhline(0, color='#546E7A', linewidth=0.8, zorder=1)
        ax.axvline(0, color='#546E7A', linewidth=0.8, zorder=1)
        ax.set_xlabel('x', fontsize=10)
        ax.set_ylabel('y', fontsize=10)
        # aspect='equal' se aplica DESPUÉS de calcular los límites dinámicos
        # para que matplotlib no distorsione la figura

    def _aplicar_limites(
        self,
        x_min: float, x_max: float,
        y_min: float, y_max: float
    ) -> None:
        """
        Aplica los límites calculados dinámicamente y fuerza aspect='equal'
        ampliando el rango más pequeño para que coincida.
        """
        ancho = x_max - x_min
        alto  = y_max - y_min

        if ancho <= 0 or alto <= 0:
            ancho = alto = 10.0

        # Igualar los rangos para no deformar (aspect equal manual)
        if ancho > alto:
            diff = (ancho - alto) / 2
            y_min -= diff
            y_max += diff
        elif alto > ancho:
            diff = (alto - ancho) / 2
            x_min -= diff
            x_max += diff

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_aspect('equal', adjustable='box')

    # ------------------------------------------------------------------
    # Helpers de dibujo
    # ------------------------------------------------------------------

    def _marcar_punto(
        self,
        x: float, y: float,
        color: str,
        marcador: str = 'o',
        tamaño: int = 8,
        label: Optional[str] = None,
        zorder: int = 5
    ) -> None:
        self.ax.plot(
            x, y,
            marker=marcador,
            color=color,
            markersize=tamaño,
            label=label,
            zorder=zorder,
            linestyle='None'
        )
        if label:
            # Texto con coordenadas junto al punto
            self.ax.annotate(
                f'({x:.3g}, {y:.3g})',
                xy=(x, y),
                xytext=(6, 6),
                textcoords='offset points',
                fontsize=7,
                color=color
            )

    def _dibujar_linea_segmento(
        self,
        x1: float, y1: float,
        x2: float, y2: float,
        color: str,
        estilo: str = '--',
        grosor: float = 1.2,
        label: Optional[str] = None
    ) -> None:
        self.ax.plot(
            [x1, x2], [y1, y2],
            color=color,
            linestyle=estilo,
            linewidth=grosor,
            label=label,
            zorder=3
        )

    def _dibujar_mensaje(self, mensaje: str) -> None:
        self.ax.text(
            0.5, 0.5, mensaje,
            ha='center', va='center',
            fontsize=12, color='red',
            transform=self.ax.transAxes
        )

    # ------------------------------------------------------------------
    # CIRCUNFERENCIA
    # ------------------------------------------------------------------

    def _dibujar_circunferencia(self) -> None:
        """
        Circunferencia: (x - h)² + (y - k)² = r²
        Método: patches.Circle con bounding-box exacta.
        Elementos: Centro, Radio (indicado en leyenda).
        """
        cd  = self.canonical_data
        h   = float(cd.get('h', 0))
        k   = float(cd.get('k', 0))
        r   = cd.get('r', None)

        if r is None or r <= 0:
            r = 5.0
        r = float(r)

        # --- Curva ---
        circulo = patches.Circle(
            (h, k), radius=r,
            fill=False,
            edgecolor=self.COLOR_CURVA,
            linewidth=2.5,
            zorder=4,
            label=f'Circunferencia r={r:.4g}'
        )
        self.ax.add_patch(circulo)

        # --- Centro ---
        self._marcar_punto(h, k, self.COLOR_CENTRO, 'o', 9,
                           label=f'Centro ({h:.4g}, {k:.4g})')

        # --- Ejes de simetría (horizontal y vertical por el centro) ---
        x_min, x_max, y_min, y_max = _calcular_rango_dinamico(h, k, r, r)
        self._dibujar_linea_segmento(
            h - r, k, h + r, k,
            self.COLOR_EJE_MAY, '--', 1.0,
            label='Eje horizontal'
        )
        self._dibujar_linea_segmento(
            h, k - r, h, k + r,
            self.COLOR_EJE_MEN, '--', 1.0,
            label='Eje vertical'
        )

        # --- Título ---
        self.ax.set_title(
            f'Circunferencia: $(x - {h:.4g})^2 + (y - {k:.4g})^2 = {r**2:.4g}$',
            fontsize=9, pad=8
        )

        # --- Límites dinámicos ---
        self._aplicar_limites(x_min, x_max, y_min, y_max)

    # ------------------------------------------------------------------
    # ELIPSE
    # ------------------------------------------------------------------

    def _dibujar_elipse(self) -> None:
        """
        Elipse: (x-h)²/a² + (y-k)²/b² = 1
        Método: patches.Ellipse con bounding-box exacta (h±a, k±b).
        Elementos: Centro, Vértices (4), Focos (2), Eje mayor, Eje menor.

        a = semieje en X,  b = semieje en Y  (según como venga de canonical_data)
        Si a > b → eje mayor horizontal;  si b > a → eje mayor vertical.
        """
        cd = self.canonical_data
        h  = float(cd.get('h', 0))
        k  = float(cd.get('k', 0))
        a  = _abs(float(cd.get('a', 5)))
        b  = _abs(float(cd.get('b', 3)))

        if a == 0:
            a = 1.0
        if b == 0:
            b = 1.0

        # Determinar orientación: cuál semieje es mayor
        # a_sq = a², b_sq = b² vienen de canonical_data; si existen, úsalos
        a_sq = cd.get('a_squared', a * a)
        b_sq = cd.get('b_squared', b * b)

        # Normalizar: a siempre = semieje horizontal, b = semieje vertical
        # (patches.Ellipse usa width=2a_x, height=2b_y)
        a_x = _sqrt(float(a_sq)) if float(a_sq) > 0 else a
        b_y = _sqrt(float(b_sq)) if float(b_sq) > 0 else b

        # --- Curva (Bounding Box exacta) ---
        elipse = patches.Ellipse(
            (h, k),
            width=2 * a_x,
            height=2 * b_y,
            fill=False,
            edgecolor=self.COLOR_CURVA,
            linewidth=2.5,
            zorder=4,
            label=f'Elipse'
        )
        self.ax.add_patch(elipse)

        # --- Centro ---
        self._marcar_punto(h, k, self.COLOR_CENTRO, 'o', 9,
                           label=f'Centro ({h:.4g}, {k:.4g})')

        # --- Vértices (extremos del semieje mayor y menor) ---
        self._marcar_punto(h + a_x, k, self.COLOR_VERTICES, 's', 7,
                           label=f'Vértice ({h+a_x:.4g}, {k:.4g})')
        self._marcar_punto(h - a_x, k, self.COLOR_VERTICES, 's', 7,
                           label=f'Vértice ({h-a_x:.4g}, {k:.4g})')
        self._marcar_punto(h, k + b_y, self.COLOR_VERTICES, 's', 7,
                           label=f'Vértice ({h:.4g}, {k+b_y:.4g})')
        self._marcar_punto(h, k - b_y, self.COLOR_VERTICES, 's', 7,
                           label=f'Vértice ({h:.4g}, {k-b_y:.4g})')

        # --- Focos ---
        # c² = |a_x² - b_y²|; focos en el eje mayor
        if a_x >= b_y:
            # eje mayor horizontal
            c = _sqrt(a_x * a_x - b_y * b_y)
            self._marcar_punto(h + c, k, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h+c:.4g}, {k:.4g})')
            self._marcar_punto(h - c, k, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h-c:.4g}, {k:.4g})')
        else:
            # eje mayor vertical
            c = _sqrt(b_y * b_y - a_x * a_x)
            self._marcar_punto(h, k + c, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h:.4g}, {k+c:.4g})')
            self._marcar_punto(h, k - c, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h:.4g}, {k-c:.4g})')

        # --- Ejes de simetría ---
        # Eje mayor (horizontal si a_x >= b_y, vertical si b_y > a_x)
        self._dibujar_linea_segmento(
            h - a_x, k, h + a_x, k,
            self.COLOR_EJE_MAY, '--', 1.2,
            label='Eje mayor' if a_x >= b_y else 'Eje menor'
        )
        self._dibujar_linea_segmento(
            h, k - b_y, h, k + b_y,
            self.COLOR_EJE_MEN, '--', 1.2,
            label='Eje menor' if a_x >= b_y else 'Eje mayor'
        )

        # --- Título ---
        self.ax.set_title(
            f'Elipse: $(x-{h:.4g})^2/{a_x**2:.4g} + (y-{k:.4g})^2/{b_y**2:.4g} = 1$',
            fontsize=9, pad=8
        )

        # --- Límites dinámicos ---
        radio_max = max(a_x, b_y)
        x_min, x_max, y_min, y_max = _calcular_rango_dinamico(h, k, a_x, b_y)
        self._aplicar_limites(x_min, x_max, y_min, y_max)

    # ------------------------------------------------------------------
    # HIPÉRBOLA
    # ------------------------------------------------------------------

    def _dibujar_hiperbola(self) -> None:
        """
        Hipérbola: (x-h)²/a² - (y-k)²/b² = 1  [horizontal]
                 o (y-k)²/a² - (x-h)²/b² = 1  [vertical]

        Método: parametrización hiperbólica mediante sinh/cosh aproximados
        con series de Taylor (sin usar math). Se usan 1000 puntos por rama.

        Elementos: Centro, Vértices (2), Focos (2), Ejes transverso y conjugado,
                   Asíntotas (2).
        """
        cd = self.canonical_data
        h  = float(cd.get('h', 0))
        k  = float(cd.get('k', 0))
        a  = _abs(float(cd.get('a', 4)))
        b  = _abs(float(cd.get('b', 3)))

        if a == 0:
            a = 1.0
        if b == 0:
            b = 1.0

        # Detectar orientación
        # canonical_data['type'] puede ser 'hipérbola_vertical' o 'hipérbola'
        # También se infiere de los coeficientes: A > 0, B < 0 → horizontal
        tipo_cd  = str(cd.get('type', ''))
        coef_A   = float(self.coefficients.get('A', 1))
        coef_B   = float(self.coefficients.get('B', -1))

        vertical = (
            'vertical' in tipo_cd or
            (coef_A < 0 and coef_B > 0)
        )

        # a_sq, b_sq desde canonical_data si están disponibles
        a_sq = cd.get('a_squared', a * a)
        b_sq = cd.get('b_squared', b * b)

        # Para hipérbola, a_squared puede ser positivo y b_squared negativo
        # (convención del módulo 6: a² = rhs/A, b² = rhs/B)
        # Normalizamos a siempre positivos
        a_real = _sqrt(_abs(float(a_sq))) if a_sq != 0 else a
        b_real = _sqrt(_abs(float(b_sq))) if b_sq != 0 else b

        if a_real == 0:
            a_real = a
        if b_real == 0:
            b_real = b

        # --- Generar puntos de las dos ramas usando parametrización ---
        # Hipérbola horizontal: x = h + a·cosh(t), y = k ± b·sinh(t)
        # Aproximamos cosh y sinh con la identidad:
        #   Para t en [t_min, t_max] discretizado, cosh(t) = (e^t + e^(-t))/2
        #   Usamos e^t nativo de Python
        n_puntos = 800
        t_max    = 3.0   # cosh(3) ≈ 10.07, suficiente para visualización

        t_vals = _linspace(-t_max, t_max, n_puntos)

        def _cosh(t):
            et = 2.718281828459045 ** t
            return (et + 1.0 / et) / 2.0

        def _sinh(t):
            et = 2.718281828459045 ** t
            return (et - 1.0 / et) / 2.0

        if not vertical:
            # Rama derecha: x = h + a·cosh(t), y = k + b·sinh(t)
            x_der = [h + a_real * _cosh(t) for t in t_vals]
            y_der = [k + b_real * _sinh(t) for t in t_vals]
            # Rama izquierda: x = h - a·cosh(t)
            x_izq = [h - a_real * _cosh(t) for t in t_vals]
            y_izq = [k + b_real * _sinh(t) for t in t_vals]
        else:
            # Hipérbola vertical: ramas arriba/abajo
            # y = k + a·cosh(t), x = h + b·sinh(t)  [rama superior]
            # y = k - a·cosh(t), x = h + b·sinh(t)  [rama inferior]
            x_der = [h + b_real * _sinh(t) for t in t_vals]
            y_der = [k + a_real * _cosh(t) for t in t_vals]
            x_izq = [h + b_real * _sinh(t) for t in t_vals]
            y_izq = [k - a_real * _cosh(t) for t in t_vals]

        # --- Dibujar las dos ramas ---
        label_hiper = ('Hipérbola (rama 1)', 'Hipérbola (rama 2)')
        self.ax.plot(x_der, y_der, color=self.COLOR_CURVA, linewidth=2.5,
                     label=label_hiper[0], zorder=4)
        self.ax.plot(x_izq, y_izq, color=self.COLOR_CURVA, linewidth=2.5,
                     label=label_hiper[1], zorder=4)

        # --- Centro ---
        self._marcar_punto(h, k, self.COLOR_CENTRO, 'o', 9,
                           label=f'Centro ({h:.4g}, {k:.4g})')

        # --- Vértices ---
        if not vertical:
            self._marcar_punto(h + a_real, k, self.COLOR_VERTICES, 's', 7,
                               label=f'Vértice ({h+a_real:.4g}, {k:.4g})')
            self._marcar_punto(h - a_real, k, self.COLOR_VERTICES, 's', 7,
                               label=f'Vértice ({h-a_real:.4g}, {k:.4g})')
        else:
            self._marcar_punto(h, k + a_real, self.COLOR_VERTICES, 's', 7,
                               label=f'Vértice ({h:.4g}, {k+a_real:.4g})')
            self._marcar_punto(h, k - a_real, self.COLOR_VERTICES, 's', 7,
                               label=f'Vértice ({h:.4g}, {k-a_real:.4g})')

        # --- Focos: c = sqrt(a² + b²) ---
        c = _sqrt(a_real * a_real + b_real * b_real)
        if not vertical:
            self._marcar_punto(h + c, k, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h+c:.4g}, {k:.4g})')
            self._marcar_punto(h - c, k, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h-c:.4g}, {k:.4g})')
        else:
            self._marcar_punto(h, k + c, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h:.4g}, {k+c:.4g})')
            self._marcar_punto(h, k - c, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h:.4g}, {k-c:.4g})')

        # --- Ejes de simetría ---
        extension = max(a_real, b_real, c) * 1.6
        if not vertical:
            # Eje transverso (horizontal)
            self._dibujar_linea_segmento(
                h - extension, k, h + extension, k,
                self.COLOR_EJE_MAY, '--', 1.2, 'Eje transverso (horizontal)'
            )
            # Eje conjugado (vertical)
            self._dibujar_linea_segmento(
                h, k - extension, h, k + extension,
                self.COLOR_EJE_MEN, '--', 1.2, 'Eje conjugado (vertical)'
            )
        else:
            self._dibujar_linea_segmento(
                h, k - extension, h, k + extension,
                self.COLOR_EJE_MAY, '--', 1.2, 'Eje transverso (vertical)'
            )
            self._dibujar_linea_segmento(
                h - extension, k, h + extension, k,
                self.COLOR_EJE_MEN, '--', 1.2, 'Eje conjugado (horizontal)'
            )

        # --- Asíntotas: y - k = ±(b/a)(x - h)  [horizontal]
        #               y - k = ±(a/b)(x - h)  [vertical] ---
        x_asint = _linspace(h - extension, h + extension, 300)
        if not vertical:
            pendiente = b_real / a_real
        else:
            pendiente = a_real / b_real

        y_asint_pos = [k + pendiente * (x - h) for x in x_asint]
        y_asint_neg = [k - pendiente * (x - h) for x in x_asint]

        self.ax.plot(x_asint, y_asint_pos,
                     color=self.COLOR_ASINTOTA, linestyle=':', linewidth=1.5,
                     label=f'Asíntota y={k:.3g}+{pendiente:.3g}(x-{h:.3g})',
                     zorder=2)
        self.ax.plot(x_asint, y_asint_neg,
                     color=self.COLOR_ASINTOTA, linestyle=':', linewidth=1.5,
                     label=f'Asíntota y={k:.3g}-{pendiente:.3g}(x-{h:.3g})',
                     zorder=2)

        # --- Título ---
        if not vertical:
            titulo = (f'Hipérbola: $(x-{h:.4g})^2/{a_real**2:.4g}'
                      f' - (y-{k:.4g})^2/{b_real**2:.4g} = 1$')
        else:
            titulo = (f'Hipérbola: $(y-{k:.4g})^2/{a_real**2:.4g}'
                      f' - (x-{h:.4g})^2/{b_real**2:.4g} = 1$')
        self.ax.set_title(titulo, fontsize=9, pad=8)

        # --- Límites dinámicos ---
        radio_x = max(a_real, c) if not vertical else max(b_real, c)
        radio_y = max(b_real, c) if not vertical else max(a_real, c)
        x_min, x_max, y_min, y_max = _calcular_rango_dinamico(
            h, k, radio_x, radio_y, margen_rel=0.40
        )
        self._aplicar_limites(x_min, x_max, y_min, y_max)

    # ------------------------------------------------------------------
    # PARÁBOLA
    # ------------------------------------------------------------------

    def _dibujar_parabola(self) -> None:
        """
        Parábola vertical:   (x - h)² = 4p(y - k)
        Parábola horizontal: (y - k)² = 4p(x - h)

        Elementos: Vértice, Foco (h, k+p) o (h+p, k), Directriz (y=k-p o x=h-p),
                   Eje de simetría.

        La curva se traza despejando la variable secundaria de la ecuación
        canónica (esto es exacto y sin raíces negativas):
            Vertical:   y = k + (x - h)² / (4p)   → siempre definida
            Horizontal: x = h + (y - k)² / (4p)   → siempre definida
        """
        cd          = self.canonical_data
        h           = float(cd.get('h', 0))
        k           = float(cd.get('k', 0))
        p           = cd.get('p', None)
        orientacion = str(cd.get('axis', ''))

        if p is None:
            p = 1.0
        p = float(p)

        # Detectar orientación desde coeficientes si no está en canonical_data
        coef_A = float(self.coefficients.get('A', 0))
        if not orientacion:
            orientacion = 'vertical' if coef_A != 0 else 'horizontal'

        # Radio de visualización adaptado a p
        radio_vis = max(_abs(p) * 6, 8.0)

        if orientacion == 'vertical':
            # y = k + (x-h)² / (4p)
            if _abs(p) < 1e-10:
                self._dibujar_mensaje("Parábola degenerada (p ≈ 0)")
                return

            x_vals = _linspace(h - radio_vis, h + radio_vis, 800)
            y_vals = [k + (x - h) ** 2 / (4.0 * p) for x in x_vals]

            self.ax.plot(x_vals, y_vals,
                         color=self.COLOR_CURVA, linewidth=2.5,
                         label='Parábola vertical', zorder=4)

            # Vértice
            self._marcar_punto(h, k, self.COLOR_VERTICES, 'D', 9,
                               label=f'Vértice ({h:.4g}, {k:.4g})')

            # Foco: (h, k + p)
            foco_y = k + p
            self._marcar_punto(h, foco_y, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({h:.4g}, {foco_y:.4g})')

            # Directriz: y = k - p
            dir_y = k - p
            x_dir_min = h - radio_vis * 0.9
            x_dir_max = h + radio_vis * 0.9
            self.ax.plot(
                [x_dir_min, x_dir_max], [dir_y, dir_y],
                color=self.COLOR_DIRECTRIZ, linestyle='--', linewidth=1.8,
                label=f'Directriz: y = {dir_y:.4g}', zorder=3
            )

            # Eje de simetría: x = h
            y_eje_min = min(k - _abs(p) * 1.5, dir_y - 1)
            y_eje_max = max(y_vals) + _abs(p)
            self._dibujar_linea_segmento(
                h, y_eje_min, h, y_eje_max,
                self.COLOR_EJE_MAY, '-.', 1.2,
                label=f'Eje de simetría: x = {h:.4g}'
            )

            # Título
            self.ax.set_title(
                f'Parábola: $(x-{h:.4g})^2 = {4*p:.4g}(y-{k:.4g})$',
                fontsize=9, pad=8
            )

            # Límites dinámicos
            y_extremo = k + radio_vis ** 2 / (4.0 * _abs(p))
            radio_y   = _abs(y_extremo - k) * 0.55
            x_min, x_max, y_min, y_max = _calcular_rango_dinamico(
                h, k + radio_y * 0.3, radio_vis * 0.9, radio_y
            )
            # Incluir directriz en el rango
            y_min = min(y_min, dir_y - 2)
            self._aplicar_limites(x_min, x_max, y_min, y_max)

        else:
            # Parábola horizontal: x = h + (y-k)² / (4p)
            if _abs(p) < 1e-10:
                self._dibujar_mensaje("Parábola degenerada (p ≈ 0)")
                return

            y_vals = _linspace(k - radio_vis, k + radio_vis, 800)
            x_vals = [h + (y - k) ** 2 / (4.0 * p) for y in y_vals]

            self.ax.plot(x_vals, y_vals,
                         color=self.COLOR_CURVA, linewidth=2.5,
                         label='Parábola horizontal', zorder=4)

            # Vértice
            self._marcar_punto(h, k, self.COLOR_VERTICES, 'D', 9,
                               label=f'Vértice ({h:.4g}, {k:.4g})')

            # Foco: (h + p, k)
            foco_x = h + p
            self._marcar_punto(foco_x, k, self.COLOR_FOCOS, '^', 8,
                               label=f'Foco ({foco_x:.4g}, {k:.4g})')

            # Directriz: x = h - p
            dir_x = h - p
            y_dir_min = k - radio_vis * 0.9
            y_dir_max = k + radio_vis * 0.9
            self.ax.plot(
                [dir_x, dir_x], [y_dir_min, y_dir_max],
                color=self.COLOR_DIRECTRIZ, linestyle='--', linewidth=1.8,
                label=f'Directriz: x = {dir_x:.4g}', zorder=3
            )

            # Eje de simetría: y = k
            x_eje_min = min(x_vals) - _abs(p)
            x_eje_max = max(x_vals) + _abs(p)
            self._dibujar_linea_segmento(
                x_eje_min, k, x_eje_max, k,
                self.COLOR_EJE_MAY, '-.', 1.2,
                label=f'Eje de simetría: y = {k:.4g}'
            )

            # Título
            self.ax.set_title(
                f'Parábola: $(y-{k:.4g})^2 = {4*p:.4g}(x-{h:.4g})$',
                fontsize=9, pad=8
            )

            # Límites dinámicos
            x_extremo = h + radio_vis ** 2 / (4.0 * _abs(p))
            radio_x   = _abs(x_extremo - h) * 0.55
            x_min, x_max, y_min, y_max = _calcular_rango_dinamico(
                h + radio_x * 0.3, k, radio_x, radio_vis * 0.9
            )
            # Incluir directriz en el rango
            x_min = min(x_min, dir_x - 2)
            self._aplicar_limites(x_min, x_max, y_min, y_max)
