Editor de Coordenadas TXT a KML - Pro
Python
License

Una herramienta para convertir archivos de texto con coordenadas a formato KML (Keyhole Markup Language), útil para visualización en Google Earth y otros sistemas GIS.

📌 Características
Conversión de TXT a KML: Transforma archivos de texto con coordenadas en archivos KML listos para usar en Google Earth.

Interfaz gráfica intuitiva: Diseñada con Tkinter para una experiencia de usuario sencilla.

Personalización: Permite modificar estilos, colores y nombres de marcadores.

Visualización previa: Muestra un mapa interactivo antes de exportar.

Temas personalizables: Soporte para diferentes estilos visuales (ej: 'clam').

⚙️ Requisitos
Python 3.7 o superior

Bibliotecas requeridas:

bash
Copy
tkinter, simplekml, pywebview (opcional para visualización HTML)
Instálalas con:

bash
Copy
pip install simplekml pywebview
🚀 Cómo usar
Ejecuta la aplicación:

bash
Copy
python editor_kml_pro.py
Carga tu archivo TXT:

El archivo debe contener coordenadas en formato lat, lon o lat lon.

Ejemplo:

Copy
-34.603722, -58.381592  
40.712776, -74.005974  
Personaliza los marcadores:

Añade nombres, descripciones o cambia colores.

Genera el KML:

Guarda el archivo en la ruta deseada y ábrelo en Google Earth.

📁 Estructura del proyecto
Copy
editor_kml_pro.py      # Código principal  
requirements.txt       # Dependencias  
ejemplo_coordenas.txt  # Archivo de ejemplo  
📜 Licencia
MIT License.

🔍 Capturas de pantalla (opcional)
Interfaz (reemplaza con una imagen real)

📧 Contacto
¿Preguntas o sugerencias?
✉️ tu-email@dominio.com

Notas adicionales
Si usas HtmlFrame para mapas interactivos, asegúrate de tener conexión a Internet.

Personaliza los temas con self.current_theme (ej: 'clam', 'alt', etc.).
