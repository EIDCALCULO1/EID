"""
Módulo 7: Interfaz Gráfica (GUI) — CustomTkinter 5.x
======================================================
Interfaz rediseñada con CustomTkinter para el proyecto MAT1186 (UCT).

Layout de 3 columnas:
  ├─ Izquierda  : Ingreso de RUT + procedimiento paso a paso
  ├─ Centro     : Resumen de cónica + gráfico Matplotlib
  └─ Derecha    : Panel de Defensa Oral (6 CTkEntry VACÍOS)

RESTRICCIÓN CRÍTICA — Panel de Defensa:
Los campos CTkEntry del panel de defensa NUNCA se auto-rellenan
ni se precargan bajo ninguna condición. El estudiante debe
completarlos manualmente durante la exposición frente a la comisión.
"""

import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Any, Dict, Optional, List

# ── Apariencia global de CustomTkinter ────────────────────────────────────────
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── DPI awareness en Windows ──────────────────────────────────────────────────
if sys.platform.startswith('win'):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

from src.rut_validator import validar_rut, mostrar_procedimiento_validacion
from src.coefficient_engine import calcular_coeficientes, mostrar_procedimiento_coeficientes
from src.conic_classifier import obtener_reglas_clasificacion_conicas
from src.graphics_renderer import RenderizadorGraficosConicas
from src.limits_engine import PestanaFuncionesPorTramos


# ── Paleta de colores ─────────────────────────────────────────────────────────
_C = {
    'primary':       '#0D2137',   # azul marino oscuro (header, títulos)
    'primary_lt':    '#1565C0',   # azul royal (botón principal)
    'primary_hover': '#0D47A1',   # hover botón principal
    'bg':            '#EEF2F7',   # fondo general
    'card':          '#FFFFFF',   # fondo de paneles/tarjetas
    'card_inner':    '#F5F8FF',   # fondo secciones internas
    'border':        '#DDE3EC',   # bordes sutiles
    'text':          '#1A2B3C',   # texto principal
    'muted':         '#607D8B',   # texto secundario/placeholder
    'btn_neutral':   '#546E7A',   # botón secundario
    'btn_neutral_hv':'#37474F',   # hover botón secundario
    # Panel de defensa
    'def_header':    '#1A2F45',   # header del panel de defensa
    'def_accent':    '#E65100',   # color de alerta/advertencia
    'def_warn_bg':   '#FFF3E0',   # fondo advertencia
    'def_warn_brd':  '#FFA726',   # borde advertencia
    'def_field_bg':  '#F8FAFF',   # fondo de cada campo
    'def_field_brd': '#C5D3E8',   # borde de cada campo
    'def_entry_brd': '#90A4C8',   # borde CTkEntry
    'def_clear_btn': '#4A5568',   # botón limpiar defensa
    'def_clear_hv':  '#2D3748',   # hover limpiar
    'def_eval_btn':  '#1565C0',   # botón evaluar defensa
    'def_eval_hv':   '#0D47A1',   # hover evaluar
    'def_ok':        '#2E7D32',   # resultado correcto
    'def_bad':       '#C62828',   # resultado incorrecto
    'def_neutral':   '#90A4AE',   # estado neutro
}


