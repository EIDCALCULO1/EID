"""
Módulo 7: Interfaz Gráfica (GUI)

Provee una interfaz profesional para ingresar un RUT chileno, mostrar
el procedimiento completo de validación y cálculo, y renderizar la cónica.

Incluye campos vacíos para que el usuario complete durante la defensa:
Centro, Vértices, Focos, Ejes, Directriz.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from typing import Any, Dict, Optional

from src.rut_validator import validar_rut, mostrar_procedimiento_validacion
from src.coefficient_engine import calcular_coeficientes, mostrar_procedimiento_coeficientes
from src.conic_classifier import obtener_reglas_clasificacion_conicas
from src.graphics_renderer import RenderizadorGraficosConicas


class InterfazAnalisisConicas:
    """Interfaz gráfica principal para el sistema de cónicas."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Análisis de Cónicas desde RUT")
        
        # Configurar resizable ANTES de establecer geometry
        self.root.resizable(True, True)
        
        # Establecer tamaño inicial
        self.root.geometry("1320x900")
        
        # Establecer tamaño mínimo
        self.root.minsize(1100, 900)

        # Estilos y fuentes modernos
        self.style = ttk.Style(self.root)
        try:
            self.style.theme_use('clam')
        except Exception:
            pass
        self.font_heading = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.font_normal = tkfont.Font(family="Segoe UI", size=11)
        self.font_mono = tkfont.Font(family="Consolas", size=10)
        # Paleta de colores azul
        self.palette = {
            'primary': '#0b5fa5',   # encabezado
            'accent': '#2a9df4',    # acento botones
            'surface': '#eef6ff',   # fondo general
            'muted': '#4b6b88'      # texto secundario
        }
        # Estilo de botón acentuado
        self.style.configure('Accent.TButton', background=self.palette['accent'], foreground='white')
        self.style.map('Accent.TButton', background=[('active', self.palette['primary'])])

        self.renderer: Optional[RenderizadorGraficosConicas] = None
        self.current_result: Optional[Dict[str, Any]] = None

        self._build_interface()

    def _build_interface(self) -> None:

        """
        Construye la estructura principal de la ventana usando grid para control preciso del espacio:
        - Cabecera con título (fila 0) - FIJA
        - Área central scrollable con paneles y footer (fila 1)
        - Scrollbar global que afecta el contenido de body y footer
        
        Usa pesos de grid para que al redimensionar:
        - El header mantiene altura fija
        - El área scrollable dominan el crecimiento
        - Una única scrollbar global controla todo el contenido debajo del header
        """

        # Configurar grid en la ventana principal
        self.root.grid_rowconfigure(0, weight=0, minsize=70)  # header: altura fija 70px
        self.root.grid_rowconfigure(1, weight=1, minsize=600) # scrollable content: crece
        self.root.grid_columnconfigure(0, weight=1)

        # Fondo de la ventana principal
        self.root.configure(bg=self.palette['surface'])

        # HEADER: Cabecera con título
        header_frame = tk.Frame(self.root, bg=self.palette['primary'], height=70)
        header_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        header_frame.grid_propagate(False)

        tk.Label(
            header_frame,
            text="Interfaz Gráfica de Cónicas",
            bg=self.palette['primary'],
            fg="white",
            font=self.font_heading
        ).pack(padx=20, pady=14, anchor="w")

        # CANVAS SCROLLABLE: Contenedor principal para body y footer con scrollbar global
        scrollable_container = tk.Frame(self.root, bg="#f7f9fb")
        scrollable_container.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
        scrollable_container.grid_rowconfigure(0, weight=1)
        scrollable_container.grid_columnconfigure(0, weight=1)

        main_canvas = tk.Canvas(scrollable_container, bg="#f7f9fb", bd=0, highlightthickness=0)
        main_scrollbar = ttk.Scrollbar(scrollable_container, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#f7f9fb")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)

        main_canvas.grid(row=0, column=0, sticky="nsew")
        main_scrollbar.grid(row=0, column=1, sticky="ns")

        # Mapear rueda del mouse para scroll global
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # BODY: Área central con paneles izquierdo y derecho
        body_frame = tk.Frame(scrollable_frame, bg="#f7f9fb")
        body_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # Paned window para redimensionado intuitivo
        paned = tk.PanedWindow(body_frame, orient="horizontal", sashrelief="raised")
        paned.pack(fill="both", expand=True)

        left_panel = tk.Frame(paned, bg="#ffffff", bd=0)
        right_panel = tk.Frame(paned, bg="#ffffff", bd=0)
        paned.add(left_panel, minsize=420)
        paned.add(right_panel, minsize=560)

        self._build_left_panel(left_panel)
        self._build_right_panel(right_panel)

        # FOOTER: Parámetros geométricos e instrucciones (sin scrollbar local)
        footer_frame = tk.Frame(scrollable_frame, bg="#d3d3d3")
        footer_frame.pack(fill="both", expand=False, padx=0, pady=(12, 0))
        self._build_footer_panel(footer_frame)

    def _build_left_panel(self, parent: tk.Frame) -> None:
        """Construye el panel izquierdo con campos de entrada y el texto "paso a paso".

        Contiene:
        - Entrada de RUT y botones de procesar/limpiar
        - Widget de texto con scroll que muestra el procedimiento detallado
        """

        input_frame = ttk.Frame(parent, padding=(12, 12, 12, 6))
        input_frame.pack(fill="x")

        ttk.Label(
            input_frame,
            text="Ingrese RUT (formato: XX.XXX.XXX-X)",
            font=self.font_normal
        ).pack(anchor="w")

        entry_row = ttk.Frame(input_frame)
        entry_row.pack(fill="x", pady=8)

        self.rut_entry = ttk.Entry(entry_row, font=self.font_normal, width=22)
        self.rut_entry.pack(side="left", ipady=4)
        self.rut_entry.bind("<Return>", lambda event: self.on_process())

        process_button = ttk.Button(entry_row, text="Procesar RUT", command=self.on_process, style='Accent.TButton')
        process_button.pack(side="left", padx=8)

        clear_button = ttk.Button(entry_row, text="Limpiar", command=self.on_clear)
        clear_button.pack(side="left")

        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill="x", padx=8, pady=(6, 12))

        self.text_frame = ttk.Frame(parent, padding=(12, 8))
        self.text_frame.pack(fill="both", expand=True)

        text_label = ttk.Label(self.text_frame, text="Procedimiento paso a paso", font=self.font_normal)
        text_label.pack(anchor="w")

        text_container = ttk.Frame(self.text_frame)
        text_container.pack(fill="both", expand=True, pady=(8, 0))

        self.text_widget = tk.Text(
            text_container,
            wrap="word",
            bg="#ffffff",
            fg="#111111",
            font=self.font_mono,
            padx=8,
            pady=8,
            bd=0
        )
        self.text_widget.pack(side="left", fill="both", expand=True)
        self.text_widget.config(state="disabled")

        text_scroll = ttk.Scrollbar(text_container, orient="vertical", command=self.text_widget.yview)
        text_scroll.pack(side="right", fill="y")
        self.text_widget['yscrollcommand'] = text_scroll.set

    def _build_right_panel(self, parent: tk.Frame) -> None:
        """Construye el panel derecho que muestra el resumen y el gráfico de la cónica.

        El panel derecho contiene un resumen textual con scrollbar y un contenedor donde se
        inserta el `FigureCanvasTkAgg` devuelto por el renderer.
        """

        top_right = ttk.Frame(parent, padding=(12, 12))
        top_right.pack(fill="x")

        ttk.Label(top_right, text="Resumen de Cónica", font=self.font_normal).pack(anchor="w")

        # Contenedor para text widget con scrollbar
        summary_container = ttk.Frame(top_right)
        summary_container.pack(fill="both", expand=True, pady=(8, 6))

        self.summary_text = tk.Text(
            summary_container,
            wrap="word",
            bg="#ffffff",
            fg="#111111",
            font=self.font_normal,
            padx=8,
            pady=8,
            bd=0,
            height=8
        )
        self.summary_text.pack(side="left", fill="both", expand=True)
        self.summary_text.config(state="disabled")

        # Scrollbar para el resumen
        summary_scroll = ttk.Scrollbar(summary_container, orient="vertical", command=self.summary_text.yview)
        summary_scroll.pack(side="right", fill="y")
        self.summary_text['yscrollcommand'] = summary_scroll.set

        self.canvas_container = ttk.Frame(parent)
        self.canvas_container.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        placeholder = tk.Label(
            self.canvas_container,
            text="El gráfico de la cónica aparecerá aquí",
            font=self.font_normal,
            bg=self.palette['surface'],
            fg=self.palette['muted'],
            anchor="center",
            justify="center"
        )
        placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def _build_footer_panel(self, parent: tk.Frame) -> None:
        """Construye el footer con campos geométricos y las instrucciones de uso.

        Los campos del footer se usan durante la defensa para completar
        parámetros como centro, focos y directriz.
        
        Nota: El footer ahora es controlado por la scrollbar global,
        sin scrollbar local. El contenido se expande naturalmente.
        """

        # Configurar padding para el footer
        content_frame = tk.Frame(parent, bg="#d3d3d3")
        content_frame.pack(fill="both", expand=False, padx=12, pady=8)

        # Footer con dos columnas de contenido
        left_footer = ttk.Frame(content_frame)
        left_footer.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        right_footer = ttk.Frame(content_frame)
        right_footer.grid(row=0, column=1, sticky="nsew")

        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)

        ttk.Label(left_footer, text="Parámetros geométricos (complete)", font=self.font_normal).pack(anchor="w", pady=(0, 6))

        fields = [
            ("Centro", "center"),
            ("Vértices", "vertices"),
            ("Focos", "focos"),
            ("Ejes", "ejes"),
            ("Directriz", "directriz")
        ]

        self.footer_entries: Dict[str, tk.Entry] = {}
        for label, key in fields:
            frame = ttk.Frame(left_footer)
            frame.pack(fill="x", pady=4)
            ttk.Label(frame, text=f"{label}:", width=10).pack(side="left")
            entry = ttk.Entry(frame, width=36)
            entry.pack(side="left", padx=8)
            self.footer_entries[key] = entry

        ttk.Label(right_footer, text="Instrucciones de uso:", font=self.font_normal).pack(anchor="w", pady=(0, 6))

        instruction_text = (
            "1) Ingrese un RUT válido y presione Procesar.\n"
            "2) Revise el paso a paso y el resumen de la cónica.\n"
            "3) Use los campos vacíos para completar Centro, Vértices, Focos, Ejes y Directriz durante la defensa."
        )
        ttk.Label(right_footer, text=instruction_text, wraplength=420, justify="left").pack(anchor="w")

    def on_process(self) -> None:
        """Handler principal: procesa el RUT, calcula coeficientes y renderiza resultados.

        Flujo:
        1. Leer RUT desde la entrada y validar formato/algoritmo con `validate_rut`.
        2. Si es válido, calcular coeficientes con `calculate_coefficients`.
        3. Actualizar paneles de texto/resumen y renderizar la cónica.
        """

        # Leer y validar entrada
        rut = self.rut_entry.get().strip()
        if not rut:
            messagebox.showwarning("RUT requerido", "Ingrese un RUT en formato XX.XXX.XXX-X.")
            return

        validation = validar_rut(rut)
        if not validation['is_valid']:
            # Mostrar error amigable si la validación falla
            messagebox.showerror("RUT inválido", validation['error'])
            return

        # Extraer valores necesarios para el motor de coeficientes
        digits = validation['digits']
        dv = validation['dv']

        # Calcular coeficientes; capturar excepciones para mostrar feedback
        try:
            result = calcular_coeficientes(digits, dv)
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo calcular la cónica:\n{error}")
            return

        # Actualizar estado y vistas
        self.current_result = result
        self._update_text_panel(rut, validation, result)
        self._update_summary_panel(result)
        self._render_conic(result)

    def on_clear(self) -> None:
        """Limpia todos los campos y cierra cualquier renderer activo."""

        # Limpiar campos de entrada y widgets de texto
        self.rut_entry.delete(0, tk.END)
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state="disabled")
        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.config(state="disabled")
        for entry in self.footer_entries.values():
            entry.delete(0, tk.END)

        # Cerrar renderer para liberar recursos gráficos
        if self.renderer:
            self.renderer.close()
            self.renderer = None

    def _update_text_panel(self, rut: str, validation: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Rellena el widget de texto con el procedimiento paso a paso.

        Construye el contenido combinando los módulos de validación,
        cálculo de coeficientes, ajustes, clasificación y transformación canónica.
        """

        lines = []
        lines.append("MÓDULO 1: Validación de RUT")
        lines.append("RUT ingresado: " + rut)
        lines.append("RUT limpio: " + validation['rut_clean'])
        lines.append("Dígitos: " + ", ".join(str(d) for d in validation['digits']))
        lines.append("DV: " + validation['dv'])
        lines.append("\nProcedimiento de validación:")
        validation_text = mostrar_procedimiento_validacion(rut) or "No se pudo generar el procedimiento de validación."
        lines.append(validation_text)

        lines.append("\nMÓDULO 2: Cálculo de coeficientes")
        lines.append(mostrar_procedimiento_coeficientes(validation['digits'], validation['dv'], use_fractions=True))

        lines.append("\nMÓDULO 5: Generador de desarrollo textual")
        lines.append(result['explanation_fraction'])

        lines.append("\nMÓDULO 3: Reglas de ajuste")
        if result['adjustments']:
            lines.append("Ajustes aplicados:")
            for adj in result['adjustments']:
                lines.append("  - " + adj)
        else:
            lines.append("No se aplicaron ajustes de cónicas.")

        lines.append("\nMÓDULO 4: Clasificación de la cónica")
        lines.append(obtener_reglas_clasificacion_conicas())
        classification = result['conic_classification']
        lines.append(f"Tipo: {classification['type']}")
        lines.append("Justificación:")
        lines.append(classification['justification'])

        lines.append("\nMÓDULO 6: Transformación a forma canónica")
        canonical = result.get('canonical_transformation')
        if canonical and isinstance(canonical, dict) and canonical.get('procedure'):
            lines.append(canonical['procedure'])
        else:
            lines.append("No se pudo generar la transformación canónica.")

        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, "\n".join(lines))
        self.text_widget.config(state="disabled")

    def _update_summary_panel(self, result: Dict[str, Any]) -> None:
        """Actualiza el resumen de parámetros de la cónica mostrado a la derecha."""

        summary_lines = []
        summary_lines.append("Resumen de Parámetros de la Cónica")
        summary_lines.append("===============================")
        summary_lines.append(f"Tipo de cónica: {result['conic_type']}")
        summary_lines.append(f"A = {result['A']}")
        summary_lines.append(f"B = {result['B']}")
        summary_lines.append(f"C = {result['C']}")
        summary_lines.append(f"D = {result['D']}")
        summary_lines.append(f"E = {result['E']}")
        summary_lines.append("")
        summary_lines.append("Ecuación general:")
        summary_lines.append(result['equation_fraction'])

        canonical = result.get('canonical_transformation')
        if canonical and isinstance(canonical, dict):
            summary_lines.append("")
            summary_lines.append("Ecuación canónica aproximada:")
            if 'canonical_equation' in canonical:
                summary_lines.append(canonical['canonical_equation'])
            else:
                if canonical.get('type') == 'circunferencia':
                    summary_lines.append(f"(x - {canonical.get('h', 0)})² + (y - {canonical.get('k', 0)})² = {canonical.get('r_squared', '?')}")
                elif canonical.get('type') == 'elipse':
                    summary_lines.append(f"(x - {canonical.get('h', 0)})²/{canonical.get('a_squared', '?')} + (y - {canonical.get('k', 0)})²/{canonical.get('b_squared', '?')} = 1")
                elif canonical.get('type') == 'hipérbola':
                    summary_lines.append("Hipérbola en forma canónica")
                elif canonical.get('type') == 'parábola':
                    summary_lines.append("Parábola en forma canónica")

        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, "\n".join(summary_lines))
        self.summary_text.config(state="disabled")

    def _render_conic(self, result: Dict[str, Any]) -> None:
        """Inicializa y ejecuta el `ConicGraphicsRenderer` para dibujar la cónica.

        - Cierra el renderer anterior si existe para evitar fugas de widgets.
        - Pasa los coeficientes y los datos canónicos al renderer.
        """

        # Cerrar renderer previo
        if self.renderer:
            self.renderer.close()
            self.renderer = None

        # Preparar datos para el renderer
        conic_type = result['conic_type']
        coefficients = {
            'A': result['A'],
            'B': result['B'],
            'C': result['C'],
            'D': result['D'],
            'E': result['E']
        }
        canonical = result.get('canonical_transformation') or {}

        # Crear y renderizar
        self.renderer = RenderizadorGraficosConicas(
            self.canvas_container,
            coefficients=coefficients,
            conic_type=conic_type,
            canonical_data=canonical
        )
        self.renderer.render()


def main() -> None:
    root = tk.Tk()
    app = InterfazAnalisisConicas(root)
    root.mainloop()


if __name__ == "__main__":
    main()
