
import shlex
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

from graphviz import Digraph
from nltk import Tree
from espanol.gramatica_es import cargar, gramatica_v2, parsear


# ============================================
# COLORES DE LA INTERFAZ
# ============================================

FONDO = "#F3F6FB"
AZUL = "#172B4D"
TEXTO = "#26374B"

ESTILOS = {
    "oracion": ("#27476D", "#27476D", "#FFFFFF"),
    "nominal": ("#DCF4ED", "#39A88D", "#135E51"),
    "verbal": ("#E5EAFE", "#7A8BDD", "#334994"),
    "complemento": ("#FFF1D8", "#D7A04C", "#80561A"),
    "categoria": ("#EDF2F8", "#9BAEC5", "#3F5169"),
    "palabra": ("#E9F7EA", "#78B78D", "#255F3B"),
}


# ============================================
# SIGNIFICADOS DE LOS NODOS
# ============================================

SIGNIFICADOS = {
    "S": "Oración completa. Es la estructura principal del análisis.",
    "SN": "Sintagma nominal. Grupo cuyo núcleo es un sustantivo.",
    "SNobj": "Sintagma nominal que cumple la función de objeto del verbo.",
    "SV": "Sintagma verbal. Grupo organizado alrededor de un verbo.",
    "SP": "Sintagma preposicional. Grupo introducido por una preposición.",
    "Rel": "Cláusula relativa. Añade información sobre un sustantivo.",
    "Det": "Determinante. Acompaña al sustantivo: el, la, los, las...",
    "N": "Sustantivo. Nombra personas, animales, cosas o ideas.",
    "Adj": "Adjetivo. Describe una característica del sustantivo.",
    "PN": "Nombre propio, como Ana o Luis.",
    "V_t": "Verbo transitivo. Se combina con un objeto en esta gramática.",
    "V_i": "Verbo intransitivo. No exige objeto directo en esta gramática.",
    "V": "Verbo. Expresa una acción, proceso o estado.",
    "Prep": "Preposición. Introduce un complemento: con, en, de...",
    "Adv": "Adverbio. Modifica al verbo u otra expresión.",
}

RASGOS = {
    "ms": "masculino singular",
    "fs": "femenino singular",
    "mp": "masculino plural",
    "fp": "femenino plural",
    "s": "singular",
    "p": "plural",
}


# ============================================
# EXPLICAR EL SIGNIFICADO DE UN NODO
# ============================================

def explicar(etiqueta, es_arbol):

    if not es_arbol:
        return (
            "Palabra: " + etiqueta,
            "Es una palabra de la oración, al final de una rama del árbol."
        )

    base = etiqueta
    rasgo = ""

    for nombre in sorted(SIGNIFICADOS, key=len, reverse=True):

        if etiqueta == nombre:
            base = nombre
            break

        if etiqueta.startswith(nombre + "_"):
            base = nombre
            sufijo = etiqueta[len(nombre) + 1:]

            if sufijo in RASGOS:
                rasgo = " Rasgo: " + RASGOS[sufijo] + "."

            break

    return (
        etiqueta,
        SIGNIFICADOS.get(
            base, "Categoría de la gramática."
        ) + rasgo
    )


# ============================================
# IDENTIFICAR EL COLOR DE CADA NODO
# ============================================

def categoria(etiqueta, es_arbol):

    if not es_arbol:
        return "palabra"

    if etiqueta == "S":
        return "oracion"

    if etiqueta.startswith("SN") or etiqueta == "PN":
        return "nominal"

    if etiqueta.startswith("SV") or etiqueta.startswith("V_"):
        return "verbal"

    if (
        etiqueta == "SP"
        or etiqueta.startswith("Rel")
        or etiqueta == "Prep"
    ):
        return "complemento"

    return "categoria"


# ============================================
# INTERFAZ PRINCIPAL
# ============================================

