import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

def generar_informe_ejecutivo(datos, tipo='pdf'):
    """
    Genera un informe ejecutivo con datos resumidos y gráficos
    """
    if tipo == 'pdf':
        return generar_pdf_ejecutivo(datos)
    else:  # csv
        return generar_csv_ejecutivo(datos)

def generar_informe_tecnico(datos, tipo='pdf'):
    """
    Genera un informe técnico detallado con toda la información
    """
    if tipo == 'pdf':
        return generar_pdf_tecnico(datos)
    else:  # csv
        return generar_csv_tecnico(datos)

def generar_pdf_ejecutivo(datos):
    """
    Genera un PDF con formato ejecutivo, incluyendo gráficos y resúmenes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=72)

    story = []
    styles = getSampleStyleSheet()

    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Informe Ejecutivo de Vulnerabilidades", title_style))
    story.append(Spacer(1, 12))

    # Información del contexto
    context_style = ParagraphStyle(
        'Context',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=20
    )

    # Sede y fecha
    sede_info = f"Sede: {datos.get('sede', 'Todas las sedes')}"
    fecha_info = "Período: "
    if datos.get('fecha_inicio') and datos.get('fecha_fin'):
        fecha_info += f"Del {datos['fecha_inicio']} al {datos['fecha_fin']}"
    elif datos.get('fecha_inicio'):
        fecha_info += f"Desde {datos['fecha_inicio']}"
    elif datos.get('fecha_fin'):
        fecha_info += f"Hasta {datos['fecha_fin']}"
    else:
        fecha_info += "Todo el período"

    story.append(Paragraph(sede_info, context_style))
    story.append(Paragraph(fecha_info, context_style))
    story.append(Paragraph(f"Fecha del informe: {datetime.now().strftime('%Y-%m-%d')}", context_style))
    story.append(Spacer(1, 12))

    # Resumen ejecutivo
    story.append(Paragraph("Resumen Ejecutivo", styles["Heading2"]))
    total_vulnerabilidades = sum(len(host['vulnerabilidades']) for host in datos['hosts_detalle'].values())
    total_hosts = len(datos['hosts_detalle'])
    story.append(Paragraph(f"Total de hosts analizados: {total_hosts}", styles["Normal"]))
    story.append(Paragraph(f"Total de vulnerabilidades identificadas: {total_vulnerabilidades}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Tabla de resumen
    data = [['Nivel', 'Cantidad', '% del Total']]
    niveles = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}

    for host_data in datos['hosts_detalle'].values():
        for vuln in host_data['vulnerabilidades']:
            niveles[vuln['nivel_amenaza']] += 1

    for nivel, cantidad in niveles.items():
        porcentaje = (cantidad / total_vulnerabilidades * 100) if total_vulnerabilidades > 0 else 0
        data.append([nivel, str(cantidad), f"{porcentaje:.1f}%"])

    table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    story.append(table)
    story.append(Spacer(1, 20))

    # Añadir sección de recomendaciones
    story.append(Paragraph("Recomendaciones Prioritarias", styles["Heading2"]))
    if niveles['Critical'] > 0:
        story.append(Paragraph("• Atención inmediata requerida: Se han detectado vulnerabilidades críticas que necesitan ser mitigadas urgentemente.", styles["Normal"]))
    if niveles['High'] > 0:
        story.append(Paragraph("• Plan de acción requerido: Las vulnerabilidades de alto riesgo deben ser abordadas en el corto plazo.", styles["Normal"]))
    story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_csv_ejecutivo(datos):
    """
    Genera un CSV con formato ejecutivo
    """
    buffer = BytesIO()
    
    # Preparar datos para el DataFrame
    rows = []
    for ip, host_data in datos.items():
        for vuln in host_data['vulnerabilidades']:
            rows.append({
                'IP': ip,
                'Nombre Host': host_data['nombre_host'],
                'Vulnerabilidad': vuln['nvt'],
                'Nivel': vuln['nivel_amenaza'],
                'CVSS': vuln['cvss'],
                'Puerto': vuln['puerto']
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return buffer

def generar_pdf_tecnico(datos):
    """
    Genera un PDF con información técnica detallada
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                          rightMargin=36, leftMargin=36,
                          topMargin=36, bottomMargin=36)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("Informe Técnico Detallado", title_style))
    story.append(Spacer(1, 12))
    
    # Contenido detallado por host
    for ip, host_data in datos.items():
        # Información del host
        story.append(Paragraph(f"Host: {ip}", styles["Heading2"]))
        if host_data['nombre_host']:
            story.append(Paragraph(f"Nombre: {host_data['nombre_host']}", styles["Normal"]))
        story.append(Spacer(1, 12))
        
        # Tabla de vulnerabilidades
        vuln_data = [['Vulnerabilidad', 'Nivel', 'CVSS', 'Puerto', 'Estado']]
        for vuln in host_data['vulnerabilidades']:
            vuln_data.append([
                vuln['nvt'],
                vuln['nivel_amenaza'],
                vuln['cvss'],
                vuln['puerto'],
                vuln.get('estado', 'No especificado')
            ])
        
        table = Table(vuln_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Detalles de cada vulnerabilidad
        for vuln in host_data['vulnerabilidades']:
            story.append(Paragraph(f"Detalle de Vulnerabilidad: {vuln['nvt']}", styles["Heading3"]))
            story.append(Paragraph(f"Resumen: {vuln['resumen']}", styles["Normal"]))
            story.append(Paragraph(f"Impacto: {vuln['impacto']}", styles["Normal"]))
            story.append(Paragraph(f"Solución: {vuln['solucion']}", styles["Normal"]))
            if vuln['referencias']:
                story.append(Paragraph("Referencias:", styles["Normal"]))
                for ref in vuln['referencias']:
                    story.append(Paragraph(f"• {ref}", styles["Normal"]))
            story.append(Spacer(1, 12))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generar_csv_tecnico(datos):
    """
    Genera un CSV con información técnica detallada
    """
    buffer = BytesIO()
    
    # Preparar datos para el DataFrame
    rows = []
    for ip, host_data in datos.items():
        for vuln in host_data['vulnerabilidades']:
            rows.append({
                'IP': ip,
                'Nombre Host': host_data['nombre_host'],
                'Vulnerabilidad': vuln['nvt'],
                'OID': vuln['oid'],
                'Nivel': vuln['nivel_amenaza'],
                'CVSS': vuln['cvss'],
                'Puerto': vuln['puerto'],
                'Resumen': vuln['resumen'],
                'Impacto': vuln['impacto'],
                'Solución': vuln['solucion'],
                'Método Detección': vuln['metodo_deteccion'],
                'Referencias': '; '.join(vuln['referencias']) if vuln['referencias'] else '',
                'Estado': vuln.get('estado', 'No especificado')
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(buffer, index=False, encoding='utf-8')
    buffer.seek(0)
    return buffer