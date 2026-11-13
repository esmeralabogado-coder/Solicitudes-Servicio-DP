from io import BytesIO
import os
import openpyxl
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# Librerías de ReportLab para la generación del PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Gestión de Solicitudes y Actas - Defensoría", page_icon="⚖️"
)

st.title("⚖️ Módulo de Solicitud de Servicios y Acta de Derechos")
st.markdown(
    "Sistema de recepción, entrevista inicial, firma digital y generación de"
    " PDF institucional."
)

# --- Menú de Selección de Vista ---
vista = st.sidebar.selectbox(
    "Seleccionar Vista:",
    ["Portal del Ciudadano (Formulario)", "Panel del Abogado y Supervisor"],
)

# ==========================================
# VISTA 1: FORMULARIO DEL CIUDADANO
# ==========================================
if vista == "Portal del Ciudadano (Formulario)":
    st.header("Portal de Registro y Consentimiento")
    st.markdown(
        "Por favor, complete cada una de las secciones con información verídica"
        " y firme al final."
    )

    # 1. Información del Proceso (Control Interno del Abogado)
    with st.expander(
        "📂 Información del Proceso (Uso exclusivo / Precargada)", expanded=False
    ):
        col1, col2 = st.columns(2)
        with col1:
            ruc = st.text_input(
                "RUC (Registro Único de Casos)", value="RUC-2026-0042"
            )
            rus = st.text_input("RUS", value="RUS-2026-8890")
        with col2:
            despacho = st.text_input(
                "Despacho Judicial",
                value="Juzgado 01 Penal del Circuito de Puerto Berrío",
            )
            delito = st.text_input(
                "Delito Imputado", value="Fabricación, tráfico y porte de armas"
            )

    st.markdown("---")

    # 2. Formulario Completo para el Solicitante
    with st.form("form_solicitud_completa"):

        # SECCIÓN A: Datos Personales
        st.subheader("👤 A. Datos Personales y de Ubicación")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            nombres = st.text_input("Nombres y Apellidos Completos *")
            cedula = st.text_input("Cédula de Ciudadanía / Documento *")
            edad = st.number_input("Edad", min_value=18, max_value=110, value=30)
        with col_a2:
            celular = st.text_input("Número de Contacto / Celular *")
            direccion = st.text_input("Dirección de Residencia y Barrio *")
            ocupacion = st.text_input("Ocupación u Oficio Actual")

        # SECCIÓN B: Núcleo Familiar
        st.subheader("👨‍👩‍👧‍👦 B. Composición del Núcleo Familiar")
        personas_a_cargo = st.number_input(
            "Número de personas que dependen económicamente de usted",
            min_value=0,
            max_value=15,
            value=0,
        )
        vivienda = st.selectbox(
            "Condición de Vivienda",
            ("Propia", "Alquilada", "Familiar", "Invasión / Otra"),
        )

        # SECCIÓN C: Ingresos y Gastos Mensuales
        st.subheader(
            "💰 C. Información Económica (Ingresos y Gastos Mensuales)"
        )
        st.markdown(
            "_Indique valores aproximados en pesos colombianos (COP) mes._"
        )

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown("**Ingresos**")
            ingreso_salario = st.number_input(
                "Salario o ingresos por trabajo mensual",
                min_value=0,
                value=0,
                step=50000,
            )
            ingreso_otros = st.number_input(
                "Otros ingresos (ventas, ayudas, etc.)",
                min_value=0,
                value=0,
                step=50000,
            )
        with col_e2:
            st.markdown("**Gastos**")
            gasto_arriendo = st.number_input(
                "Gastos en arriendo / vivienda",
                min_value=0,
                value=0,
                step=50000,
            )
            gasto_servicios = st.number_input(
                "Gastos en servicios públicos", min_value=0, value=0, step=20000
            )
            gasto_alimentacion = st.number_input(
                "Gastos en alimentación", min_value=0, value=0, step=50000
            )

        # SECCIÓN D: Declaración y Firma
        st.subheader("✍️ D. Constancia de Fe y Firma Digital")
        st.markdown(
            "Manifiesto bajo gravedad de juramento que los datos aquí"
            " suministrados son verídicos."
        )

        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 1)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=140,
            width=340,
            drawing_mode="freedraw",
            key="canvas_firma",
        )

        submitted = st.form_submit_button("✅ Enviar Solicitud y Generar PDF")

    # 3. Procesamiento y Generación de PDF / WhatsApp
    if submitted:
        if not nombres or not cedula or not celular or not direccion:
            st.error(
                "⚠️ Por favor complete todos los campos obligatorios marcados"
                " con asterisco (*)."
            )
        else:
            total_ingresos = ingreso_salario + ingreso_otros
            total_gastos = (
                gasto_arriendo + gasto_servicios + gasto_alimentacion
            )

            # Guardar la firma temporalmente si el usuario dibujó algo
            firma_path = None
            if (
                canvas_result.image_data is not None
                and canvas_result.image_data.any()
            ):
                img_array = canvas_result.image_data
                img = Image.fromarray(img_array.astype("uint8"), mode="RGBA")
                # Convertir transparente a blanco para el PDF
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                firma_path = "firma_temp.png"
                background.save(firma_path)

            # Función para generar el PDF institucional
            def generar_pdf_acta(
                filename,
                ruc,
                rus,
                despacho,
                delito,
                nombres,
                cedula,
                edad,
                celular,
                direccion,
                ocupacion,
                personas_a_cargo,
                vivienda,
                total_ingresos,
                total_gastos,
                firma_img,
            ):
                doc = SimpleDocTemplate(filename, pagesize=letter)
                story = []
                from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

                styles = getSampleStyleSheet()

                # Títulos y Encabezado
                story.append(
                    Paragraph(
                        "<b>DEFENSORÍA PÚBLICA - COLOMBIA</b>", styles["Title"]
                    )
                )
                story.append(
                    Paragraph(
                        "<b>Formato de Solicitud de Servicios y Acta de"
                        " Derechos</b>",
                        styles["Heading2"],
                    )
                )
                story.append(Spacer(1, 12))

                # Contenido del Acta
                texto_contenido = f"""
                <b>1. Información del Proceso:</b><br/>
                • RUC: {ruc} | RUS: {rus}<br/>
                • Despacho: {despacho}<br/>
                • Delito Imputado: {delito}<br/><br/>
                
                <b>2. Datos Personales del Solicitante:</b><br/>
                • Nombre: {nombres}<br/>
                • Cédula: {cedula} (Edad: {edad})<br/>
                • Celular: {celular}<br/>
                • Dirección: {direccion}<br/>
                • Ocupación: {ocupacion}<br/><br/>
                
                <b>3. Núcleo Familiar y Vivienda:</b><br/>
                • Personas a cargo: {personas_a_cargo}<br/>
                • Condición de Vivienda: {vivienda}<br/><br/>
                
                <b>4. Balance Económico Mensual:</b><br/>
                • Total Ingresos: ${total_ingresos:,.0f} COP<br/>
                • Total Gastos: ${total_gastos:,.0f} COP<br/><br/>
                
                <b>5. Constancia y Declaración:</b><br/>
                Manifiesto bajo gravedad de juramento que la información aquí"
                " consignada es verídica y autorizo el trámite ante la"
                " Defensoría Pública.<br/><br/>
                """
                story.append(
                    Paragraph(texto_contenido, styles["Normal"])
                )
                story.append(Spacer(1, 20))

                # Insertar Firma si existe
                if firma_img and os.path.exists(firma_img):
                    from reportlab.platypus import Image as RLImage

                    story.append(
                        Paragraph("<b>Firma del Solicitante:</b>", styles["Normal"])
                    )
                    story.append(Spacer(1, 5))
                    story.append(
                        RLImage(firma_img, width=200, height=80)
                    )

                doc.build(story)

            pdf_filename = f"Solicitud_Defensoria_{cedula}.pdf"
            generar_pdf_acta(
                pdf_filename,
                ruc,
                rus,
                despacho,
                delito,
                nombres,
                cedula,
                edad,
                celular,
                direccion,
                ocupacion,
                personas_a_cargo,
                vivienda,
                total_ingresos,
                total_gastos,
                firma_path,
            )

            st.success(
                "¡Formulario procesado y acta PDF generada con éxito!"
            )

            # Botón de Descarga del PDF Directo
            with open(pdf_filename, "rb") as pdf_file:
                bytes_pdf = pdf_file.read()
                st.download_button(
                    label="📥 Descargar Acta Firmada en PDF",
                    data=bytes_pdf,
                    file_name=pdf_filename,
                    mime="application/pdf",
                )

            # Mensaje para WhatsApp
            mensaje_whatsapp = f"""*⚖️ SOLICITUD DE SERVICIOS - DEFENSORÍA PÚBLICA*

*1. Proceso:*
• RUC: {ruc} | RUS: {rus}
• Despacho: {despacho}
• Delito: {delito}

*2. Datos Personales:*
• Nombre: {nombres}
• Cédula: {cedula} (Edad: {edad})
• Celular: {celular}
• Dirección: {direccion}

*3. Balance Económico:*
• Ingresos: ${total_ingresos:,.0f} | Gastos: ${total_gastos:,.0f}

_El usuario ha firmado la constancia y generado su PDF oficial._"""

            import urllib.parse

            texto_codificado = urllib.parse.quote(mensaje_whatsapp)
            link_whatsapp = f"https://wa.me/573167491973?text={texto_codificado}"

            st.markdown(
                f"""
            <div style="text-align: center; margin-top: 20px;">
                <a href="{link_whatsapp}" target="_blank">
                    <button style="background-color: #25D366; color: white; padding: 14px 24px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                        💬 Enviar Resumen a mi WhatsApp
                    </button>
                </a>
            </div>
            """,
                unsafe_allow_html=True,
            )

# ==========================================
# VISTA 2: PANEL DEL ABOGADO Y SUPERVISOR
# ==========================================
elif vista == "Panel del Abogado y Supervisor":
    st.header("🔒 Panel de Control del Despacho (Abogado y Supervisor)")
    st.subheader("Casos Recibidos y Exportación Excel")

    try:
        wb = openpyxl.load_workbook("SD-P02-F91 SOLICITUD DEL SERVICIO.xlsx")
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        st.download_button(
            label="📥 Descargar Formato Excel Institucional",
            data=buffer,
            file_name="SD-P02-F91_Diligenciado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.info("La plantilla de Excel se exportará al estar disponible.")
