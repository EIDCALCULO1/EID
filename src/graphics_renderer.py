"""
Módulo 8: Renderizado del Gráfico de Cónicas

Dibuja la cónica matemáticamente correcta a partir de los coeficientes
calculados y del tipo de cónica identificado.

SIN DEPENDENCIAS DE: numpy, scipy, sympy, pandas (solo matplotlib permitido)
"""

import math
from typing import Any, Dict, Optional, List

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches


class RenderizadorGraficosConicas:
    """Renderiza una cónica en un contenedor Tkinter usando Matplotlib.

    Esta clase encapsula la creación de una figura Matplotlib y su incrustación
    en un widget Tkinter (`FigureCanvasTkAgg`). Recibe los coeficientes de la
    ecuación general, el tipo de cónica y opcionalmente datos de la forma
    canónica para dibujar elementos geométricos (centro, focos, directriz).
    
    NOTA: Implementación pura en Python sin numpy/scipy/sympy/pandas.
    """

    def __init__(
        self,
        parent,
        coefficients: Dict[str, float],
        conic_type: str,
        canonical_data: Optional[Dict[str, Any]] = None,
        figsize=(6, 6)
    ) -> None:
        """Inicializa el renderer.

        Parámetros:
        - parent: contenedor Tkinter donde se incrustará el canvas
        - coefficients: diccionario {'A','B','C','D','E'} de la ecuación general
        - conic_type: tipo detectado ('elipse','hipérbola','parábola','circunferencia')
        - canonical_data: valores útiles para el dibujado (h,k,a,b,p,r, etc.)
        """

        self.parent = parent
        self.coefficients = coefficients
        self.conic_type = conic_type
        self.canonical_data = canonical_data or {}

        # Figura Matplotlib usada para el renderizado
        self.figure = Figure(figsize=figsize, dpi=100, facecolor="#ffffff")
        self.ax = self.figure.add_subplot(111)
        self.canvas = None

    @staticmethod
    def _linspace(start: float, stop: float, num: int) -> List[float]:
        """
        Genera una lista de números espaciados uniformemente (equivalente a np.linspace).
        
        Parámetros:
        - start: valor inicial
        - stop: valor final (incluido)
        - num: cantidad de puntos
        
        Retorna: lista de números espaciados uniformemente
        """
        if num <= 0:
            return []
        if num == 1:
            return [start]
        
        step = (stop - start) / (num - 1)
        return [start + i * step for i in range(num)]

    @staticmethod
    def _where(condition: List[bool], if_true: List[float], if_false: float = float('nan')) -> List[float]:
        """
        Equivalente a np.where - retorna valores según condición.
        
        Parámetros:
        - condition: lista de booleanos
        - if_true: lista de valores a retornar si condición es True
        - if_false: valor a retornar si condición es False (default NaN)
        
        Retorna: lista con valores seleccionados
        """
        result = []
        for i, cond in enumerate(condition):
            if cond:
                result.append(if_true[i] if i < len(if_true) else if_false)
            else:
                result.append(if_false)
        return result

    @staticmethod
    def _safe_sqrt(value: float) -> float:
        """
        Calcula raíz cuadrada de forma segura, retornando NaN si valor es negativo.
        
        Parámetros:
        - value: número a calcular raíz
        
        Retorna: raíz cuadrada o NaN
        """
        if value >= 0:
            return math.sqrt(value)
        else:
            return float('nan')

    def render(self) -> None:
        """Renderiza la cónica actual en el contenedor Tkinter.

        Se encarga de limpiar el contenedor previo, configurar los ejes y
        delegar al método de dibujo correspondiente según el tipo de cónica.
        """

        # Limpiar y preparar ejes
        self._clear_container()
        self._configure_axes()

        # Seleccionar rutina de dibujo según el tipo
        if self.conic_type == 'circunferencia':
            self._draw_circle()
        elif self.conic_type == 'elipse':
            self._draw_ellipse()
        elif self.conic_type == 'hipérbola':
            self._draw_hyperbola()
        elif self.conic_type == 'parábola':
            self._draw_parabola()
        else:
            self._draw_message(f"Tipo de cónica no reconocido: {self.conic_type}")

        # Incrustar figura en Tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _configure_axes(self) -> None:
        """Configura la apariencia básica de los ejes y límites de la figura."""

        self.ax.clear()
        self.ax.set_facecolor("#f7f7f7")
        self.ax.grid(True, linestyle='--', linewidth=0.5, color='#999999', alpha=0.6)
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        # Mantener aspecto igual para que las formas no se deformen
        self.ax.set_aspect('equal', adjustable='box')
        # Límites por defecto; se podrían adaptar dinámicamente
        self.ax.set_xlim(-15, 15)
        self.ax.set_ylim(-15, 15)

    def _clear_container(self) -> None:
        """Elimina widgets previos y restaura la figura para un nuevo dibujo."""

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        # Limpiar la figura y crear un nuevo axes
        self.figure.clf()
        self.ax = self.figure.add_subplot(111)

    def _draw_circle(self) -> None:
        """Dibuja una circunferencia usando los datos canónicos (h,k,r).

        Si `r` no está disponible, se usa un radio por defecto para que se muestre.
        """

        h = self.canonical_data.get('h', 0)
        k = self.canonical_data.get('k', 0)
        r = self.canonical_data.get('r', None)
        if r is None or r <= 0:
            # Valor por defecto garantizado para visualización
            r = 5

        circle = patches.Circle((h, k), radius=r, fill=False, edgecolor='#1f77b4', linewidth=2.5)
        self.ax.add_patch(circle)
        # Marcar el centro y leyenda
        self.ax.plot(h, k, 'ro', label=f'Centro ({h:.2f}, {k:.2f})')
        self.ax.set_title('Circunferencia')
        self.ax.legend()

    def _draw_ellipse(self) -> None:
        """Dibuja una elipse con semi-ejes `a` y `b` centrada en (h,k).

        Calcula la distancia focal `c` para marcar los focos (si es posible).
        """

        h = self.canonical_data.get('h', 0)
        k = self.canonical_data.get('k', 0)
        a = abs(self.canonical_data.get('a', 5))
        b = abs(self.canonical_data.get('b', 3))

        ellipse = patches.Ellipse((h, k), width=2*a, height=2*b, edgecolor='#ff7f0e', fill=False, linewidth=2.5)
        self.ax.add_patch(ellipse)
        self.ax.plot(h, k, 'ro', label=f'Centro ({h:.2f}, {k:.2f})')

        # Calcular c = sqrt(|a^2 - b^2|) para ubicar focos sobre el eje mayor
        if a > b:
            c = math.sqrt(max(0, a*a - b*b))
        else:
            c = math.sqrt(max(0, b*b - a*a))
        self.ax.plot([h + c, h - c], [k, k], 'go', label='Focos')
        self.ax.set_title('Elipse')
        self.ax.legend()

    def _draw_hyperbola(self) -> None:
        """Dibuja una hipérbola usando parámetros canónicos.

        La implementación trata dos orientaciones:
        - Hipérbola vertical: se parametriza en función de y
        - Hipérbola horizontal: se parametriza en función de x

        Implementación pura en Python sin numpy.
        """

        h = self.canonical_data.get('h', 0)
        k = self.canonical_data.get('k', 0)
        a = abs(self.canonical_data.get('a', 4))
        b = abs(self.canonical_data.get('b', 2))

        # Si se detecta orientación vertical, parametrizamos en y
        if self.canonical_data.get('type') == 'hipérbola_vertical' or (self.coefficients['A'] > 0 and self.coefficients['B'] < 0):
            # Generar valores de y
            y_values = self._linspace(-15, 15, 1200)
            
            # Calcular x para cada y: (y-k)^2/a^2 - 1 = (x-h)^2/b^2
            # Despejamos: (x-h)^2 = b^2 * ((y-k)^2/a^2 - 1)
            x_plus = []
            x_minus = []
            
            for y in y_values:
                inner = (y - k)**2 / (a**2) - 1
                if inner >= 0:
                    sqrt_val = math.sqrt(inner * b**2)
                    x_plus.append(h + sqrt_val)
                    x_minus.append(h - sqrt_val)
                else:
                    # Valor inválido (NaN), no se ploteará
                    x_plus.append(float('nan'))
                    x_minus.append(float('nan'))
            
            # Filtrar puntos NaN para graficación
            y_plot_plus = [y for y, x in zip(y_values, x_plus) if not math.isnan(x)]
            x_plot_plus = [x for x in x_plus if not math.isnan(x)]
            
            y_plot_minus = [y for y, x in zip(y_values, x_minus) if not math.isnan(x)]
            x_plot_minus = [x for x in x_minus if not math.isnan(x)]
            
            if x_plot_plus:
                self.ax.plot(x_plot_plus, y_plot_plus, color='#2ca02c', linewidth=2)
            if x_plot_minus:
                self.ax.plot(x_plot_minus, y_plot_minus, color='#2ca02c', linewidth=2)
        else:
            # Orientación horizontal: parametrizamos en x
            x_values = self._linspace(-15, 15, 1200)
            
            # Calcular y para cada x: (x-h)^2/a^2 - 1 = (y-k)^2/b^2
            # Despejamos: (y-k)^2 = b^2 * ((x-h)^2/a^2 - 1)
            y_plus = []
            y_minus = []
            
            for x in x_values:
                inner = (x - h)**2 / (a**2) - 1
                if inner >= 0:
                    sqrt_val = math.sqrt(inner * b**2)
                    y_plus.append(k + sqrt_val)
                    y_minus.append(k - sqrt_val)
                else:
                    y_plus.append(float('nan'))
                    y_minus.append(float('nan'))
            
            # Filtrar puntos NaN para graficación
            x_plot_plus = [x for x, y in zip(x_values, y_plus) if not math.isnan(y)]
            y_plot_plus = [y for y in y_plus if not math.isnan(y)]
            
            x_plot_minus = [x for x, y in zip(x_values, y_minus) if not math.isnan(y)]
            y_plot_minus = [y for y in y_minus if not math.isnan(y)]
            
            if x_plot_plus:
                self.ax.plot(x_plot_plus, y_plot_plus, color='#2ca02c', linewidth=2)
            if x_plot_minus:
                self.ax.plot(x_plot_minus, y_plot_minus, color='#2ca02c', linewidth=2)

        # Marcar centro y leyenda
        self.ax.plot(h, k, 'ro', label=f'Centro ({h:.2f}, {k:.2f})')
        self.ax.set_title('Hipérbola')
        self.ax.legend()

    def _draw_parabola(self) -> None:
        """Dibuja una parábola usando el parámetro focal `p`.

        Determina orientación en base a los coeficientes: si A==0 se asume
        parábola horizontal, en caso contrario vertical. Traza la directriz
        como una línea punteada para referencia.
        
        Implementación pura en Python sin numpy.
        """

        h = self.canonical_data.get('h', 0)
        k = self.canonical_data.get('k', 0)
        orientation = 'vertical'
        if self.coefficients['A'] == 0:
            orientation = 'horizontal'

        p = self.canonical_data.get('p', None)
        if p is None:
            # Valor por defecto razonable para visualización
            p = 1

        if orientation == 'vertical':
            # Parábola vertical: (x-h)^2 = 4p(y-k)
            # Despejamos: y = k + (x-h)^2 / (4p)
            x_values = self._linspace(h - 12, h + 12, 800)
            y_values = [k + ((x - h)**2) / (4 * p) for x in x_values]
            
            self.ax.plot(x_values, y_values, color='#d62728', linewidth=2)
            self.ax.plot(h, k, 'ro', label=f'Vértice ({h:.2f}, {k:.2f})')
            # Directriz y = k - p
            self.ax.axhline(k - p, color='#9467bd', linestyle='--', linewidth=1.5, label=f'Directriz y={k - p:.2f}')
        else:
            # Parábola horizontal: (y-k)^2 = 4p(x-h)
            # Despejamos: x = h + (y-k)^2 / (4p)
            y_values = self._linspace(k - 12, k + 12, 800)
            x_values = [h + ((y - k)**2) / (4 * p) for y in y_values]
            
            self.ax.plot(x_values, y_values, color='#d62728', linewidth=2)
            self.ax.plot(h, k, 'ro', label=f'Vértice ({h:.2f}, {k:.2f})')
            # Directriz x = h - p
            self.ax.axvline(h - p, color='#9467bd', linestyle='--', linewidth=1.5, label=f'Directriz x={h - p:.2f}')

        self.ax.set_title('Parábola')
        self.ax.legend()

    def _draw_message(self, message: str) -> None:
        """Muestra un mensaje centrado en la figura (por ejemplo errores)."""

        self.ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=12, color='red')

    def close(self) -> None:
        """Cierra y limpia la figura/canvas asociados a este renderer."""

        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        self.figure.clf()
