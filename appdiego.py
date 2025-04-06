import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import folium
import utm
import os
import sys
import webbrowser
import json
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
from datetime import datetime, timedelta
try:
    from tkinterhtml import HtmlFrame
except ImportError:
    HtmlFrame = None

# Función para asignar color según letra
def color_por_letra(letra):
    if not letra or not isinstance(letra, str):
        return "blue"  
    mapping = {
        "A": "red",
        "B": "blue",
        "C": "green",
        "D": "purple",
        "E": "orange",
        "F": "darkred",
        "G": "cadetblue",
        "H": "darkgreen",
        "I": "darkblue",
        "J": "lightred",
        "K": "beige",
        "L": "pink",
        "M": "lightblue",
        "N": "lightgreen",
        "O": "gray",
        "P": "black",
        "Q": "lightgray"
    }
    return mapping.get(letra.upper(), "blue")

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import csv
import os
import webbrowser
from datetime import datetime
import folium
# Asegúrate de que estas bibliotecas estén instaladas
# pip install folium
# pip install tkinterhtml (si se usa)

class MapaEditorApp:
    def __init__(self, root):
        self.root = root
        
        self.licencia_valida = self.verificar_licencia()
    
        if not self.licencia_valida:
            self.mostrar_ventana_licencia()
            if not self.licencia_valida:  # Si aún no es válida después de mostrar la ventana
                return
        
        self.mostrar_eula() 
        self.root.title("Editor de Coordenadas TXT a KML - Pro")
        self.datos = []
        self.letras = {}
        self.html_frame_available = HtmlFrame is not None
        self.mapa_frame = None
        self.current_theme = 'clam'
    
        # Configurar tamaño inicial y menú
        self.root.geometry("900x700")
        self.crear_menu()
    
        # Usar notebook (pestañas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)
    
        # Pestañas
        self.tab_principal = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_principal, text='Operaciones')
    
        self.tab_vista = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_vista, text='Vista de Datos')
    
        self.tab_mapa = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_mapa, text='Mapa')
    
        # Barra de estado (CREAR PRIMERO)
        self.status_bar = ttk.Label(root, text="Listo", relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
        # Variables para Tamaulipas (Zona 14N) (MOVIDAS DESPUÉS DE CREAR COMPONENTES)
        self.zona_utm = 14  # Zona UTM para Tamaulipas
        self.hemisferio = 'N'  # Hemisferio Norte
        self.rango_x = (200000, 800000)  # Rango aproximado Este
        self.rango_y = (3000000, 3500000)  # Rango aproximado Norte
    
        # Inicializar componentes
        self.crear_panel_archivos()
        self.crear_panel_edicion()
        self.crear_panel_exportacion()
        self.crear_tabla_datos()
        self.crear_panel_mapa()
    
        # Aplicar tema
        self.aplicar_tema(self.current_theme)
    
        #Ahora sí podemos actualizar la barra de estado
        self.actualizar_barra_estado()
        
        # Aplicar tema
        self.aplicar_tema(self.current_theme)
    
    def actualizar_barra_estado(self):
        """Actualiza la barra de estado con la zona UTM actual"""
        self.status_bar.config(
            text=f"Zona UTM: {self.zona_utm}{self.hemisferio} | Puntos: {len(self.datos)} | Listo"
        )
        
    def crear_menu(self):
        menubar = tk.Menu(self.root)
    
    # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar TXT", command=self.cargar_archivo)
        file_menu.add_command(label="Guardar sesión", command=self.guardar_sesion)
        file_menu.add_command(label="Cargar sesión", command=self.cargar_sesion)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
    
    # Menú Edición
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Editar puntos", command=self.editar_puntos)
        edit_menu.add_command(label="Asignar grupo", command=self.asignar_nombres)
        edit_menu.add_command(label="Buscar/Filtrar", command=self.buscar_filtrar)
        menubar.add_cascade(label="Edición", menu=edit_menu)
    
    # Menú Exportar
        export_menu = tk.Menu(menubar, tearoff=0)
        export_menu.add_command(label="Exportar a KML", command=self.guardar_kml)
        export_menu.add_command(label="Exportar a CSV", command=self.exportar_csv)
        export_menu.add_command(label="Exportar a GeoJSON", command=self.exportar_geojson)
        menubar.add_cascade(label="Exportar", menu=export_menu)
    
    # Menú Visualización
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Mostrar mapa externo", command=self.mostrar_mapa)
        view_menu.add_command(label="Mostrar vista previa", command=self.mostrar_vista_previa_mapa)
        view_menu.add_command(label="Abrir en Google Maps", command=self.abrir_en_google_maps)
        view_menu.add_separator()
        menubar.add_cascade(label="Visualización", menu=view_menu)

    # Asignar el menú a la ventana principal
        self.root.config(menu=menubar)

        
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme in ['clam', 'alt', 'default', 'classic']:
            theme_menu.add_command(
                label=theme.capitalize(), 
                command=lambda t=theme: self.aplicar_tema(t)
            )
        view_menu.add_cascade(label="Temas", menu=theme_menu)
        menubar.add_cascade(label="Visualización", menu=view_menu)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Ver Licencia", command=self.mostrar_eula)
        help_menu.add_command(label="Ayuda", command=self.mostrar_ayuda)
        help_menu.add_command(label="Acerca de", command=self.mostrar_acerca_de)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def crear_panel_archivos(self):
        frame = ttk.LabelFrame(self.tab_principal, text="Archivos", padding=10)
        frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame, text="Cargar TXT/CSV", command=self.cargar_archivo).pack(side='left', padx=2)
        ttk.Button(frame, text="Guardar sesión", command=self.guardar_sesion).pack(side='left', padx=2)
        ttk.Button(frame, text="Cargar sesión", command=self.cargar_sesion).pack(side='left', padx=2)
        
        # Estadísticas
        self.label_estadisticas = ttk.Label(frame, text="Puntos: 0 | Sin nombre: 0")
        self.label_estadisticas.pack(side='right', padx=10)
    
    def crear_panel_edicion(self):
        frame = ttk.LabelFrame(self.tab_principal, text="Edición", padding=10)
        frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame, text="Editar nombres", command=self.editar_puntos).pack(side='left', padx=2)
        ttk.Button(frame, text="Asignar grupo", command=self.asignar_nombres).pack(side='left', padx=2)
        ttk.Button(frame, text="Buscar/Filtrar", command=self.buscar_filtrar).pack(side='left', padx=2)
        ttk.Button(frame, text="Estadísticas", command=self.ver_estadisticas).pack(side='left', padx=2)
    
    def crear_panel_exportacion(self):
        frame = ttk.LabelFrame(self.tab_principal, text="Exportación", padding=10)
        frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(frame, text="Exportar a KML", command=self.guardar_kml).pack(side='left', padx=2)
        ttk.Button(frame, text="Exportar a CSV", command=self.exportar_csv).pack(side='left', padx=2)
        ttk.Button(frame, text="Exportar a GeoJSON", command=self.exportar_geojson).pack(side='left', padx=2)
        ttk.Button(frame, text="Abrir en QGIS", command=self.abrir_en_qgis).pack(side='left', padx=2)
    
    def crear_tabla_datos(self):
        frame = ttk.Frame(self.tab_vista)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Scrollbars
        yscroll = ttk.Scrollbar(frame, orient='vertical')
        xscroll = ttk.Scrollbar(frame, orient='horizontal')
        
        # Treeview
        self.tree = ttk.Treeview(
            frame,
            columns=('ID', 'X', 'Y', 'Z', 'Lat', 'Lon', 'Texto', 'Grupo'),
            yscrollcommand=yscroll.set,
            xscrollcommand=xscroll.set,
            selectmode='extended'
        )
        
        # Configurar columnas
        self.tree.heading('#0', text='#')
        self.tree.column('#0', width=40, stretch=False)
        
        columns = {
            'ID': {'width': 80, 'anchor': 'w'},
            'X': {'width': 100, 'anchor': 'e'},
            'Y': {'width': 100, 'anchor': 'e'},
            'Z': {'width': 80, 'anchor': 'e'},
            'Lat': {'width': 120, 'anchor': 'e'},
            'Lon': {'width': 120, 'anchor': 'e'},
            'Texto': {'width': 200, 'anchor': 'w'},
            'Grupo': {'width': 80, 'anchor': 'center'}
        }


        
        for col, config in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **config)
        
        # Empacar
        yscroll.config(command=self.tree.yview)
        xscroll.config(command=self.tree.xview)
        
        self.tree.pack(side='left', fill='both', expand=True)
        yscroll.pack(side='right', fill='y')
        xscroll.pack(side='bottom', fill='x')
        
        # Bindings
        self.tree.bind('<Double-1>', self.editar_celda_tabla)
        
        # Botones de acción
        btn_frame = ttk.Frame(self.tab_vista)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Actualizar", command=self.actualizar_tabla_datos).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Exportar selección", command=self.exportar_seleccion).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Eliminar selección", command=self.eliminar_seleccion).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Copiar selección", command=self.copiar_seleccion).pack(side='left', padx=2)


    def editar_celda_tabla(self, event):
        """Permite editar celdas en la tabla principal con doble clic"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        col = self.tree.identify_column(event.x)
        item = self.tree.focus()
    
        if col == '#7':  # Columna de Texto
            x, y, width, height = self.tree.bbox(item, col)
            valor_actual = self.tree.item(item, 'values')[6]  # Índice 6 para Texto
        
            entry = ttk.Entry(self.tree)
            entry.place(x=x, y=y, width=width, height=height)
            entry.insert(0, valor_actual)
            entry.select_range(0, tk.END)
            entry.focus_set()
        
        def guardar_edit(event=None):
            nuevo_valor = entry.get()
            current_values = list(self.tree.item(item, 'values'))
            current_values[6] = nuevo_valor
            self.tree.item(item, values=current_values)
            
            # Actualizar los datos
            idx = int(item)
            self.datos[idx]['texto'] = nuevo_valor
            entry.destroy()
            
        entry.bind('<Return>', guardar_edit)
        entry.bind('<FocusOut>', lambda e: entry.destroy())
    
    def copiar_seleccion(self):
        """Copia los puntos seleccionados al portapapeles"""
        seleccionados = self.tree.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "No hay puntos seleccionados para copiar")
            return
    
        try:
            texto_copiado = ""
            for item in seleccionados:
                valores = self.tree.item(item, 'values')
                texto_copiado += "\t".join(str(v) for v in valores) + "\n"
        
            self.root.clipboard_clear()
            self.root.clipboard_append(texto_copiado)
            self.status_bar.config(text=f"Copiados {len(seleccionados)} puntos al portapapeles")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron copiar los puntos:\n{str(e)}")
            self.status_bar.config(text="Error al copiar puntos")


    def eliminar_seleccion(self):
        """Elimina los puntos seleccionados de la tabla y los datos"""
        seleccionados = self.tree.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "No hay puntos seleccionados para eliminar")
            return
    
        # Confirmar eliminación
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar {len(seleccionados)} punto(s) seleccionado(s)?"
        ):
            return
    
        try:
            # Eliminar en orden inverso para evitar problemas con los índices
            for item in reversed(seleccionados):
                idx = int(item)
                # Eliminar de los datos principales
                del self.datos[idx]
                # Eliminar de la tabla
                self.tree.delete(item)
        
            # Reconstruir el diccionario de letras
            self.letras = {}
            for punto in self.datos:
                if punto['texto'] and '-' in punto['texto']:
                    letra = punto['texto'].split('-')[-1][0].upper()
                    if letra.isalpha():
                        self.letras.setdefault(letra, []).append(punto['id'])
        
            self.actualizar_estadisticas()
            self.status_bar.config(text=f"Eliminados {len(seleccionados)} puntos")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron eliminar los puntos:\n{str(e)}")
            self.status_bar.config(text="Error al eliminar puntos")


        
    def actualizar_tabla_datos(self):

    # Limpiar tabla existente
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    # Llenar con nuevos datos
        for i, punto in enumerate(self.datos):
            self.tree.insert('', 'end', iid=str(i), values=(
                punto['id'],
                f"{punto['x']:.2f}",
                f"{punto['y']:.2f}",
                f"{punto['alt']:.2f}",
                f"{punto['lat']:.6f}",
                f"{punto['lon']:.6f}",
                punto['texto'],
                self.obtener_letra_punto(punto))
            )
    def crear_panel_mapa(self):
        if not self.html_frame_available:
            label = ttk.Label(
                self.tab_mapa, 
                text="Para la vista previa del mapa, instale tkinterhtml:\npip install tkinterhtml",
                justify='center'
            )
            label.pack(fill='both', expand=True)
        else:
            self.mapa_frame = HtmlFrame(self.tab_mapa)
            self.mapa_frame.pack(fill='both', expand=True)
    
        btn_frame = ttk.Frame(self.tab_mapa)
        btn_frame.pack(fill='x', padx=5, pady=5)
    
        ttk.Button(btn_frame, text="Actualizar mapa", command=self.actualizar_vista_mapa).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Abrir en navegador", command=self.mostrar_mapa).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Centrar en selección", command=self.centrar_mapa_seleccion).pack(side='left', padx=2)
    
    def actualizar_vista_mapa(self):
        if not hasattr(self, 'mapa_frame') or self.mapa_frame is None:
            self.mostrar_mapa()
            return
    
        temp_html = "temp_map_preview.html"
        try:
            self.generar_mapa_folium(temp_html)
        
            with open(temp_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
        
            self.mapa_frame.set_content(html_content)
            self.status_bar.config(text="Mapa actualizado")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el mapa:\n{str(e)}")
            self.status_bar.config(text="Error al actualizar mapa")
    
    def cargar_sesion(self):
        """Carga una sesión guardada previamente desde un archivo JSON"""
        ruta = filedialog.askopenfilename(
            defaultextension=".json", 
            filetypes=[("JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
    
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                sesion = json.load(f)
            
            self.datos = sesion.get("datos", [])
            self.letras = sesion.get("letras", {})
        
            self.actualizar_estadisticas()
            self.actualizar_tabla_datos()
            self.actualizar_vista_mapa()
        
            messagebox.showinfo("Éxito", f"Sesión cargada desde:\n{ruta}")
            self.status_bar.config(text=f"Sesión cargada: {os.path.basename(ruta)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la sesión:\n{str(e)}")
            self.status_bar.config(text="Error al cargar sesión")

    def centrar_mapa_seleccion(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        # Obtener coordenadas de los puntos seleccionados
        puntos = []
        for item in selected:
            idx = int(item)
            puntos.append(self.datos[idx])
        
        # Crear mapa centrado en la selección
        lats = [p['lat'] for p in puntos]
        lons = [p['lon'] for p in puntos]
        centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
        
        temp_html = "temp_map_centered.html"
        mapa = folium.Map(location=centro, zoom_start=18)
        
        # Añadir marcadores
        for p in puntos:
            letra = self.obtener_letra_punto(p)
            folium.Marker(
                [p['lat'], p['lon']],
                popup=self.crear_popup_punto(p),
                tooltip=f"ID: {p['id']}",
                icon=folium.Icon(color=color_por_letra(letra))
            ).add_to(mapa)
        
        mapa.save(temp_html)
        
        if self.mapa_frame is not None:
            with open(temp_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.mapa_frame.set_content(html_content)
        else:
            webbrowser.open('file://' + os.path.realpath(temp_html))
        
        self.status_bar.config(text=f"Mapa centrado en {len(puntos)} puntos seleccionados")

    
        # Coordenadas iniciales centradas en Tamaulipas
        centro_lat = 24.2669  # Latitud aproximada de centro de Tamaulipas
        centro_lon = -98.8363  # Longitud aproximada
    
        mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=7)
    
        # Añadir marcadores
        for punto in self.datos:
            letra = self.obtener_letra_punto(punto)
            folium.Marker(
                [punto['lat'], punto['lon']],
                popup=self.crear_popup_punto(punto),
                tooltip=f"ID: {punto['id']}",
                icon=folium.Icon(color=color_por_letra(letra))
            ).add_to(mapa)
    
        mapa.save(temp_html)
    
        # Calcular centro del mapa
        lats = [p['lat'] for p in self.datos]
        lons = [p['lon'] for p in self.datos]
        centro = [sum(lats)/len(lats), sum(lons)/len(lons)]
    
        mapa = folium.Map(location=centro, zoom_start=16)
    
    # Añadir marcadores
        for punto in self.datos:
            letra = self.obtener_letra_punto(punto)
            folium.Marker(
                [punto['lat'], punto['lon']],
                popup=self.crear_popup_punto(punto),
                tooltip=f"ID: {punto['id']}",
                icon=folium.Icon(color=color_por_letra(letra))
            ).add_to(mapa)
    
        mapa.save(temp_html)

    def validar_tamaulipas(self, x, y):
        """Valida rangos aproximados para el norte de Tamaulipas"""
        # Rangos más estrictos para norte de Tamaulipas
        x_min, x_max = 300000, 500000  # Rango Este
        y_min, y_max = 3100000, 3300000  # Rango Norte
        return (x_min <= x <= x_max) and (y_min <= y <= y_max)

    def obtener_letra_punto(self, punto):
        """Obtiene la letra del grupo a la que pertenece el punto"""
        if not punto.get('texto') or not isinstance(punto['texto'], str):
            return None  # O 'A' si prefieres un valor por defecto
    
        try:
            # Extraer la última parte después del último guión
            partes = punto['texto'].split('-')
            if not partes:
                return None
            
            ultima_parte = partes[-1].strip()
            if not ultima_parte:
                return None
        
            # Tomar el primer carácter y asegurarse que es letra
            letra = ultima_parte[0].upper()
            return letra if letra.isalpha() else None
    
        except (IndexError, AttributeError):
            return None

    def crear_popup_punto(self, punto):
        """Crea el contenido HTML para el popup de un punto en el mapa"""
        texto = punto.get('texto', 'Sin texto')
        alt = punto.get('alt', 0.0)
    
        return f"""
        <b>ID:</b> {punto['id']}<br>
        <b>Texto:</b> {texto}<br>
        <b>Coordenadas:</b><br>
        - UTM: {punto['x']:.2f}, {punto['y']:.2f}<br>
        - Lat/Lon: {punto['lat']:.6f}, {punto['lon']:.6f}<br>
        - Altura: {alt:.2f}
        """
    
    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(
            filetypes=[
                ("Archivos TXT", "*.txt"),
                ("Archivos CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not ruta:
            return

        # Crear ventana de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Cargando archivo...")
    
        progress = ttk.Progressbar(
            progress_window, orient='horizontal', 
            length=300, mode='determinate'
        )
        progress.pack(pady=20, padx=20)
    
        label = ttk.Label(progress_window, text="Procesando archivo...")
        label.pack(pady=5)
    
        self.root.update()

        try:
            with open(ruta, "r", encoding='utf-8') as archivo:
                lineas = archivo.readlines()
                total = len(lineas)
                self.datos = []
                self.letras = {}
    
                for i, linea in enumerate(lineas):
                    progress['value'] = (i/total)*100
                    label.config(text=f"Procesando línea {i+1} de {total}...")
                    progress_window.update()
        
                    # Procesar línea
                    vals = [v.strip() for v in linea.strip().split(",")]
        
                    if len(vals) >= 3:  # Mínimo ID, X, Y
                        idx = vals[0]
                        try:
                            x = float(vals[1])
                            y = float(vals[2])
                            alt = float(vals[3]) if len(vals) > 3 else 0.0
                            texto = vals[4] if len(vals) > 4 else ""
                
                            lat, lon = utm.to_latlon(x, y, self.zona_utm, self.hemisferio)
                
                            self.datos.append({
                                "id": idx,
                                "x": x,
                                "y": y,
                                "alt": alt,
                                "lat": lat,
                                "lon": lon,
                                "texto": texto
                            })
                
                        except ValueError as e:
                            continue  # Saltar líneas con error

            self.actualizar_estadisticas()
            self.actualizar_tabla_datos()
            self.actualizar_vista_mapa()
            self.status_bar.config(text=f"Cargados {len(self.datos)} puntos desde {os.path.basename(ruta)}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
            self.status_bar.config(text="Error al cargar archivo")
        finally:
            progress_window.destroy()

            
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en la interfaz"""
        total = len(self.datos)
        sin_nombre = sum(1 for p in self.datos if not p['texto'])
        con_nombre = total - sin_nombre
    
        # Actualizar el label de estadísticas
        self.label_estadisticas.config(
            text=f"Puntos: {total} | Con nombre: {con_nombre} | Sin nombre: {sin_nombre}"
        )
    
        # También puedes actualizar otros elementos si es necesario
        self.actualizar_barra_estado()
    
    def validar_coordenadas(self, x, y):
        """Valida que las coordenadas UTM estén en el rango esperado para Tamaulipas"""
        # Rango ajustado con base en tus datos reales
        x_min, x_max = 490000, 510000
        y_min, y_max = 2630000, 2640000

        if not (x_min <= x <= x_max) or not (y_min <= y <= y_max):
            resp = messagebox.askyesno(
                "Advertencia", 
                f"Coordenadas ({x}, {y}) fuera del rango típico para esta zona.\n"
                "¿Continuar de todos modos?"
            )
            return resp
        return True

    
    def guardar_sesion(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".json", 
            filetypes=[("JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        
        try:
            sesion = {
                "datos": self.datos, 
                "letras": self.letras,
                "metadata": {
                    "fecha_guardado": datetime.now().isoformat(),
                    "total_puntos": len(self.datos)
                }
            }
            
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(sesion, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"Sesión guardada en:\n{ruta}")
            self.status_bar.config(text=f"Sesión guardada: {os.path.basename(ruta)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la sesión:\n{str(e)}")
            self.status_bar.config(text="Error al guardar sesión")
    
    def asignar_nombres(self):
        """Asigna nombres a un grupo de puntos seleccionados o sin nombre"""
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Asignar Grupo de Nombres")
        ventana.geometry("400x350")

        # Variables
        letra_var = tk.StringVar()
        prefijo_var = tk.StringVar(value="Punto")
        sufijo_var = tk.StringVar()
        inicio_var = tk.IntVar(value=1)
        cantidad_var = tk.IntVar(value=10)
        aplicar_a_var = tk.StringVar(value="sin_nombre")  # Opción por defecto

        # Frame principal
        main_frame = ttk.Frame(ventana)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Controles
        ttk.Label(main_frame, text="Letra del grupo (A-Z):").grid(row=0, column=0, sticky='w', pady=(0,5))
        ttk.Entry(main_frame, textvariable=letra_var, width=5).grid(row=0, column=1, sticky='w', pady=(0,5))

        ttk.Label(main_frame, text="Prefijo:").grid(row=1, column=0, sticky='w', pady=(0,5))
        ttk.Entry(main_frame, textvariable=prefijo_var).grid(row=1, column=1, sticky='ew', pady=(0,5))

        ttk.Label(main_frame, text="Sufijo (opcional):").grid(row=2, column=0, sticky='w', pady=(0,5))
        ttk.Entry(main_frame, textvariable=sufijo_var).grid(row=2, column=1, sticky='ew', pady=(0,5))

        ttk.Label(main_frame, text="Número inicial:").grid(row=3, column=0, sticky='w', pady=(0,5))
        ttk.Spinbox(main_frame, from_=1, to=999, textvariable=inicio_var).grid(row=3, column=1, sticky='w', pady=(0,5))

        ttk.Label(main_frame, text="Cantidad:").grid(row=4, column=0, sticky='w', pady=(0,5))
        ttk.Spinbox(main_frame, from_=1, to=len(self.datos), textvariable=cantidad_var).grid(row=4, column=1, sticky='w', pady=(0,5))

        # Opciones para aplicar a qué puntos
        ttk.Label(main_frame, text="Aplicar a:").grid(row=5, column=0, sticky='w', pady=(0,5))
        ttk.Radiobutton(
            main_frame, 
            text="Puntos sin nombre", 
            variable=aplicar_a_var, 
            value="sin_nombre"
        ).grid(row=5, column=1, sticky='w', pady=(0,5))
    
        ttk.Radiobutton(
            main_frame, 
            text="Puntos seleccionados", 
            variable=aplicar_a_var, 
            value="seleccionados"
        ).grid(row=6, column=1, sticky='w', pady=(0,5))
    
        ttk.Radiobutton(
            main_frame, 
            text="Todos los puntos", 
            variable=aplicar_a_var, 
            value="todos"
        ).grid(row=7, column=1, sticky='w', pady=(0,5))

        # Frame para botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(10,0))

        def aplicar():
            letra = letra_var.get().strip().upper()
            if not letra or len(letra) != 1 or not letra.isalpha():
                messagebox.showerror("Error", "Ingrese una sola letra válida (A-Z).")
                return
        
            prefijo = prefijo_var.get().strip()
            sufijo = sufijo_var.get().strip()
            inicio = inicio_var.get()
            cantidad = cantidad_var.get()
            aplicar_a = aplicar_a_var.get()

            # Determinar a qué puntos aplicar los nombres
            if aplicar_a == "sin_nombre":
                puntos_a_nombrar = [i for i, p in enumerate(self.datos) if not p.get("texto", "").strip()]
            elif aplicar_a == "seleccionados":
                seleccionados = self.tree.selection()
                if not seleccionados:
                    messagebox.showwarning("Advertencia", "No hay puntos seleccionados.")
                    return
                puntos_a_nombrar = [int(item) for item in seleccionados]
            else:  # todos
                puntos_a_nombrar = list(range(len(self.datos)))

            if not puntos_a_nombrar:
                messagebox.showinfo("Info", "No hay puntos para nombrar según el criterio seleccionado.")
                ventana.destroy()
                return

            # Limitar a la cantidad especificada
            puntos_a_nombrar = puntos_a_nombrar[:cantidad]

            # Asignar nombres
            asignados = 0
            for i in puntos_a_nombrar:
                num = inicio + asignados
                nombre = f"{prefijo}-{num}{letra}"
                if sufijo:
                    nombre += f"-{sufijo}"
            
                self.datos[i]["texto"] = nombre
                self.letras.setdefault(letra, []).append(self.datos[i]["id"])
                asignados += 1

            # Actualizar interfaz
            self.actualizar_estadisticas()
            self.actualizar_tabla_datos()
            self.actualizar_vista_mapa()

            messagebox.showinfo("Éxito", f"Asignados {asignados} nombres al grupo {letra}.")
            ventana.destroy()

        # Botón Añadir
        ttk.Button(
            btn_frame, 
            text="Añadir", 
            command=aplicar
        ).pack(side='left', padx=5)

        # Botón Cancelar
        ttk.Button(
            btn_frame, 
            text="Cancelar", 
            command=ventana.destroy
        ).pack(side='left', padx=5)

        # Configurar expansión de columnas
        main_frame.columnconfigure(1, weight=1)

    def exportar_seleccion(self):
        """Exporta los puntos seleccionados a un archivo CSV"""
        seleccionados = self.tree.selection()
        if not seleccionados:
            messagebox.showwarning("Advertencia", "No hay puntos seleccionados")
            return
    
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
    
        try:
            with open(ruta, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'X', 'Y', 'Z', 'Lat', 'Lon', 'Texto'])
            
                for item in seleccionados:
                    idx = int(item)
                    punto = self.datos[idx]
                    writer.writerow([
                        punto['id'], 
                        punto['x'], 
                        punto['y'], 
                        punto['alt'], 
                        punto['lat'], 
                        punto['lon'], 
                        punto['texto']
                    ])
        
            messagebox.showinfo("Éxito", f"Se exportaron {len(seleccionados)} puntos a:\n{ruta}")
            self.status_bar.config(text=f"Selección exportada: {os.path.basename(ruta)}")
    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar la selección:\n{str(e)}")
            self.status_bar.config(text="Error al exportar selección")

    

    def actualizar_estadisticas(self):
        total = len(self.datos)
        sin_nombre = sum(1 for p in self.datos if not p['texto'])
        self.label_estadisticas.config(
            text=f"Puntos: {total} | Sin nombre: {sin_nombre}"
        )
    
    def aplicar_tema(self, tema):
        self.current_theme = tema
        ttk.Style().theme_use(tema)
        self.status_bar.config(text=f"Tema aplicado: {tema.capitalize()}")

    def editar_puntos(self):
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Editar Puntos")
        ventana.geometry("800x600")
        
        frame = ttk.Frame(ventana)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview para edición
        tree = ttk.Treeview(
            frame,
            columns=('ID', 'Texto'),
            show='headings'
        )
        tree.heading('ID', text='ID')
        tree.heading('Texto', text='Texto')
        tree.column('ID', width=100)
        tree.column('Texto', width=600)
        
        # Scrollbar
        scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        
        scroll.pack(side='right', fill='y')
        tree.pack(side='left', fill='both', expand=True)
        
        # Llenar datos
        for punto in self.datos:
            tree.insert('', 'end', values=(punto['id'], punto['texto']))
        
        # Edición en doble click
        def on_double_click(event):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            
            if column == '#2' and item:  # Columna de texto
                x, y, width, height = tree.bbox(item, column)
                value = tree.item(item, 'values')[1]
                
                entry = ttk.Entry(tree)
                entry.place(x=x, y=y, width=width, height=height)
                entry.insert(0, value)
                entry.select_range(0, tk.END)
                entry.focus_set()
                
                def save_edit(event=None):
                    new_value = entry.get()
                    current_values = list(tree.item(item, 'values'))
                    current_values[1] = new_value
                    tree.item(item, values=current_values)
                    entry.destroy()
                
                entry.bind('<Return>', save_edit)
                entry.bind('<FocusOut>', lambda e: entry.destroy())
        
        tree.bind('<Double-1>', on_double_click)
        
        # Botón para guardar
        def guardar_cambios():
            for item in tree.get_children():
                item_id, texto = tree.item(item, 'values')
                for punto in self.datos:
                    if punto['id'] == item_id:
                        punto['texto'] = texto
                        break
            
            # Reconstruir diccionario de letras
            self.letras = {}
            for punto in self.datos:
                if punto['texto'] and '-' in punto['texto']:
                    letra = punto['texto'].split('-')[-1][0].upper()
                    if letra.isalpha():
                        self.letras.setdefault(letra, []).append(punto['id'])
            
            self.actualizar_estadisticas()
            self.actualizar_tabla_datos()
            self.actualizar_vista_mapa()
            messagebox.showinfo("Éxito", "Cambios guardados correctamente.")
            ventana.destroy()
        
        ttk.Button(
            ventana, 
            text="Guardar Cambios", 
            command=guardar_cambios
        ).pack(pady=5)
    
    def buscar_filtrar(self):
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Buscar/Filtrar Puntos")
        ventana.geometry("400x200")
        
        ttk.Label(ventana, text="Buscar por:").pack(pady=(10, 0))
        
        search_var = tk.StringVar()
        search_entry = ttk.Entry(ventana, textvariable=search_var)
        search_entry.pack(pady=5, padx=10, fill='x')
        
        search_type = tk.StringVar(value="texto")
        ttk.Radiobutton(
            ventana, 
            text="En texto", 
            variable=search_type, 
            value="texto"
        ).pack(anchor='w', padx=20)
        
        ttk.Radiobutton(
            ventana, 
            text="En ID", 
            variable=search_type, 
            value="id"
        ).pack(anchor='w', padx=20)
        
        ttk.Radiobutton(
            ventana, 
            text="En grupo (letra)", 
            variable=search_type, 
            value="grupo"
        ).pack(anchor='w', padx=20)
        
        def buscar():
            criterio = search_var.get().strip().upper()
            tipo = search_type.get()
            
            if not criterio:
                messagebox.showwarning("Advertencia", "Ingrese un criterio de búsqueda.")
                return
            
            resultados = []
            
            if tipo == "texto":
                resultados = [p for p in self.datos if criterio in p['texto'].upper()]
            elif tipo == "id":
                resultados = [p for p in self.datos if criterio in p['id'].upper()]
            elif tipo == "grupo":
                resultados = [p for p in self.datos 
                            if p['texto'] and '-' in p['texto'] 
                            and criterio == p['texto'].split('-')[-1][0].upper()]
            
            if not resultados:
                messagebox.showinfo("Resultados", "No se encontraron coincidencias.")
                return
            
            # Mostrar resultados en una nueva ventana
            result_window = tk.Toplevel(self.root)
            result_window.title(f"Resultados: {len(resultados)} puntos")
            result_window.geometry("600x400")
            
            frame = ttk.Frame(result_window)
            frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            tree = ttk.Treeview(
                frame,
                columns=('ID', 'Texto', 'Coordenadas'),
                show='headings'
            )
            
            tree.heading('ID', text='ID')
            tree.heading('Texto', text='Texto')
            tree.heading('Coordenadas', text='Coordenadas (Lat, Lon)')
            
            tree.column('ID', width=100)
            tree.column('Texto', width=250)
            tree.column('Coordenadas', width=200)
            
            scroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scroll.set)
            
            scroll.pack(side='right', fill='y')
            tree.pack(side='left', fill='both', expand=True)
            
            for punto in resultados:
                coords = f"{punto['lat']:.6f}, {punto['lon']:.6f}"
                tree.insert('', 'end', values=(punto['id'], punto['texto'], coords))
            
            def mostrar_seleccion():
                if not self.licencia_valida:
                    return
                selected = tree.focus()
                if selected:
                    values = tree.item(selected, 'values')
                    messagebox.showinfo(
                        "Detalle del punto",
                        f"ID: {values[0]}\n"
                        f"Texto: {values[1]}\n"
                        f"Coordenadas: {values[2]}\n"
                        f"UTM: {next(p['x'] for p in self.datos if p['id'] == values[0]):.2f}, "
                        f"{next(p['y'] for p in self.datos if p['id'] == values[0]):.2f}"
                    )
            
            ttk.Button(
                result_window, 
                text="Ver Detalle", 
                command=mostrar_seleccion
            ).pack(pady=5)
            
            ventana.destroy()
        
        ttk.Button(ventana, text="Buscar", command=buscar).pack(pady=10)
    
    def ver_estadisticas(self):
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
        
        ventana = tk.Toplevel(self.root)
        ventana.title("Estadísticas")
        ventana.geometry("500x500")
        
        notebook = ttk.Notebook(ventana)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Pestaña de resumen
        tab_resumen = ttk.Frame(notebook)
        notebook.add(tab_resumen, text="Resumen")
        
        total = len(self.datos)
        con_nombre = sum(1 for p in self.datos if p['texto'])
        sin_nombre = total - con_nombre
        
        texto_resumen = (
            f"Total de puntos: {total}\n"
            f"Puntos con nombre: {con_nombre} ({con_nombre/total*100:.1f}%)\n"
            f"Puntos sin nombre: {sin_nombre} ({sin_nombre/total*100:.1f}%)\n\n"
            f"Grupos definidos: {len(self.letras)}\n"
        )
        
        for letra, puntos in sorted(self.letras.items()):
            texto_resumen += f" - Grupo {letra}: {len(puntos)} puntos\n"
        
        label_resumen = ttk.Label(
            tab_resumen, 
            text=texto_resumen,
            justify='left'
        )
        label_resumen.pack(pady=10, padx=10, anchor='nw')
        
        # Pestaña de gráfico
        if self.letras:
            tab_grafico = ttk.Frame(notebook)
            notebook.add(tab_grafico, text="Gráfico")
            
            fig, ax = plt.subplots(figsize=(5, 4))
            letras = sorted(self.letras.keys())
            counts = [len(self.letras[l]) for l in letras]
            
            ax.bar(letras, counts, color=[color_por_letra(l) for l in letras])
            ax.set_title("Distribución por Grupo")
            ax.set_xlabel("Letra del grupo")
            ax.set_ylabel("Número de puntos")
            
            canvas = FigureCanvasTkAgg(fig, master=tab_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def mostrar_ayuda(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Ayuda")
        ventana.geometry("600x500")
        
        texto_ayuda = """
        Editor de Coordenadas TXT a KML - Ayuda
        
        1. CARGAR DATOS
        - Puede cargar archivos TXT o CSV con el formato: ID,X,Y,Z,Texto(opcional)
        - Las coordenadas deben ser UTM (zona 14Q)
        - También puede cargar una sesión guardada (.json)
        
        2. EDITAR PUNTOS
        - Asigne nombres a grupos de puntos usando la función "Asignar grupo"
        - Edite manualmente los nombres con "Editar puntos"
        - Busque y filtre puntos con "Buscar/Filtrar"
        
        3. VISUALIZACIÓN
        - Vea los puntos en el mapa (vista previa o navegador)
        - Abra los datos en Google Maps o QGIS
        - Consulte estadísticas de distribución
        
        4. EXPORTAR DATOS
        - Exporte los datos a formatos KML, CSV o GeoJSON.
        - Los datos exportados pueden ser utilizados en otras aplicaciones de SIG.
        
        5. TEMAS
        - Cambie el tema de la interfaz para personalizar la apariencia.
        
        Para más información, consulte la documentación o el soporte técnico.
        """
        
        label_ayuda = ttk.Label(ventana, text=texto_ayuda, justify='left')
        label_ayuda.pack(pady=10, padx=10, anchor='nw')
    
    def mostrar_acerca_de(self):
        messagebox.showinfo("Acerca de", "Editor de Coordenadas TXT a KML - Versión 1.0\nDesarrollado por Allen Zuñiga Aldape\n\nEste software permite cargar, editar y exportar datos de coordenadas en diferentes formatos.")
    
    def guardar_kml(self):
        try:
            import simplekml
        except ImportError:
            messagebox.showerror("Error", "Para exportar KML, instale simplekml: pip install simplekml")
            return
    
        ruta = filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=[("KML", "*.kml"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        try:
            kml = simplekml.Kml()
            for punto in self.datos:
                pnt = kml.newpoint(
                    name=punto["texto"],
                    coords=[(punto["lon"], punto["lat"])],
                    description=f"ID: {punto['id']}\nX: {punto['x']}\nY: {punto['y']}\nZ: {punto['alt']}"
                )
            kml.save(ruta)
        
            messagebox.showinfo("Éxito", f"KML guardado en:\n{ruta}")
            self.status_bar.config(text=f"KML guardado: {os.path.basename(ruta)}")
    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el KML:\n{str(e)}")
            self.status_bar.config(text="Error al guardar KML")

        
    
    def exportar_csv(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        
        try:
            with open(ruta, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'X', 'Y', 'Z', 'Lat', 'Lon', 'Texto'])
                for punto in self.datos:
                    writer.writerow([punto['id'], punto['x'], punto['y'], punto['alt'], punto['lat'], punto['lon'], punto['texto']])
            
            messagebox.showinfo("Éxito", f"CSV guardado en:\n{ruta}")
            self.status_bar.config(text=f"CSV guardado: {os.path.basename(ruta)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el CSV:\n{str(e)}")
            self.status_bar.config(text="Error al guardar CSV")
    
    def exportar_geojson(self):
        ruta = filedialog.asksaveasfilename(
            defaultextension=".geojson",
            filetypes=[("GeoJSON", "*.geojson"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return
        
        try:
            geojson_data = {
                "type": "FeatureCollection",
                "features": []
            }
            
            for punto in self.datos:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [punto['lon'], punto['lat']]
                    },
                    "properties": {
                        "id": punto['id'],
                        "texto": punto['texto']
                    }
                }
                geojson_data["features"].append(feature)
            
            with open(ruta, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Éxito", f"GeoJSON guardado en:\n{ruta}")
            self.status_bar.config(text=f"GeoJSON guardado: {os.path.basename(ruta)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el GeoJSON:\n{str(e)}")
            self.status_bar.config(text="Error al guardar GeoJSON")

    def mostrar_mapa(self):
        """Muestra el mapa en el navegador web."""
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
    
        temp_html = "temp_map.html"
        self.generar_mapa_folium(temp_html)
        webbrowser.open('file://' + os.path.realpath(temp_html))

    def mostrar_vista_previa_mapa(self):
        """Muestra una vista previa del mapa en la aplicación."""
        self.actualizar_vista_mapa()  # Asegúrate de que esta función esté definida

    def abrir_en_google_maps(self):
        """Abre la ubicación en Google Maps."""
        if not self.datos:
            messagebox.showwarning("Advertencia", "No hay datos cargados.")
            return
        
        # Suponiendo que quieres abrir el primer punto en Google Maps
        primer_punto = self.datos[0]
        lat = primer_punto['lat']
        lon = primer_punto['lon']
        url = f"https://www.google.com/maps/@{lat},{lon},15z"
        webbrowser.open(url)

    def abrir_en_qgis(self):
        """Abre la ubicación en QGIS."""
        messagebox.showinfo("Información", "Esta función requiere configuración adicional para integrarse con QGIS")

    def generar_mapa_folium(self, temp_html):
        """Genera un mapa usando Folium centrado en Tamaulipas"""
        if not self.datos:
            return

        # Coordenadas iniciales centradas en Tamaulipas
        centro_lat = 24.2669
        centro_lon = -98.8363

        mapa = folium.Map(location=[centro_lat, centro_lon], zoom_start=7)

        # Añadir marcadores
        for punto in self.datos:
            letra = self.obtener_letra_punto(punto)
            folium.Marker(
                [punto['lat'], punto['lon']],
                popup=self.crear_popup_punto(punto),
                tooltip=punto['texto'] if punto['texto'] else f"ID: {punto['id']}",  # Mostrar texto si existe, sino mostrar ID
                icon=folium.Icon(color=color_por_letra(letra))
            ).add_to(mapa)

        mapa.save(temp_html)
    
    def mostrar_eula(self):
        eula_text = """\
    TÉRMINOS Y CONDICIONES DE USO
    --------------------------------
    [ACUERDO DE LICENCIA DE USUARIO FINAL (EULA)

Importante: Lea detenidamente este Acuerdo antes de instalar o utilizar este software. Al instalar, copiar o utilizar el Software, usted acepta estar sujeto a los términos de este Acuerdo.

1. Concesión de Licencia
El Licenciante, Allen Josue Zuñiga Aldape, le otorga una licencia no exclusiva, intransferible y limitada para instalar y utilizar el Software ("Editor de Coordenadas TXT a KML - Pro") en un único equipo, únicamente para uso comercial interno.

2. Uso Comercial y Valor Premium
El Software es una solución comercial de alta calidad, diseñada y optimizada para el manejo, edición y exportación de datos geográficos. El valor de esta licencia refleja su exclusividad y las funcionalidades avanzadas integradas. Usted reconoce que este producto no puede ser redistribuido, sublicenciado, vendido, o ofrecido como servicio a terceros sin el consentimiento previo y por escrito del Licenciante. Cualquier intento de comercialización o integración sin autorización constituirá una violación de este Acuerdo.

3. Restricciones

No se permite la ingeniería inversa, descompilación, desensamblado ni modificación del Software.

No se autoriza la eliminación o alteración de avisos de propiedad intelectual o de derechos de autor contenidos en el Software.

No podrá integrarse el Software en otros productos o servicios sin la autorización expresa del Licenciante.

4. Pago, Actualizaciones y Soporte
El precio de esta licencia ha sido fijado considerando el valor comercial y las características premium del Software. El Licenciante se reserva el derecho de modificar el precio para futuras versiones o actualizaciones del Software. Los servicios de soporte y actualizaciones adicionales podrán ofrecerse mediante acuerdos complementarios que podrían implicar costos adicionales.

5. Garantías y Limitaciones de Responsabilidad
El Software se suministra "tal cual", sin garantía de ningún tipo, ya sea expresa o implícita. En ningún caso el Licenciante será responsable de daños directos, indirectos, incidentales, especiales o consecuentes, incluyendo pérdida de datos o beneficios, derivados del uso o la imposibilidad de uso del Software, incluso si el Licenciante ha sido advertido de la posibilidad de tales daños.

6. Terminación
Este Acuerdo se rescindirá de manera inmediata si usted incumple cualquiera de sus términos. En caso de terminación, deberá dejar de utilizar el Software y destruir todas las copias en su poder. La terminación no liberará al usuario de las obligaciones de pago acumuladas o de cualquier responsabilidad pendiente derivada del incumplimiento.

7. Propiedad Intelectual
Todos los derechos, títulos e intereses sobre el Software y cualquier copia del mismo son propiedad exclusiva del Licenciante. Este Acuerdo no otorga ningún derecho de propiedad sobre el Software, solo el derecho de uso conforme a sus términos.

8. Ley Aplicable y Jurisdicción
Este Acuerdo se regirá e interpretará de acuerdo con las leyes de Mexico. Cualquier controversia derivada del presente Acuerdo se someterá a la jurisdicción exclusiva de los tribunales de [Ciudad/Región], renunciando expresamente a cualquier otro fuero que pudiera corresponder.

9. Aceptación del Acuerdo
Al instalar, copiar o utilizar el Software, usted reconoce haber leído, comprendido y aceptado los términos y condiciones establecidos en este Acuerdo. Si no está de acuerdo, no debe instalar ni utilizar el Software.

    Al hacer clic en "Acepto", usted acepta estos términos.
    """
        ventana_eula = tk.Toplevel(self.root)
        ventana_eula.title("Acuerdo de Licencia")
        ventana_eula.geometry("600x400")
        ventana_eula.grab_set()  # Hace que la ventana sea modal

        texto = tk.Text(ventana_eula, wrap="word")
        texto.insert("1.0", eula_text)
        texto.configure(state="disabled")
        texto.pack(fill="both", expand=True, padx=10, pady=10)

        def aceptar():
            ventana_eula.destroy()
            # Aquí se podría guardar un indicador de aceptación

        def rechazar():
            self.root.destroy()

        btn_frame = tk.Frame(ventana_eula)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Acepto", command=aceptar).pack(side="left", padx=10)
        tk.Button(btn_frame, text="No acepto", command=rechazar).pack(side="left", padx=10)

        self.root.wait_window(ventana_eula)

    @staticmethod
    def generar_licencia(nombre_cliente, fecha_expiracion=None):
        """Genera un archivo de licencia .lic"""
        lic_data = {
            'nombre': nombre_cliente,
            'fecha_generacion': datetime.now().strftime("%Y-%m-%d"),
            'fecha_expiracion': fecha_expiracion.strftime("%Y-%m-%d") if fecha_expiracion else None,
            'hash_verificacion': hashlib.sha256((nombre_cliente + str(datetime.now().timestamp())).encode()).hexdigest()[:16]
        }
        return lic_data
    @staticmethod
    def guardar_licencia(lic_data, ruta_archivo):
        """Guarda la licencia en un archivo"""
        with open(ruta_archivo, 'w') as f:
            json.dump(lic_data, f, indent=2)

    @staticmethod
    def cargar_licencia(ruta_archivo):
        """Carga y verifica la licencia"""
        try:
            with open(ruta_archivo, 'r') as f:
                lic_data = json.load(f)
        
            # Verificación básica (puedes hacerla más compleja)
            if not all(key in lic_data for key in ['nombre', 'hash_verificacion']):
                return None
            
            if 'fecha_expiracion' in lic_data and lic_data['fecha_expiracion']:
                if datetime.strptime(lic_data['fecha_expiracion'], "%Y-%m-%d") < datetime.now():
                    return None
                
            return lic_data
        except:
            return None
        
    def verificar_licencia(self):
        """Verifica si existe una licencia válida"""
        lic_path = os.path.join(os.path.dirname(__file__), "licencia.lic")
        if not os.path.exists(lic_path):
            return False
    
        lic_data = self.cargar_licencia(lic_path)
        return lic_data is not None

    def mostrar_ventana_licencia(self):
        """Muestra la ventana de registro de licencia"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Registro de Licencia")
        ventana.geometry("400x250")

        ttk.Label(ventana, text="Registro de Licencia", font=('Arial', 12, 'bold')).pack(pady=10)

        frame = ttk.Frame(ventana)
        frame.pack(pady=10, padx=20, fill='x')

        ttk.Label(frame, text="Nombre del Cliente:").pack(anchor='w')
        nombre_var = tk.StringVar()
        ttk.Entry(frame, textvariable=nombre_var).pack(fill='x', pady=5)

        def generar_licencia_cliente():
            nombre = nombre_var.get().strip()
            if not nombre:
                messagebox.showerror("Error", "Por favor ingrese un nombre válido")
                return
        
            # Generar licencia con 1 año de validez
            fecha_expiracion = datetime.now() + timedelta(days=365)
            lic_data = self.generar_licencia(nombre, fecha_expiracion)
    
            # Guardar licencia en el mismo directorio que la aplicación
            lic_path = os.path.join(os.path.dirname(__file__), "licencia.lic")
            self.guardar_licencia(lic_data, lic_path)
    
            messagebox.showinfo("Éxito", f"Licencia generada para {nombre}\nVálida hasta {fecha_expiracion.strftime('%Y-%m-%d')}")
            ventana.destroy()
            self.licencia_valida = True
            # Reiniciar la aplicación mostrando EULA
            self.mostrar_eula()
            self.crear_interfaz_principal()

        ttk.Button(
            ventana, 
            text="Generar Licencia", 
            command=generar_licencia_cliente
        ).pack(pady=15)

        ttk.Label(
            ventana, 
            text="Para adquirir una licencia, contacte al desarrollador",
            font=('Arial', 8)
        ).pack(side='bottom', pady=5)

        # Hacer que la ventana sea modal
        ventana.grab_set()
        self.root.wait_window(ventana)

    def crear_interfaz_principal(self):
        """Crea todos los componentes de la interfaz principal"""
        self.root.title("Editor de Coordenadas TXT a KML - Pro")
        self.datos = []
        self.letras = {}
        self.html_frame_available = HtmlFrame is not None
        self.mapa_frame = None
        self.current_theme = 'clam'

        # Configurar tamaño inicial y menú
        self.root.geometry("900x700")
        self.crear_menu()

        # Resto de la inicialización de la interfaz...
        # (Mover aquí todo el código de inicialización que estaba en __init__ después de la verificación de licencia)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = MapaEditorApp(root)
    if app.licencia_valida:  # Solo ejecutar mainloop si la licencia es válida
        root.mainloop()