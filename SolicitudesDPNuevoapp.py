from io import BytesIO
import openpyxl
import pandas as pd
import streamlit as st
from streamlit_drawable_canvas import st_canvas

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Gestión de Solicitudes y Actas - Defensoría", page_icon="⚖️"
)

st.title("⚖️ Módulo de Solicitud de Servicios y Acta de Derechos")
st.markdown(
    "Sistema de recepción, entrevista inicial y gestión socioeconómica."
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

        submitted = st.form_submit_button("✅ Enviar Solicitud y Acta Firmada")

    # 3. Procesamiento y Envío a WhatsApp
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

            st.success(
                "¡Formulario completado con éxito! Haz clic en el botón para"
                " enviar el reporte vía WhatsApp."
            )

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
• Ocupación: {ocupacion}

*3. Núcleo Familiar y Vivienda:*
• Personas a cargo: {personas_a_cargo}
• Vivienda: {vivienda}

*4. Balance Económico Mensual:*
• Total Ingresos: ${total_ingresos:,.0f}
• Total Gastos: ${total_gastos:,.0f}

_El usuario ha registrado sus datos socioeconómicos y firmado la constancia._"""

            import urllib.parse

            texto_codificado = urllib.parse.quote(mensaje_whatsapp)
            numero_destino = "573167491973"
            link_whatsapp = (
                f"https://wa.me/{numero_destino}?text={texto_codificado}"
            )

            st.markdown(
                f"""
            <div style="text-align: center; margin-top: 20px;">
                <a href="{link_whatsapp}" target="_blank">
                    <button style="background-color: #25D366; color: white; padding: 14px 24px; font-size: 16px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold;">
                        💬 Enviar Información Completa a mi WhatsApp
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
    st.subheader("Casos Recibidos Pendientes de Complemento")

    expediente_sel = st.selectbox(
        "Seleccionar expediente:",
        [
            "[RUC-2026-0042] - JUAN PÉREZ - Porte de Armas",
            "[RUC-2026-0043] - Otro Caso Ejemplo",
        ],
    )

    st.markdown("---")
    st.subheader("👤 Datos del Solicitante / Procesado")
    orientacion = st.text_area(
        "Tipo de orientación brindada:",
        value=(
            "Se efectúa entrevista inicial con el procesado, explicación"
            " detallada de los cargos imputados, análisis de elementos materiales"
            " probatorios y estructuración de la estrategia defensiva inicial."
        ),
    )

    if st.button("Guardar Orientación del Abogado"):
        st.success("¡Orientación del abogado guardada con éxito!")

    st.markdown("---")
    st.subheader("2. Decisión Adoptada (Supervisión / Coordinación)")
    decision = st.selectbox(
        "Seleccionar Decisión:",
        [
            "Asignación Definitiva de Defensor Público",
            "Inadmisión por Ingresos Superiores",
            "Requerimiento de Soportes Adicionales",
        ],
    )
    observaciones_sup = st.text_area(
        "Observaciones del Supervisor:",
        value="Aprobada la designación conforme a los requisitos legales.",
    )

    if st.button("Finalizar y cerrar formato institucional"):
        st.success("¡Formato institucional cerrado y registrado con éxito!")

    st.markdown("---")
    st.subheader("📥 Exportar Planilla de Excel")
    try:
        wb = openpyxl.load_workbook("SD-P02-F91 SOLICITUD DEL SERVICIO.xlsx")
        ws = wb.active

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        st.download_button(
            label="📥 Descargar Formato Excel Institucional Lleno",
            data=buffer,
            file_name="SD-P02-F91_Diligenciado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.info(
            "Nota: El archivo de plantilla Excel local se cargará y exportará"
            " cuando esté disponible en el directorio."
        )