class InterfazAnalisisConicas:
    """
    Interfaz gráfica principal para el sistema de análisis de cónicas.

    Ventana con 3 paneles laterales:
    - Izquierdo : entrada de RUT y procedimiento detallado
    - Central   : resumen de parámetros y gráfico de la cónica
    - Derecho   : panel de defensa oral con CTkEntry vacíos
    """

    def __init__(self, root: ctk.CTk) -> None:
        self.root = root
        self.root.title("Análisis de Cónicas desde RUT — MAT1186 UCT")
        self.root.geometry("1460x860")
        self.root.minsize(1100, 700)
        self.root.resizable(True, True)
        self.root.configure(fg_color=_C['bg'])

        # ── Estado interno ──
        self.renderer: Optional[RenderizadorGraficosConicas] = None
        self.current_result: Optional[Dict[str, Any]] = None

        # Referencia al label dinámico del campo 6 (Directriz / Asíntotas)
        self._label_dir_asin: Optional[ctk.CTkLabel] = None

        # Diccionario de CTkEntry del panel de defensa de cónicas
        # ⚠ NUNCA se escriben desde código: solo el estudiante los completa
        self._defense_entries: Dict[str, ctk.CTkEntry] = {}
        self._defense_status_label: Optional[ctk.CTkLabel] = None

        # Pestaña de funciones por tramos (se instancia en _build_main_area)
        self._pestana_limites: Optional[PestanaFuncionesPorTramos] = None

        self._build_ui()

    # ─────────────────────────────────────────────────────────────────────────
    # Construcción principal
    # ─────────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Ensambla el layout de 2 filas: header fijo + área principal."""
        self.root.grid_rowconfigure(0, weight=0, minsize=64)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_main_area()

    def _build_header(self) -> None:
        """Barra superior oscura con título y branding UCT."""
        hdr = ctk.CTkFrame(
            self.root,
            fg_color=_C['primary'],
            corner_radius=0,
            height=64
        )
        hdr.grid(row=0, column=0, sticky='nsew')
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(0, weight=1)
        hdr.grid_columnconfigure(1, weight=0)
        hdr.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text='  📐  Análisis de Cónicas desde RUT',
            font=ctk.CTkFont(family='Segoe UI', size=17, weight='bold'),
            text_color='#FFFFFF',
            anchor='w'
        ).grid(row=0, column=0, padx=22, sticky='w')

        ctk.CTkLabel(
            hdr,
            text='EID  ·  MAT1186  ·  Universidad Católica de Temuco',
            font=ctk.CTkFont(family='Segoe UI', size=11),
            text_color='#90CAF9',
            anchor='e'
        ).grid(row=0, column=1, padx=22, sticky='e')

    def _build_main_area(self) -> None:
        """
        Área principal: CTkTabview con 2 pestañas.
          Tab 1 '📐  Cónicas'              — panel existente de análisis de cónicas
          Tab 2 '📈  Funciones por Tramos' — módulo de límites laterales
        """
        tabview = ctk.CTkTabview(
            self.root,
            fg_color=_C['bg'],
            border_width=0,
            corner_radius=10,
            segmented_button_fg_color=_C['primary'],
            segmented_button_selected_color=_C['primary_lt'],
            segmented_button_selected_hover_color='#0D47A1',
            segmented_button_unselected_color=_C['primary'],
            segmented_button_unselected_hover_color='#1A3A5C',
            text_color='#FFFFFF',
            text_color_disabled='#90CAF9'
        )
        tabview.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))

        tabview.add('📐  Cónicas')
        tabview.add('📈  Funciones por Tramos')

        # ── Pestaña 1: Cónicas (contenido existente) ──
        self._build_conicas_tab(tabview.tab('📐  Cónicas'))

        # ── Pestaña 2: Funciones por Tramos (nuevo módulo) ──
        self._pestana_limites = PestanaFuncionesPorTramos(
            tabview.tab('📈  Funciones por Tramos')
        )

    def _build_conicas_tab(self, tab_frame: ctk.CTkFrame) -> None:
        """Construye el contenido de la pestaña de Cónicas (3 columnas)."""
        tab_frame.grid_rowconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(0, weight=0, minsize=370)
        tab_frame.grid_columnconfigure(1, weight=1, minsize=490)
        tab_frame.grid_columnconfigure(2, weight=0, minsize=340)

        left_card   = ctk.CTkFrame(tab_frame, fg_color=_C['card'], corner_radius=14)
        center_card = ctk.CTkFrame(tab_frame, fg_color=_C['card'], corner_radius=14)
        right_card  = ctk.CTkFrame(tab_frame, fg_color=_C['card'], corner_radius=14)

        left_card.grid  (row=0, column=0, sticky='nsew', padx=(14, 5), pady=14)
        center_card.grid(row=0, column=1, sticky='nsew', padx=5,       pady=14)
        right_card.grid (row=0, column=2, sticky='nsew', padx=(5, 14), pady=14)

        self._build_left_panel(left_card)
        self._build_center_panel(center_card)
        self._build_defense_panel(right_card)

    # ─────────────────────────────────────────────────────────────────────────
    # Panel izquierdo: RUT + procedimiento
    # ─────────────────────────────────────────────────────────────────────────

    def _build_left_panel(self, parent: ctk.CTkFrame) -> None:
        """Panel con entrada de RUT, botones y textbox de procedimiento."""
        # Título de sección
        ctk.CTkLabel(
            parent,
            text='Ingreso de RUT',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=_C['primary'],
            anchor='w'
        ).pack(fill='x', padx=18, pady=(18, 6))

        # ── Tarjeta de entrada ──
        inp = ctk.CTkFrame(
            parent,
            fg_color=_C['card_inner'],
            corner_radius=10,
            border_color=_C['border'],
            border_width=1
        )
        inp.pack(fill='x', padx=14, pady=(0, 8))

        ctk.CTkLabel(
            inp,
            text='Formato: XX.XXX.XXX-X',
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color=_C['muted'],
            anchor='w'
        ).pack(fill='x', padx=13, pady=(11, 3))

        self.rut_entry_widget = ctk.CTkEntry(
            inp,
            placeholder_text='Ej: 12.345.678-9',
            height=38,
            font=ctk.CTkFont(family='Consolas', size=13),
            border_color='#90CAF9',
            corner_radius=8
        )
        self.rut_entry_widget.pack(fill='x', padx=13, pady=(0, 9))
        self.rut_entry_widget.bind('<Return>', lambda e: self.on_process())

        # Botones en fila
        btn_row = ctk.CTkFrame(inp, fg_color='transparent')
        btn_row.pack(fill='x', padx=13, pady=(0, 13))

        ctk.CTkButton(
            btn_row,
            text='▶  Procesar RUT',
            command=self.on_process,
            height=36,
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'),
            fg_color=_C['primary_lt'],
            hover_color=_C['primary_hover'],
            corner_radius=8
        ).pack(side='left', expand=True, fill='x', padx=(0, 5))

        ctk.CTkButton(
            btn_row,
            text='✕  Limpiar',
            command=self.on_clear,
            height=36,
            font=ctk.CTkFont(family='Segoe UI', size=12),
            fg_color=_C['btn_neutral'],
            hover_color=_C['btn_neutral_hv'],
            corner_radius=8
        ).pack(side='left', expand=True, fill='x', padx=(5, 0))

        # Separador
        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(2, 8)
        )

        # Etiqueta del procedimiento
        ctk.CTkLabel(
            parent,
            text='Procedimiento paso a paso',
            font=ctk.CTkFont(family='Segoe UI', size=12, weight='bold'),
            text_color=_C['primary'],
            anchor='w'
        ).pack(fill='x', padx=18, pady=(0, 5))

        # Textbox scrollable
        self.text_widget = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family='Consolas', size=9),
            border_color=_C['border'],
            border_width=1,
            corner_radius=8,
            wrap='word',
            state='disabled',
            activate_scrollbars=True
        )
        self.text_widget.pack(fill='both', expand=True, padx=14, pady=(0, 14))

    # ─────────────────────────────────────────────────────────────────────────
    # Panel central: resumen + canvas Matplotlib
    # ─────────────────────────────────────────────────────────────────────────

    def _build_center_panel(self, parent: ctk.CTkFrame) -> None:
        """Panel central con tira de resumen y el canvas de la cónica."""
        # Título de sección
        ctk.CTkLabel(
            parent,
            text='Gráfico de la Cónica',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color=_C['primary'],
            anchor='w'
        ).pack(fill='x', padx=18, pady=(18, 6))

        # Tira de resumen (CTkTextbox compacto, no editable)
        self.summary_textbox = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family='Consolas', size=10),
            border_color=_C['border'],
            border_width=1,
            corner_radius=8,
            wrap='word',
            state='disabled',
            height=90,
            activate_scrollbars=False
        )
        self.summary_textbox.pack(fill='x', padx=14, pady=(0, 6))

        # Separador
        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(0, 6)
        )

        # ── Contenedor externo (visual CTkFrame) ──
        canvas_outer = ctk.CTkFrame(
            parent,
            fg_color='#F8F9FA',
            corner_radius=10,
            border_color=_C['border'],
            border_width=1
        )
        canvas_outer.pack(fill='both', expand=True, padx=14, pady=(0, 14))

        # ── Contenedor interno: tk.Frame puro para FigureCanvasTkAgg ──
        # Se usa tk.Frame aquí porque FigureCanvasTkAgg necesita un widget
        # tk estándar como master para embeberse correctamente.
        self.canvas_container = tk.Frame(canvas_outer, bg='#F8F9FA')
        self.canvas_container.pack(fill='both', expand=True, padx=2, pady=2)

        # Placeholder visible hasta que se cargue una cónica
        self._placeholder_label = ctk.CTkLabel(
            self.canvas_container,
            text='📈\n\nProcese un RUT para ver\nel gráfico de la cónica aquí',
            font=ctk.CTkFont(family='Segoe UI', size=13),
            text_color='#B0BEC5',
            justify='center',
            bg_color='#F8F9FA'
        )
        self._placeholder_label.place(relx=0.5, rely=0.5, anchor='center')

    # ─────────────────────────────────────────────────────────────────────────
    # Panel derecho: DEFENSA ORAL
    # ─────────────────────────────────────────────────────────────────────────

    def _build_defense_panel(self, parent: ctk.CTkFrame) -> None:
        """
        Panel lateral de Defensa Oral.

        Contiene 6 CTkEntry completamente vacíos que el estudiante debe
        completar manualmente durante la exposición frente a la comisión.

        ══════════════════════════════════════════════════════════════════
        RESTRICCIÓN ABSOLUTA: ningún método de esta clase escribe en estos
        campos. El único código que los toca es _limpiar_campos_defensa()
        (para borrarlos, no para precargarlos) y está invocado solo por
        el botón "Limpiar campos" que acciona el propio estudiante.
        ══════════════════════════════════════════════════════════════════
        """

        # ── Header oscuro del panel ──
        hdr = ctk.CTkFrame(
            parent,
            fg_color=_C['def_header'],
            corner_radius=10
        )
        hdr.pack(fill='x', padx=14, pady=(14, 8))

        ctk.CTkLabel(
            hdr,
            text='🎓  Panel de Defensa Oral',
            font=ctk.CTkFont(family='Segoe UI', size=13, weight='bold'),
            text_color='#FFFFFF',
            anchor='w'
        ).pack(fill='x', padx=14, pady=(12, 2))

        ctk.CTkLabel(
            hdr,
            text='Universidad Católica de Temuco  ·  MAT1186',
            font=ctk.CTkFont(family='Segoe UI', size=9),
            text_color='#90CAF9',
            anchor='w'
        ).pack(fill='x', padx=14, pady=(0, 12))

        # ── Caja de instrucción ──
        warn = ctk.CTkFrame(
            parent,
            fg_color=_C['def_warn_bg'],
            corner_radius=8,
            border_color=_C['def_warn_brd'],
            border_width=1
        )
        warn.pack(fill='x', padx=14, pady=(0, 10))

        ctk.CTkLabel(
            warn,
            text='⚠  Instrucción al estudiante',
            font=ctk.CTkFont(family='Segoe UI', size=10, weight='bold'),
            text_color=_C['def_accent'],
            anchor='w'
        ).pack(fill='x', padx=12, pady=(9, 2))

        ctk.CTkLabel(
            warn,
            text=(
                'Complete los siguientes campos durante\n'
                'la exposición oral para demostrar\n'
                'comprensión del procedimiento analítico.'
            ),
            font=ctk.CTkFont(family='Segoe UI', size=10),
            text_color='#BF360C',
            anchor='w',
            justify='left'
        ).pack(fill='x', padx=12, pady=(0, 9))

        # ── Separador ──
        ctk.CTkFrame(parent, height=1, fg_color=_C['border']).pack(
            fill='x', padx=14, pady=(0, 6)
        )

        # ── Área scrollable con los 6 campos ──
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color='transparent',
            scrollbar_button_color=_C['border'],
            scrollbar_button_hover_color='#BDBDBD',
            corner_radius=0
        )
        scroll.pack(fill='both', expand=True, padx=8, pady=(0, 4))

        # ── Definición de los 6 campos de defensa ──
        # Cada tupla: (clave_dict, icono+etiqueta, placeholder)
        CAMPOS_DEFENSA = [
            (
                'centro',
                '📍',
                'Centro (h, k)',
                'Ej: (h, k)'
            ),
            (
                'vertices',
                '◆',
                'Vértices',
                'Ej: (x₁, y₁)  y  (x₂, y₂)'
            ),
            (
                'focos',
                '✦',
                'Focos',
                'Ej: F₁(x₁, y₁)  y  F₂(x₂, y₂)'
            ),
            (
                'eje_mayor',
                '↔',
                'Long. Eje Mayor / Transverso',
                'Ej: 2a =  ...'
            ),
            (
                'eje_menor',
                '↕',
                'Long. Eje Menor / Conjugado',
                'Ej: 2b =  ...'
            ),
            (
                'dir_asin',
                '—',
                'Directriz / Asíntotas',   # <- texto dinámico, cambia con la cónica
                'Ej: y = k ± (b/a)(x − h)'
            ),
        ]

        for key, icono, etiqueta, placeholder in CAMPOS_DEFENSA:
            # Tarjeta individual de campo
            campo_card = ctk.CTkFrame(
                scroll,
                fg_color=_C['def_field_bg'],
                corner_radius=9,
                border_color=_C['def_field_brd'],
                border_width=1
            )
            campo_card.pack(fill='x', padx=4, pady=(0, 8))

            # Fila de encabezado del campo (icono + etiqueta)
            lbl_row = ctk.CTkFrame(campo_card, fg_color='transparent')
            lbl_row.pack(fill='x', padx=10, pady=(10, 4))

            ctk.CTkLabel(
                lbl_row,
                text=icono,
                font=ctk.CTkFont(family='Segoe UI', size=13),
                text_color=_C['primary_lt'],
                width=22,
                anchor='w'
            ).pack(side='left')

            lbl = ctk.CTkLabel(
                lbl_row,
                text=etiqueta,
                font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
                text_color=_C['primary'],
                anchor='w'
            )
            lbl.pack(side='left', fill='x', expand=True)

            # Guardar referencia al label del campo dir_asin para actualización dinámica
            if key == 'dir_asin':
                self._label_dir_asin = lbl

            # ─────────────────────────────────────────────────────────────
            # CTkEntry VACÍO
            # RESTRICCIÓN: este entry NUNCA es manipulado por código del
            # sistema. Queda siempre vacío hasta que el estudiante escriba.
            # ─────────────────────────────────────────────────────────────
            entry = ctk.CTkEntry(
                campo_card,
                placeholder_text=placeholder,
                height=36,
                font=ctk.CTkFont(family='Consolas', size=11),
                border_color=_C['def_entry_brd'],
                corner_radius=7,
                fg_color='#FFFFFF'
            )
            entry.pack(fill='x', padx=10, pady=(0, 10))

            # Almacenar referencia (solo para poder borrarlos con el botón manual)
            self._defense_entries[key] = entry

        # ── Botón para limpiar los campos de defensa (acción del estudiante) ──
        ctk.CTkButton(
            parent,
            text='✅   Evaluar defensa',
            command=self._evaluar_defensa,
            height=34,
            font=ctk.CTkFont(family='Segoe UI', size=11, weight='bold'),
            fg_color=_C['def_eval_btn'],
            hover_color=_C['def_eval_hv'],
            corner_radius=8
        ).pack(fill='x', padx=14, pady=(2, 8))

        ctk.CTkButton(
            parent,
            text='🗑   Limpiar campos de defensa',
            command=self._limpiar_campos_defensa,
            height=34,
            font=ctk.CTkFont(family='Segoe UI', size=11),
            fg_color=_C['def_clear_btn'],
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
    # Handlers de eventos
    # ─────────────────────────────────────────────────────────────────────────

    def on_process(self) -> None:
        """
        Handler del botón "Procesar RUT".
        Valida el RUT, calcula coeficientes, actualiza paneles de texto/resumen
        y renderiza el gráfico.

        NOTA: Este método NO toca ningún CTkEntry del panel de defensa.
        """
        rut = self.rut_entry_widget.get().strip()
        if not rut:
            messagebox.showwarning('RUT requerido', 'Ingrese un RUT en formato XX.XXX.XXX-X.')
            return

        validation = validar_rut(rut)
        if not validation['is_valid']:
            messagebox.showerror('RUT inválido', validation['error'])
            return

        digits = validation['digits']
        dv     = validation['dv']

        try:
            result = calcular_coeficientes(digits, dv)
        except Exception as exc:
            messagebox.showerror('Error de cálculo', f'No se pudo procesar:\n{exc}')
            return

        self.current_result = result

        # Actualizar paneles de información
        self._update_text_panel(rut, validation, result)
        self._update_summary_panel(result)
        self._render_conic(result)
        self._reset_defense_evaluation()

        # Actualizar SOLO el texto de la etiqueta del campo 6 (el entry sigue vacío)
        self._update_label_dir_asin(result.get('conic_type', ''))

        # Actualizar pestaña de Funciones por Tramos con los mismos dígitos
        # NOTA: los campos de defensa de esa pestaña tampoco se auto-rellenan
        if self._pestana_limites is not None:
            try:
                self._pestana_limites.actualizar(digits, dv)
            except Exception:
                pass  # No interrumpir el flujo de cónicas si el módulo falla

    def on_clear(self) -> None:
        """
        Handler del botón "Limpiar".
        Resetea el campo de RUT, el procedimiento, el resumen y el gráfico.

        NOTA: NO limpia los campos de defensa (eso es responsabilidad
        del estudiante usando el botón "Limpiar campos de defensa").
        """
        self.rut_entry_widget.delete(0, 'end')

        self.text_widget.configure(state='normal')
        self.text_widget.delete('1.0', 'end')
        self.text_widget.configure(state='disabled')

        self.summary_textbox.configure(state='normal')
        self.summary_textbox.delete('1.0', 'end')
        self.summary_textbox.configure(state='disabled')

        if self.renderer:
            self.renderer.close()
            self.renderer = None

        self._reset_defense_evaluation()

    def _limpiar_campos_defensa(self) -> None:
        """
        Limpia manualmente los 6 campos del panel de defensa.
        Solo se invoca desde el botón que acciona el propio estudiante.
        """
        for entry in self._defense_entries.values():
            entry.delete(0, 'end')

        self._reset_defense_evaluation()

    def _evaluar_defensa(self) -> None:
        """Evalúa los campos del panel de defensa contra el resultado actual."""
        if self.current_result is None:
            messagebox.showwarning(
                'Sin resultado',
                'Primero procese un RUT para generar la cónica y luego evalúe la defensa.'
            )
            return

        expectativas = self._construir_expectativas_defensa(self.current_result)
        correctos = 0
        evaluables = 0
        errores: List[str] = []

        for key, spec in expectativas.items():
            widget = self._defense_entries.get(key)
            if widget is None:
                continue

            evaluables += 1
            respuesta = widget.get().strip()
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
            widget.configure(border_color=_C['def_entry_brd'])

        if self._defense_status_label is not None:
            self._defense_status_label.configure(
                text='Pulsa “Evaluar defensa” para verificar cada campo.',
                text_color=_C['def_neutral']
            )

    def _construir_expectativas_defensa(self, result: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Construye las respuestas esperadas para la defensa oral."""
        canonical = result.get('canonical_transformation') or {}
        conic_type = str(result.get('conic_type', ''))

        h = float(canonical.get('h', 0) or 0)
        k = float(canonical.get('k', 0) or 0)

        if conic_type == 'circunferencia':
            r = float(canonical.get('r', 0) or 0)
            centro = self._formatear_punto(h, k)
            return {
                'centro': {'label': 'Centro', 'expected': centro, 'kind': 'point', 'tokens': [centro]},
                'vertices': {'label': 'Vértices', 'expected': f'{self._formatear_punto(h + r, k)} / {self._formatear_punto(h - r, k)}', 'kind': 'contains_all', 'tokens': [self._formatear_punto(h + r, k), self._formatear_punto(h - r, k)]},
                'focos': {'label': 'Focos', 'expected': f'{centro}', 'kind': 'text', 'tokens': [centro]},
                'eje_mayor': {'label': 'Long. Eje Mayor / Transverso', 'expected': self._formatear_numero(2 * r), 'kind': 'number', 'value': 2 * r},
                'eje_menor': {'label': 'Long. Eje Menor / Conjugado', 'expected': self._formatear_numero(2 * r), 'kind': 'number', 'value': 2 * r},
                'dir_asin': {'label': 'Directriz / Asíntotas', 'expected': 'No aplica', 'kind': 'na'},
            }

        if conic_type == 'elipse':
            a = abs(float(canonical.get('a', 0) or 0))
            b = abs(float(canonical.get('b', 0) or 0))
            eje_horizontal = a >= b
            a_mayor = max(a, b)
            b_menor = min(a, b)
            c = (a_mayor * a_mayor - b_menor * b_menor) ** 0.5

            if eje_horizontal:
                vertices = [self._formatear_punto(h + a_mayor, k), self._formatear_punto(h - a_mayor, k)]
                focos = [self._formatear_punto(h + c, k), self._formatear_punto(h - c, k)]
            else:
                vertices = [self._formatear_punto(h, k + a_mayor), self._formatear_punto(h, k - a_mayor)]
                focos = [self._formatear_punto(h, k + c), self._formatear_punto(h, k - c)]

            centro = self._formatear_punto(h, k)
            return {
                'centro': {'label': 'Centro', 'expected': centro, 'kind': 'point', 'tokens': [centro]},
                'vertices': {'label': 'Vértices', 'expected': ' / '.join(vertices), 'kind': 'contains_all', 'tokens': vertices},
                'focos': {'label': 'Focos', 'expected': ' / '.join(focos), 'kind': 'contains_all', 'tokens': focos},
                'eje_mayor': {'label': 'Long. Eje Mayor / Transverso', 'expected': self._formatear_numero(2 * a_mayor), 'kind': 'number', 'value': 2 * a_mayor},
                'eje_menor': {'label': 'Long. Eje Menor / Conjugado', 'expected': self._formatear_numero(2 * b_menor), 'kind': 'number', 'value': 2 * b_menor},
                'dir_asin': {'label': 'Directriz / Asíntotas', 'expected': 'No aplica', 'kind': 'na'},
            }

        if conic_type == 'hipérbola':
            a = abs(float(canonical.get('a', 0) or 0))
            b = abs(float(canonical.get('b', 0) or 0))
            vertical = float(result.get('A', 0) or 0) < 0 < float(result.get('B', 0) or 0)
            c = (a * a + b * b) ** 0.5
            if vertical:
                vertices = [self._formatear_punto(h, k + a), self._formatear_punto(h, k - a)]
                focos = [self._formatear_punto(h, k + c), self._formatear_punto(h, k - c)]
                asintotas = [f'y = {self._formatear_numero(k)} + {self._formatear_numero(a / b if b else 0)}(x - {self._formatear_numero(h)})', f'y = {self._formatear_numero(k)} - {self._formatear_numero(a / b if b else 0)}(x - {self._formatear_numero(h)})']
            else:
                vertices = [self._formatear_punto(h + a, k), self._formatear_punto(h - a, k)]
                focos = [self._formatear_punto(h + c, k), self._formatear_punto(h - c, k)]
                asintotas = [f'y = {self._formatear_numero(k)} + {self._formatear_numero(b / a if a else 0)}(x - {self._formatear_numero(h)})', f'y = {self._formatear_numero(k)} - {self._formatear_numero(b / a if a else 0)}(x - {self._formatear_numero(h)})']

            centro = self._formatear_punto(h, k)
            return {
                'centro': {'label': 'Centro', 'expected': centro, 'kind': 'point', 'tokens': [centro]},
                'vertices': {'label': 'Vértices', 'expected': ' / '.join(vertices), 'kind': 'contains_all', 'tokens': vertices},
                'focos': {'label': 'Focos', 'expected': ' / '.join(focos), 'kind': 'contains_all', 'tokens': focos},
                'eje_mayor': {'label': 'Long. Eje Mayor / Transverso', 'expected': self._formatear_numero(2 * a), 'kind': 'number', 'value': 2 * a},
                'eje_menor': {'label': 'Long. Eje Menor / Conjugado', 'expected': self._formatear_numero(2 * b), 'kind': 'number', 'value': 2 * b},
                'dir_asin': {'label': 'Directriz / Asíntotas', 'expected': ' / '.join(asintotas), 'kind': 'contains_all', 'tokens': asintotas},
            }

        if conic_type == 'parábola':
            p = float(canonical.get('p', 0) or 0)
            axis = str(canonical.get('axis', 'vertical'))
            if axis == 'vertical':
                foco = self._formatear_punto(h, k + p)
                directriz = f'y = {self._formatear_numero(k - p)}'
            else:
                foco = self._formatear_punto(h + p, k)
                directriz = f'x = {self._formatear_numero(h - p)}'

            vertex = self._formatear_punto(h, k)
            return {
                'centro': {'label': 'Vértice', 'expected': vertex, 'kind': 'point', 'tokens': [vertex]},
                'vertices': {'label': 'Vértice', 'expected': vertex, 'kind': 'point', 'tokens': [vertex]},
                'focos': {'label': 'Foco', 'expected': foco, 'kind': 'point', 'tokens': [foco]},
                'eje_mayor': {'label': 'Long. Eje Mayor / Transverso', 'expected': 'No aplica', 'kind': 'na'},
                'eje_menor': {'label': 'Long. Eje Menor / Conjugado', 'expected': 'No aplica', 'kind': 'na'},
                'dir_asin': {'label': 'Directriz', 'expected': directriz, 'kind': 'text', 'tokens': [directriz]},
            }

        return {}

    def _comparar_respuesta_defensa(self, respuesta: str, spec: Dict[str, Any]) -> bool:
        """Compara la respuesta escrita con la expectativa calculada."""
        tipo = spec.get('kind', 'text')
        respuesta_norm = self._normalizar_texto(respuesta)

        if tipo == 'na':
            return self._es_no_aplica(respuesta_norm)

        if tipo == 'number':
            esperado = self._formatear_numero(float(spec.get('value', 0)))
            return esperado in respuesta_norm

        tokens = [self._normalizar_texto(token) for token in spec.get('tokens', [])]
        if not tokens:
            return False

        if tipo == 'contains_all':
            return all(token in respuesta_norm for token in tokens)

        return any(token in respuesta_norm for token in tokens)

    def _normalizar_texto(self, texto: str) -> str:
        """Normaliza texto manual para una comparación tolerante."""
        texto = texto.lower().strip()
        reemplazos = {
            'á': 'a',
            'é': 'e',
            'í': 'i',
            'ó': 'o',
            'ú': 'u',
            'ü': 'u',
            'ñ': 'n',
            '−': '-',
            '–': '-',
            '×': 'x',
            '·': '',
            '√': '',
            ' ': '',
        }
        for origen, destino in reemplazos.items():
            texto = texto.replace(origen, destino)

        return ''.join(ch for ch in texto if ch.isalnum() or ch in '().,+-=<>:/')

    def _es_no_aplica(self, texto_norm: str) -> bool:
        """Verifica respuestas equivalentes a 'No aplica'."""
        return any(valor in texto_norm for valor in ('noaplica', 'n/a', 'na', 'noaplica'))

    def _formatear_numero(self, value: float) -> str:
        """Formatea números para validación de respuestas."""
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        texto = f'{value:.2f}'.rstrip('0').rstrip('.')
        return '0' if texto == '-0' else texto

    def _formatear_punto(self, x: float, y: float) -> str:
        """Formatea un punto cartesiano para comparación textual."""
        return f'({self._formatear_numero(x)}, {self._formatear_numero(y)})'

    def _update_label_dir_asin(self, conic_type: str) -> None:
        """
        Actualiza el texto de la ETIQUETA del campo Directriz/Asíntotas
        según el tipo de cónica identificado.

        El CTkEntry asociado permanece intacto (vacío).
        """
        if self._label_dir_asin is None:
            return

        mapa_etiqueta = {
            'parábola':       'Ecuación de la Directriz',
            'hipérbola':      'Ecuaciones de las Asíntotas',
            'elipse':         'Directriz  (no aplica — Elipse)',
            'circunferencia': 'Directriz / Asíntotas  (N/A)',
        }
        nuevo_texto = mapa_etiqueta.get(conic_type, 'Directriz / Asíntotas')
        self._label_dir_asin.configure(text=nuevo_texto)

    # ─────────────────────────────────────────────────────────────────────────
    # Actualización de paneles de texto
    # ─────────────────────────────────────────────────────────────────────────

    def _update_text_panel(
        self,
        rut: str,
        validation: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """Construye y vuelca el procedimiento paso a paso en el textbox izquierdo."""
        SEP = '═' * 48

        lines = []
        lines.append(SEP)
        lines.append('MÓDULO 1: Validación de RUT')
        lines.append(SEP)
        lines.append(f'RUT ingresado : {rut}')
        lines.append(f'RUT limpio    : {validation["rut_clean"]}')
        lines.append(f'Dígitos       : {", ".join(str(d) for d in validation["digits"])}')
        lines.append(f'DV            : {validation["dv"]}')
        lines.append('')
        proc_val = mostrar_procedimiento_validacion(rut) or '(sin procedimiento)'
        lines.append(proc_val)

        lines.append('')
        lines.append(SEP)
        lines.append('MÓDULO 2: Cálculo de coeficientes')
        lines.append(SEP)
        lines.append(mostrar_procedimiento_coeficientes(
            validation['digits'], validation['dv'], use_fractions=True
        ))

        lines.append('')
        lines.append(SEP)
        lines.append('MÓDULO 5: Desarrollo textual')
        lines.append(SEP)
        lines.append(result.get('explanation_fraction', '(no disponible)'))

        lines.append('')
        lines.append(SEP)
        lines.append('MÓDULO 3: Ajustes de cónicas')
        lines.append(SEP)
        adjs = result.get('adjustments', [])
        if adjs:
            for adj in adjs:
                lines.append(f'  • {adj}')
        else:
            lines.append('  (Sin ajustes aplicados)')

        lines.append('')
        lines.append(SEP)
        lines.append('MÓDULO 4: Clasificación geométrica')
        lines.append(SEP)
        lines.append(obtener_reglas_clasificacion_conicas())
        cls = result.get('conic_classification', {})
        lines.append(f'Tipo detectado : {cls.get("type", "—").upper()}')
        lines.append('')
        lines.append('Justificación:')
        lines.append(cls.get('justification', ''))

        lines.append('')
        lines.append(SEP)
        lines.append('MÓDULO 6: Transformación canónica')
        lines.append(SEP)
        canonical = result.get('canonical_transformation')
        if canonical and isinstance(canonical, dict) and canonical.get('procedure'):
            lines.append(canonical['procedure'])
        else:
            lines.append('(No disponible para este tipo de cónica)')

        self.text_widget.configure(state='normal')
        self.text_widget.delete('1.0', 'end')
        self.text_widget.insert('end', '\n'.join(lines))
        self.text_widget.configure(state='disabled')

    def _update_summary_panel(self, result: Dict[str, Any]) -> None:
        """Vuelca una tira compacta de parámetros en el textbox del panel central."""
        ctype     = result.get('conic_type', '—')
        canonical = result.get('canonical_transformation') or {}

        lines = []
        lines.append(
            f'Tipo: {ctype.upper():<18} '
            f'A={result.get("A","—")}  B={result.get("B","—")}  '
            f'C={result.get("C","—")}  D={result.get("D","—")}  E={result.get("E","—")}'
        )
        lines.append(f'Ec. General: {result.get("equation_fraction", "—")}')

        if canonical and isinstance(canonical, dict):
            if ctype == 'circunferencia':
                h = canonical.get('h', 0)
                k = canonical.get('k', 0)
                r2 = canonical.get('r_squared', '?')
                lines.append(f'Canónica : (x − {h})² + (y − {k})² = {r2}')
            elif ctype == 'elipse':
                h   = canonical.get('h', 0)
                k   = canonical.get('k', 0)
                a2  = canonical.get('a_squared', '?')
                b2  = canonical.get('b_squared', '?')
                lines.append(f'Canónica : (x − {h})²/{a2} + (y − {k})²/{b2} = 1')
            elif ctype == 'hipérbola':
                h  = canonical.get('h', 0)
                k  = canonical.get('k', 0)
                a2 = canonical.get('a_squared', '?')
                b2 = canonical.get('b_squared', '?')
                lines.append(f'Canónica : (x − {h})²/{a2} − (y − {k})²/{abs(b2) if b2 != "?" else "?"} = 1')
            elif ctype == 'parábola':
                h    = canonical.get('h', 0)
                k    = canonical.get('k', 0)
                p    = canonical.get('p', '?')
                axis = canonical.get('axis', '?')
                lines.append(f'Canónica : parábola {axis} — vértice ({h}, {k}), p = {p}')

        self.summary_textbox.configure(state='normal')
        self.summary_textbox.delete('1.0', 'end')
        self.summary_textbox.insert('end', '\n'.join(lines))
        self.summary_textbox.configure(state='disabled')

    # ─────────────────────────────────────────────────────────────────────────
    # Renderizado de la cónica
    # ─────────────────────────────────────────────────────────────────────────

    def _render_conic(self, result: Dict[str, Any]) -> None:
        """Crea el RenderizadorGraficosConicas y lo incrusta en canvas_container."""
        # Destruir renderer previo para evitar fugas de widgets
        if self.renderer:
            self.renderer.close()
            self.renderer = None

        # Ocultar placeholder una vez que hay gráfico
        if hasattr(self, '_placeholder_label'):
            self._placeholder_label.place_forget()

        conic_type   = result.get('conic_type', '')
        coefficients = {
            'A': result.get('A', 0),
            'B': result.get('B', 0),
            'C': result.get('C', 0),
            'D': result.get('D', 0),
            'E': result.get('E', 0),
        }
        canonical = result.get('canonical_transformation') or {}

        self.renderer = RenderizadorGraficosConicas(
            self.canvas_container,
            coefficients=coefficients,
            conic_type=conic_type,
            canonical_data=canonical
        )
        self.renderer.render()


# ─────────────────────────────────────────────────────────────────────────────
# Punto de entrada directo
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    root = ctk.CTk()
    app  = InterfazAnalisisConicas(root)
    root.mainloop()


if __name__ == '__main__':
    main()