class Aplicacion:

    def __init__(self, ventana):

        self.ventana = ventana

        ventana.title(
            "TEO | Visualizador de árboles sintácticos"
        )

        ventana.geometry("1230x780")
        ventana.minsize(840, 540)
        ventana.configure(bg=FONDO)

        # Utilizamos el parser existente
        self.gramatica = cargar(gramatica_v2(True))

        self.resultados = []
        self.indice = 0
        self.escala_manual = None

        self.tooltip = None
        self.rectangulos = {}
        self.activo = None

        self.crear_interfaz()

        ventana.after(150, self.analizar)

    # ========================================
    # ETIQUETAS Y BOTONES
    # ========================================

    def etiqueta(
        self, padre, contenido, tam=11,
        negrita=False, color=TEXTO,
        fondo=None, **otros
    ):

        return tk.Label(
            padre,
            text=contenido,
            fg=color,
            bg=fondo or padre.cget("bg"),
            font=(
                "Segoe UI",
                tam,
                "bold" if negrita else "normal"
            ),
            **otros
        )

    def boton(
        self, padre, contenido,
        comando, destacado=False
    ):

        return tk.Button(
            padre,
            text=contenido,
            command=comando,
            bg="#4263D6" if destacado else "#FFFFFF",
            fg="white" if destacado else AZUL,
            activebackground=(
                "#2E49AE" if destacado else "#E8EFF7"
            ),
            activeforeground=(
                "white" if destacado else AZUL
            ),
            relief="flat",
            bd=0,
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=9,
            cursor="hand2"
        )

    # ========================================
    # CONSTRUIR LA VENTANA
    # ========================================

    def crear_interfaz(self):

        encabezado = tk.Frame(
            self.ventana,
            bg=AZUL,
            padx=25,
            pady=18
        )

        encabezado.pack(fill="x")

        self.etiqueta(
            encabezado,
            "TEO  /  TEORÍA DE LENGUAJES",
            9, True, "#8EDBCF"
        ).pack(anchor="w")

        self.etiqueta(
            encabezado,
            "Laboratorio de árboles sintácticos",
            21, True, "white"
        ).pack(anchor="w", pady=(4, 0))

        self.etiqueta(
            encabezado,
            "Proyecto académico · Español · Gramática V3",
            10, color="#BED1E4"
        ).pack(anchor="w")

        # ENTRADA DE ORACIÓN

        entrada_marco = tk.Frame(
            self.ventana,
            bg="white",
            padx=18,
            pady=13
        )

        entrada_marco.pack(
            fill="x",
            padx=21,
            pady=(16, 10)
        )

        self.etiqueta(
            entrada_marco,
            "ESCRIBE UNA ORACIÓN",
            10, True
        ).pack(anchor="w")

        fila = tk.Frame(entrada_marco, bg="white")
        fila.pack(fill="x", pady=(8, 2))

        self.entrada = tk.Entry(
            fila,
            font=("Segoe UI", 12),
            bg="#F7F9FC",
            fg=TEXTO,
            relief="solid",
            bd=1
        )

        self.entrada.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9,
            padx=(0, 10)
        )

        self.entrada.insert(
            0,
            "el hombre ve la mujer con el telescopio"
        )

        self.entrada.bind(
            "<Return>",
            lambda _: self.analizar()
        )

        self.boton(
            fila,
            "Analizar  →",
            self.analizar,
            True
        ).pack(side="right")

        # BOTONES DE NAVEGACIÓN

        herramientas = tk.Frame(
            self.ventana,
            bg=FONDO,
            padx=21
        )

        herramientas.pack(
            fill="x",
            pady=(0, 8)
        )

        self.atras = self.boton(
            herramientas,
            "← Anterior",
            self.anterior
        )

        self.atras.pack(
            side="left",
            padx=(0, 8)
        )

        self.contador = self.etiqueta(
            herramientas,
            "Árbol 0 de 0",
            10, True
        )

        self.contador.pack(
            side="left",
            padx=6
        )

        self.adelante = self.boton(
            herramientas,
            "Siguiente →",
            self.siguiente
        )

        self.adelante.pack(
            side="left",
            padx=(8, 0)
        )

        self.boton(
            herramientas,
            "Guardar PNG",
            self.guardar
        ).pack(side="right")

        self.boton(
            herramientas,
            "Ajustar",
            self.ajustar
        ).pack(side="right", padx=5)

        self.boton(
            herramientas,
            "+",
            lambda: self.zoom(1.2)
        ).pack(side="right")

        self.porcentaje = self.etiqueta(
            herramientas,
            "100%",
            10, True
        )

        self.porcentaje.pack(
            side="right",
            padx=7
        )

        self.boton(
            herramientas,
            "−",
            lambda: self.zoom(1 / 1.2)
        ).pack(side="right")

        # ESTADO DEL ANÁLISIS

        self.estado = self.etiqueta(
            self.ventana,
            "Preparando análisis...",
            10,
            color="#64748B"
        )

        self.estado.pack(
            anchor="w",
            padx=25,
            pady=(0, 8)
        )

        # CONTENEDOR PRINCIPAL

        contenido = tk.Frame(
            self.ventana,
            bg=FONDO,
            padx=21
        )

        contenido.pack(
            fill="both",
            expand=True,
            pady=(0, 15)
        )

        area = tk.Frame(
            contenido,
            bg="white"
        )

        area.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            area,
            bg="white",
            highlightthickness=0
        )

        vertical = tk.Scrollbar(
            area,
            orient="vertical",
            command=self.canvas.yview
        )

        horizontal = tk.Scrollbar(
            area,
            orient="horizontal",
            command=self.canvas.xview
        )

        self.canvas.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        vertical.pack(side="right", fill="y")
        horizontal.pack(side="bottom", fill="x")

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas.bind(
            "<Configure>",
            lambda _: self.dibujar()
            if self.escala_manual is None
            and self.resultados else None
        )

        # PANEL DE EXPLICACIONES

        lateral = tk.Frame(
            contenido,
            bg="white",
            width=260,
            padx=16,
            pady=16
        )

        lateral.pack(
            side="right",
            fill="y",
            padx=(12, 0)
        )

        lateral.pack_propagate(False)

        self.etiqueta(
            lateral,
            "GUÍA INTERACTIVA",
            10, True, "#64748B"
        ).pack(anchor="w")

        self.etiqueta(
            lateral,
            "¿Qué significa?",
            14, True
        ).pack(
            anchor="w",
            pady=(10, 6)
        )

        self.etiqueta(
            lateral,
            "Pasa el cursor sobre cualquier nodo.",
            10,
            color="#64748B",
            wraplength=220,
            justify="left"
        ).pack(anchor="w")

        tk.Frame(
            lateral,
            height=1,
            bg="#DDE5EF"
        ).pack(fill="x", pady=15)

        self.titulo_detalle = self.etiqueta(
            lateral,
            "Selecciona un nodo",
            12, True,
            wraplength=220,
            justify="left"
        )

        self.titulo_detalle.pack(anchor="w")

        self.detalle = self.etiqueta(
            lateral,
            "Aquí aparecerá su explicación.",
            10,
            color="#64748B",
            wraplength=220,
            justify="left"
        )

        self.detalle.pack(
            anchor="w",
            pady=(7, 18)
        )

        # LEYENDA

        self.etiqueta(
            lateral,
            "LEYENDA DE COLORES",
            10, True,
            "#64748B"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        nombres = [
            ("oracion", "Oración"),
            ("nominal", "Sintagma nominal"),
            ("verbal", "Sintagma verbal"),
            ("complemento", "Complemento"),
            ("categoria", "Categoría"),
            ("palabra", "Palabra")
        ]

        for estilo, texto in nombres:

            linea = tk.Frame(
                lateral,
                bg="white"
            )

            linea.pack(
                anchor="w",
                pady=3
            )

            tk.Label(
                linea,
                text="    ",
                bg=ESTILOS[estilo][0],
                highlightbackground=ESTILOS[estilo][1],
                highlightthickness=1
            ).pack(
                side="left",
                padx=(0, 8)
            )

            self.etiqueta(
                linea,
                texto,
                10
            ).pack(side="left")

        self.actualizar_botones()

    # ========================================
    # ANALIZAR LA ORACIÓN
    # ========================================

    def analizar(self):

        frase = self.entrada.get().strip()

        if not frase:
            messagebox.showwarning(
                "Falta oración",
                "Escribe una oración."
            )
            return

        try:

            arboles = list(
                parsear(self.gramatica, frase)
            )

            nuevos = []

            for arbol in arboles:

                grafo = Digraph()

                grafo.attr(
                    rankdir="TB",
                    nodesep="0.40",
                    ranksep="0.62",
                    bgcolor="white"
                )

                grafo.attr(
                    "edge",
                    color="#A8B7CA",
                    dir="none"
                )

                datos = {}
                siguiente_id = [0]

                # CONSTRUIR NODOS DEL ÁRBOL

                def agregar(nodo, padre=None):

                    identificador = (
                        "n" + str(siguiente_id[0])
                    )

                    siguiente_id[0] += 1

                    es_arbol = isinstance(
                        nodo, Tree
                    )

                    nombre = (
                        str(nodo.label())
                        if es_arbol else str(nodo)
                    )

                    tipo = categoria(
                        nombre, es_arbol
                    )

                    fondo, borde, texto = (
                        ESTILOS[tipo]
                    )

                    titulo, descripcion = explicar(
                        nombre, es_arbol
                    )

                    datos[identificador] = (
                        nombre,
                        tipo,
                        titulo,
                        descripcion
                    )

                    grafo.node(
                        identificador,
                        nombre,
                        shape="box",
                        style="rounded,filled",
                        fillcolor=fondo,
                        color=borde,
                        fontcolor=texto,
                        fontname="Arial",
                        fontsize="12"
                    )

                    if padre is not None:
                        grafo.edge(
                            padre,
                            identificador
                        )

                    if es_arbol:
                        for hijo in nodo:
                            agregar(
                                hijo,
                                identificador
                            )

                agregar(arbol)

                # GRAPHVIZ CALCULA POSICIONES

                salida = grafo.pipe(
                    format="plain"
                ).decode("utf-8")

                nodos = {}
                aristas = []

                ancho = alto = 1.0

                for linea in salida.splitlines():

                    partes = shlex.split(linea)

                    if not partes:
                        continue

                    if partes[0] == "graph":
                        ancho = float(partes[2])
                        alto = float(partes[3])

                    elif partes[0] == "node":

                        nodos[partes[1]] = tuple(
                            map(float, partes[2:6])
                        )

                    elif partes[0] == "edge":

                        cantidad = int(partes[3])

                        aristas.append([
                            (
                                float(
                                    partes[4 + j * 2]
                                ),
                                float(
                                    partes[5 + j * 2]
                                )
                            )
                            for j in range(cantidad)
                        ])

                nuevos.append((
                    grafo,
                    datos,
                    ancho,
                    alto,
                    nodos,
                    aristas
                ))

        except Exception as error:
            messagebox.showerror(
                "Error al analizar",
                str(error)
            )
            return

        self.resultados = nuevos
        self.indice = 0
        self.escala_manual = None

        self.ocultar_ayuda()

        if nuevos:
            mensaje = (
                f"Análisis completado: {len(nuevos)} árbol(es). "
                "Pasa el cursor sobre los nodos."
            )
        else:
            mensaje = (
                "La gramática V3 no reconoce esta oración."
            )

        self.estado.config(text=mensaje)

        self.dibujar()

    # ========================================
    # DIBUJAR LOS ÁRBOLES
    # ========================================

    def dibujar(self):

        self.ocultar_ayuda()

        self.canvas.delete("all")
        self.rectangulos.clear()

        self.actualizar_botones()

        if not self.resultados:
            return

        (
            _,
            datos,
            ancho,
            alto,
            nodos,
            aristas
        ) = self.resultados[self.indice]

        w = max(
            self.canvas.winfo_width(),
            400
        )

        h = max(
            self.canvas.winfo_height(),
            250
        )

        ajuste = min(
            (w - 40) / ancho,
            (h - 40) / alto,
            120
        )

        escala = (
            ajuste
            if self.escala_manual is None
            else self.escala_manual
        )

        escala = max(12, escala)

        origen_x = max(
            20,
            (w - ancho * escala) / 2
        )

        origen_y = max(
            20,
            (h - alto * escala) / 2
        )

        def coordenada(x, y):

            return (
                origen_x + x * escala,
                origen_y + (alto - y) * escala
            )

        # DIBUJAR CONEXIONES

        for camino in aristas:

            puntos = []

            for x, y in camino:
                puntos.extend(
                    coordenada(x, y)
                )

            if len(puntos) >= 4:
                self.canvas.create_line(
                    *puntos,
                    smooth=True,
                    fill="#A8B7CA",
                    width=1.5
                )

        # DIBUJAR NODOS INTERACTIVOS

        for identificador, (
            x, y, ancho_n, alto_n
        ) in nodos.items():

            nombre, tipo, _, _ = (
                datos[identificador]
            )

            cx, cy = coordenada(x, y)

            rx = ancho_n * escala / 2
            ry = alto_n * escala / 2

            fondo, borde, texto = (
                ESTILOS[tipo]
            )

            etiqueta_tag = (
                "nodo_" + identificador
            )

            figura = self.canvas.create_rectangle(
                cx - rx,
                cy - ry,
                cx + rx,
                cy + ry,
                fill=fondo,
                outline=borde,
                width=1.6,
                tags=(etiqueta_tag,)
            )

            self.rectangulos[identificador] = (
                figura
            )

            self.canvas.create_text(
                cx,
                cy,
                text=nombre,
                fill=texto,
                font=(
                    "Segoe UI",
                    max(
                        7,
                        min(
                            14,
                            round(escala * 0.13)
                        )
                    ),
                    "bold"
                    if tipo == "oracion"
                    else "normal"
                ),
                tags=(etiqueta_tag,)
            )

            # EVENTOS DEL CURSOR

            self.canvas.tag_bind(
                etiqueta_tag,
                "<Enter>",
                lambda evento, n=identificador:
                self.mostrar_ayuda(evento, n)
            )

            self.canvas.tag_bind(
                etiqueta_tag,
                "<Motion>",
                self.mover_ayuda
            )

            self.canvas.tag_bind(
                etiqueta_tag,
                "<Leave>",
                lambda _: self.ocultar_ayuda()
            )

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                max(
                    w,
                    origen_x + ancho * escala + 20
                ),
                max(
                    h,
                    origen_y + alto * escala + 20
                )
            )
        )

        self.porcentaje.config(
            text=f"{round(escala / 96 * 100)}%"
        )

    # ========================================
    # MOSTRAR EXPLICACIÓN AL PASAR EL CURSOR
    # ========================================

    def mostrar_ayuda(
        self, evento, identificador
    ):

        self.ocultar_ayuda()

        self.activo = identificador

        _, datos, _, _, _, _ = (
            self.resultados[self.indice]
        )

        _, _, titulo, descripcion = (
            datos[identificador]
        )

        # ACTUALIZAR PANEL LATERAL

        self.titulo_detalle.config(
            text=titulo
        )

        self.detalle.config(
            text=descripcion
        )

        # RESALTAR NODO

        self.canvas.itemconfigure(
            self.rectangulos[identificador],
            width=3
        )

        # CREAR VENTANA EMERGENTE

        self.tooltip = tk.Toplevel(
            self.ventana
        )

        self.tooltip.overrideredirect(True)
        self.tooltip.attributes(
            "-topmost", True
        )

        tarjeta = tk.Frame(
            self.tooltip,
            bg="white",
            padx=12,
            pady=9,
            highlightbackground="#9BAEC5",
            highlightthickness=1
        )

        tarjeta.pack()

        self.etiqueta(
            tarjeta,
            titulo,
            10, True,
            AZUL
        ).pack(anchor="w")

        self.etiqueta(
            tarjeta,
            descripcion,
            9,
            color="#64748B",
            wraplength=270,
            justify="left"
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        self.mover_ayuda(evento)

    # ========================================
    # MOVER EXPLICACIÓN CON EL CURSOR
    # ========================================

    def mover_ayuda(self, evento):

        if (
            self.tooltip is not None
            and self.tooltip.winfo_exists()
        ):

            self.tooltip.update_idletasks()

            x = min(
                evento.x_root + 18,
                self.ventana.winfo_screenwidth()
                - self.tooltip.winfo_reqwidth()
                - 12
            )

            y = min(
                evento.y_root + 18,
                self.ventana.winfo_screenheight()
                - self.tooltip.winfo_reqheight()
                - 45
            )

            self.tooltip.geometry(
                f"+{max(0, x)}+{max(0, y)}"
            )

    # ========================================
    # OCULTAR EXPLICACIÓN
    # ========================================

    def ocultar_ayuda(self):

        if self.activo in self.rectangulos:

            self.canvas.itemconfigure(
                self.rectangulos[self.activo],
                width=1.6
            )

        self.activo = None

        if self.tooltip is not None:

            self.tooltip.destroy()
            self.tooltip = None

    # ========================================
    # ZOOM
    # ========================================

    def zoom(self, factor):

        if not self.resultados:
            return

        if self.escala_manual is None:

            _, _, ancho, alto, _, _ = (
                self.resultados[self.indice]
            )

            self.escala_manual = min(
                (
                    max(
                        400,
                        self.canvas.winfo_width()
                    ) - 40
                ) / ancho,
                (
                    max(
                        250,
                        self.canvas.winfo_height()
                    ) - 40
                ) / alto,
                120
            )

        self.escala_manual = max(
            18,
            min(
                230,
                self.escala_manual * factor
            )
        )

        self.dibujar()

    # ========================================
    # AJUSTAR A VENTANA
    # ========================================

    def ajustar(self):

        self.escala_manual = None
        self.dibujar()

    # ========================================
    # CAMBIAR ENTRE LOS ÁRBOLES
    # ========================================

    def anterior(self):

        if self.indice > 0:
            self.indice -= 1
            self.ajustar()

    def siguiente(self):

        if self.indice < len(self.resultados) - 1:
            self.indice += 1
            self.ajustar()

    def actualizar_botones(self):

        total = len(self.resultados)

        if total:
            self.contador.config(
                text=f"Árbol {self.indice + 1} de {total}"
            )
        else:
            self.contador.config(
                text="Árbol 0 de 0"
            )

        self.atras.config(
            state="normal"
            if self.indice > 0
            else "disabled"
        )

        self.adelante.config(
            state="normal"
            if self.indice < total - 1
            else "disabled"
        )

    # ========================================
    # GUARDAR ÁRBOL COMO IMAGEN
    # ========================================

    def guardar(self):

        if not self.resultados:
            messagebox.showinfo(
                "Sin árbol",
                "Primero analiza una oración."
            )
            return

        destino = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("Imagen PNG", "*.png")
            ],
            initialfile=f"arbol_{self.indice + 1}.png"
        )

        if destino:

            try:

                grafo = (
                    self.resultados[self.indice][0]
                )

                Path(destino).write_bytes(
                    grafo.pipe(format="png")
                )

                messagebox.showinfo(
                    "Guardado",
                    "Imagen guardada correctamente."
                )

            except Exception as error:

                messagebox.showerror(
                    "Error",
                    str(error)
                )


# ============================================
# INICIAR APLICACIÓN
# ============================================

if __name__ == "__main__":

    raiz = tk.Tk()
    app = Aplicacion(raiz)
    raiz.mainloop()
