"""
Generador de PDF para reportes de análisis de marcas
Utiliza WeasyPrint para convertir HTML a PDF
"""

import os
import logging
from datetime import datetime
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class GeneradorPDF:
    """
    Genera reportes PDF profesionales a partir de análisis de marcas
    """
    
    def __init__(self, pdf_folder: str, logo_path: str = None):
        """
        Inicializa el generador de PDF
        
        Args:
            pdf_folder: Carpeta donde se guardarán los PDFs
            logo_path: Ruta al archivo del logo (opcional)
        """
        self.pdf_folder = pdf_folder
        self.logo_path = logo_path
        
        # Crear carpeta si no existe
        os.makedirs(pdf_folder, exist_ok=True)
        
        logger.info(f"GeneradorPDF inicializado. Carpeta: {pdf_folder}")
    
    def generar_reporte(self, lead: dict, analisis: dict) -> str:
        """
        Genera un reporte PDF completo
        
        Args:
            lead: Diccionario con datos del lead
            analisis: Diccionario con datos del análisis
        
        Returns:
            Ruta al archivo PDF generado
        """
        try:
            # Sanitizar nombre de marca para nombre de archivo
            marca_limpia = "".join(c for c in lead.get('marca', 'marca') if c.isalnum() or c in (' ', '-', '_')).strip()
            marca_limpia = marca_limpia.replace(' ', '_')[:50]
            
            # Nombre del archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reporte_{marca_limpia}_{timestamp}.pdf"
            filepath = os.path.join(self.pdf_folder, filename)
            
            logger.info(f"[PDF] Generando: {filename}")
            
            # Generar HTML
            html_content = self._generar_html(lead, analisis)
            
            # CSS personalizado
            css_content = self._generar_css()
            
            # Configuración de fuentes
            font_config = FontConfiguration()
            
            # Convertir HTML a PDF
            HTML(string=html_content).write_pdf(
                filepath,
                stylesheets=[CSS(string=css_content, font_config=font_config)],
                font_config=font_config
            )
            
            logger.info(f"✅ PDF generado: {filename}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generando PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generar_html(self, lead: dict, analisis: dict) -> str:
        """
        Genera el HTML del reporte
        """
        marca = lead.get('marca', 'N/A')
        cliente = lead.get('nombre', 'Cliente')
        clase = lead.get('clase_sugerida', 'N/A')
        
        # Formatear fecha en español
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        ahora = datetime.now()
        fecha_analisis = f"{ahora.day} de {meses[ahora.month-1]} de {ahora.year}"
        
        # Datos del análisis
        viabilidad = analisis.get('porcentaje_viabilidad', 0)
        nivel_riesgo = analisis.get('nivel_riesgo', 'MEDIO')
        analisis_principal = analisis.get('analisis_principal', '')
        factores_riesgo = analisis.get('factores_riesgo', [])
        factores_favorables = analisis.get('factores_favorables', [])
        recomendaciones = analisis.get('recomendaciones', [])
        marcas_conflictivas = analisis.get('marcas_conflictivas', [])
        
        # Convertir listas a HTML si vienen como strings con saltos de línea
        if isinstance(factores_riesgo, str):
            factores_riesgo = [f.strip('• ').strip() for f in factores_riesgo.split('\n') if f.strip()]
        if isinstance(factores_favorables, str):
            factores_favorables = [f.strip('• ').strip() for f in factores_favorables.split('\n') if f.strip()]
        if isinstance(recomendaciones, str):
            recomendaciones = [r.strip('1234567890. ').strip() for r in recomendaciones.split('\n') if r.strip()]
        
        # Color del riesgo
        color_riesgo = {
            'BAJO': '#10b981',
            'MEDIO': '#f59e0b',
            'ALTO': '#ef4444'
        }.get(nivel_riesgo.upper(), '#6b7280')
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte de Análisis - {marca}</title>
</head>
<body>
    <!-- HEADER -->
    <div class="header">
        <div class="logo-container">
            <div class="logo-text">MARCA SEGURA</div>
        </div>
        <div class="header-title">
            <h1>Examen de Viabilidad aplicado a la marca<br><strong>{marca}</strong><br>ante el IMPI</h1>
        </div>
        <div class="header-info">
            <p><strong>Fecha:</strong> {fecha_analisis}</p>
            <p><strong>Cliente:</strong> {cliente}</p>
            <p><strong>Clase Niza:</strong> {clase}</p>
        </div>
    </div>
    
    <!-- RESUMEN EJECUTIVO -->
    <div class="seccion">
        <h2>Resumen Ejecutivo</h2>
        <div class="viabilidad-container">
            <div class="viabilidad-box">
                <div class="viabilidad-label">Porcentaje de Viabilidad</div>
                <div class="viabilidad-valor">{viabilidad}%</div>
            </div>
            <div class="riesgo-box" style="border-color: {color_riesgo};">
                <div class="riesgo-label">Nivel de Riesgo</div>
                <div class="riesgo-valor" style="color: {color_riesgo};">{nivel_riesgo}</div>
            </div>
        </div>
    </div>
    
    <!-- ANÁLISIS DETALLADO -->
    <div class="seccion">
        <h2>Análisis Detallado</h2>
        <div class="texto-analisis">
            {analisis_principal.replace(chr(10), '<br>')}
        </div>
    </div>
    
    <!-- MARCAS CONFLICTIVAS -->
    {self._generar_tabla_marcas(marcas_conflictivas)}
    
    <!-- FACTORES DE RIESGO -->
    {self._generar_lista('Factores de Riesgo', factores_riesgo, 'riesgo')}
    
    <!-- FACTORES FAVORABLES -->
    {self._generar_lista('Factores Favorables', factores_favorables, 'favorable')}
    
    <!-- RECOMENDACIONES -->
    {self._generar_recomendaciones(recomendaciones)}
    
    <!-- FOOTER -->
    <div class="footer">
        <p>Este reporte ha sido elaborado por MARCA SEGURA</p>
        <p>Consultores especializados en propiedad intelectual</p>
        <p>Documento confidencial - Para uso exclusivo del cliente</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generar_tabla_marcas(self, marcas: list) -> str:
        """Genera la tabla de marcas conflictivas"""
        if not marcas or len(marcas) == 0:
            return """
            <div class="seccion">
                <h2>Marcas Potencialmente Conflictivas</h2>
                <p class="no-marcas">No se identificaron marcas conflictivas significativas.</p>
            </div>
            """
        
        filas = ""
        for i, marca in enumerate(marcas[:15], 1):
            denominacion = marca.get('denominacion', 'N/A')
            expediente = marca.get('expediente', 'N/A')
            titular = marca.get('titular', 'No especificado')
            clase = marca.get('clase', 'N/A')
            estado = marca.get('estado', 'N/A')
            
            # Truncar titular si es muy largo
            if len(titular) > 40:
                titular = titular[:40] + '...'
            
            filas += f"""
            <tr>
                <td>{i}</td>
                <td><strong>{denominacion}</strong></td>
                <td>{expediente}</td>
                <td>{titular}</td>
                <td>{clase}</td>
                <td><span class="estado-marca">{estado}</span></td>
            </tr>
            """
        
        return f"""
        <div class="seccion">
            <h2>Marcas Potencialmente Conflictivas</h2>
            <p class="descripcion-tabla">Se han identificado {len(marcas)} marcas registradas que podrían representar un conflicto. A continuación se muestran las más relevantes:</p>
            <table class="tabla-marcas">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Denominación</th>
                        <th>Expediente</th>
                        <th>Titular</th>
                        <th>Clase</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
                    {filas}
                </tbody>
            </table>
        </div>
        """
    
    def _generar_lista(self, titulo: str, items: list, tipo: str) -> str:
        """Genera una lista con viñetas"""
        if not items or len(items) == 0:
            return ""
        
        icono = '⚠' if tipo == 'riesgo' else '✓'
        color = '#ef4444' if tipo == 'riesgo' else '#10b981'
        
        items_html = ""
        for item in items:
            items_html += f'<li><span class="icono" style="color: {color};">{icono}</span> {item}</li>'
        
        return f"""
        <div class="seccion">
            <h2>{titulo}</h2>
            <ul class="lista-items">
                {items_html}
            </ul>
        </div>
        """
    
    def _generar_recomendaciones(self, recomendaciones: list) -> str:
        """Genera la sección de recomendaciones"""
        if not recomendaciones or len(recomendaciones) == 0:
            return ""
        
        items_html = ""
        for i, rec in enumerate(recomendaciones, 1):
            items_html += f'<li><strong>{i}.</strong> {rec}</li>'
        
        return f"""
        <div class="seccion recomendaciones">
            <h2>Recomendaciones</h2>
            <ol class="lista-recomendaciones">
                {items_html}
            </ol>
        </div>
        """
    
    def _generar_css(self) -> str:
        """Genera el CSS para el PDF"""
        return """
        @page {
            size: Letter;
            margin: 2cm 1.5cm;
            
            @top-right {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 9pt;
                color: #6b7280;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1f2937;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #7c3aed;
        }
        
        .logo-text {
            font-size: 24pt;
            font-weight: bold;
            color: #7c3aed;
            letter-spacing: 2px;
        }
        
        .header-title h1 {
            font-size: 18pt;
            color: #1f2937;
            margin: 15px 0;
            line-height: 1.4;
        }
        
        .header-title strong {
            color: #7c3aed;
            font-size: 20pt;
        }
        
        .header-info {
            margin-top: 15px;
            font-size: 10pt;
            color: #6b7280;
        }
        
        .seccion {
            margin-bottom: 25px;
            page-break-inside: avoid;
        }
        
        h2 {
            color: #7c3aed;
            font-size: 14pt;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        .viabilidad-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        
        .viabilidad-box, .riesgo-box {
            text-align: center;
            padding: 20px;
            border: 3px solid #7c3aed;
            border-radius: 10px;
            width: 45%;
        }
        
        .viabilidad-valor {
            font-size: 36pt;
            font-weight: bold;
            color: #7c3aed;
        }
        
        .riesgo-valor {
            font-size: 24pt;
            font-weight: bold;
        }
        
        .texto-analisis {
            background-color: #f9fafb;
            padding: 15px;
            border-left: 4px solid #7c3aed;
            border-radius: 5px;
            font-size: 10pt;
            line-height: 1.8;
        }
        
        .tabla-marcas {
            width: 100%;
            border-collapse: collapse;
            font-size: 9pt;
        }
        
        .tabla-marcas thead {
            background-color: #7c3aed;
            color: white;
        }
        
        .tabla-marcas th {
            padding: 10px 8px;
            text-align: left;
        }
        
        .tabla-marcas td {
            padding: 8px;
            border-bottom: 1px solid #e5e7eb;
        }
        
        .tabla-marcas tbody tr:nth-child(even) {
            background-color: #f9fafb;
        }
        
        .lista-items {
            list-style: none;
            padding: 0;
        }
        
        .lista-items li {
            margin-bottom: 10px;
            padding-left: 30px;
            position: relative;
        }
        
        .lista-items .icono {
            position: absolute;
            left: 0;
            font-size: 14pt;
        }
        
        .recomendaciones {
            background-color: #fef3c7;
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #f59e0b;
        }
        
        .lista-recomendaciones {
            padding-left: 0;
            list-style: none;
        }
        
        .lista-recomendaciones li {
            margin-bottom: 12px;
        }
        
        .lista-recomendaciones strong {
            color: #f59e0b;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e5e7eb;
            text-align: center;
            font-size: 9pt;
            color: #6b7280;
        }
        """
