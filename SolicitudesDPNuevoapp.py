import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image

st.set_page_config(page_title="Gestión de Solicitudes y Actas - Defensoría", layout="centered")

st.title("⚖️ Módulo de Solicitud de Servicios y Acta de Derechos")
st.markdown("### Portal de Registro y Consentimiento")

# Selección de Vista
vista = st.sidebar.selectbox("Seleccionar Vista:", ["Portal del Ciudadano / Solicitante", "🔒 Panel del Abogado y Supervisor"])

if vista == "Portal del Ciudadano / Solicitante":
    st.markdown("---")
    st.subheader("📋 Información del Proceso (Precargada)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("RUC (Registro Único de Casos):", value="RUC-2026-0042", disabled=True)
        st.text_input("RUS:", value="RUS-2026-8890", disabled=True)
    with col2:
        st.text_input("Despacho Judicial:", value="Juzgado 01 Penal del Circuito de Puerto Berrío", disabled=True)
        st.text_input("Delito Imputado:", value="Fabricación, tráfico y porte de armas", disabled=True)

    st.markdown("---")
    st.subheader("👤 Datos del Solicitante / Procesado")
    
    nombres = st.text_input("Nombres y Apellidos Completos *")
    cc = st.text_input("Cédula de Ciudadanía / Documento de Identidad *")
    telefono = st.text_input("Número de Contacto / Celular *")
    correo = st.text_input("Correo Electrónico (Opcional)")

    st.markdown("---")
    st.subheader("✍️ Firma Digital del Solicitante")
    st.markdown("Firme dentro del recuadro usando su dedo (desde el celular) o el ratón (computador):")

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=150,
        width=450,
        drawing_mode="freedraw",
        key="canvas_firma_usuario",
    )

    st.markdown("---")
    st.subheader("👆 Registro de Huella Dactilar")
    st.markdown("Tome una foto clara de su huella dactilar plasmada en un papel blanco y súbala a continuación:")

    archivo_huella = st.file_uploader("Subir imagen de la huella", type=["png", "jpg", "jpeg"])

    if archivo_huella is not None:
        img_huella = Image.open(archivo_huella)
        st.image(img_huella, caption="Huella cargada con éxito", width=120)

    submitted = st.button("✅ Enviar Solicitud y Acta Firmada", type="primary")

    if submitted:
        if not nombres or not cc or not telefono:
            st.error("Por favor complete todos los campos obligatorios marcados con (*).")
        else:
            st.success("¡Documentos generados y firmados exitosamente!")
            st.balloons()
            st.info("📨 Su información ha sido enviada al despacho del abogado para su respectiva radicación institucional.")

else:
    st.header("🔒 Panel de Control del Despacho (Abogado y Supervisor)")
    st.markdown("### Casos Recibidos Pendientes de Complemento")

    caso_ejemplo = st.selectbox("Seleccionar expediente:", ["[RUC-2026-0042] - JUAN PÉREZ - Porte de Armas"])

    st.markdown("---")
    st.subheader("1. Complemento del Abogado Defensor")
    orientacion_brindada = st.text_area(
        "Tipo de orientación brindada:",
        value="Se efectúa entrevista inicial con el procesado, explicación detallada de los cargos imputados, análisis de elementos materiales probatorios y estructuración de la estrategia defensiva inicial."
    )

    if st.button("Guardar Orientación del Abogado"):
        st.success("Orientación guardada y remitida al supervisor.")

    st.markdown("---")
    st.subheader("2. Decisión Adoptada (Supervisión / Coordinación)")
    
    decision_adoptada = st.selectbox(
        "Seleccionar Decisión:",
        ["Asignación Definitiva de Defensor Público", "Requerimiento de Documentos Adicionales", "Inadmisión de Solicitud"]
    )
    
    observaciones_sup = st.text_area(
        "Observaciones del Supervisor:",
        value="Aprobada la designación conforme a los requisitos legales."
    )

    if st.button("Finalizar y Cerrar Formato Institucional"):
        st.success("🎉 ¡El formato ha quedado 100% diligenciado, firmado, con huella y cerrado institucionalmente!")
        
        # Botón para descargar el acta directamente
        st.download_button(
            label="📥 Descargar Acta Firmada (TXT/PDF)",
            data=f"ACTA DE DERECHOS Y SERVICIOS - DEFENSORÍA PÚBLICA\nDespacho: Juzgado 01 Penal del Circuito de Puerto Berrío\nExpediente: {caso_ejemplo}\nDecision: {decision_adoptada}\nObservaciones: {observaciones_sup}\nEstado: Cerrado y Firmado Institucionalmente.",
            file_name="Acta_Defensoria_Caso.txt",
            mime="text/plain"
        )
