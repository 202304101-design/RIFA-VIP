import streamlit as st
import pandas as pd
import os

# Configuración estética estilo Apple
st.set_page_config(page_title="Rifa Manager", page_icon="🎟️", layout="centered")

# Estilo personalizado (CSS) para mayor elegancia
st.markdown("""
    <style>
    .main { background-color: #f5f5f7; }
    .stButton>button {
        border-radius: 20px;
        background-color: #007aff;
        color: white;
        border: none;
        width: 100%;
    }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎟️ Registro de Rifa")

# Base de datos simple en CSV
DB_FILE = "participantes.csv"
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Nombre", "Boletos", "Teléfono"])
    df.to_csv(DB_FILE, index=False)

# Cargar datos
df = pd.read_csv(DB_FILE)

# --- SECCIÓN DE REGISTRO ---
with st.expander("Añadir Nuevo Participante", expanded=True):
    nombre = st.text_input("Nombre Completo")
    col1, col2 = st.columns(2)
    with col1:
        cantidad = st.number_input("Cantidad de Boletos", min_value=1, max_value=1000, step=1)
    with col2:
        tel = st.text_input("Teléfono (WhatsApp)")
    
    if st.button("Registrar en la Lista"):
        if nombre and tel:
            nuevo_registro = pd.DataFrame([[nombre, cantidad, tel]], columns=["Nombre", "Boletos", "Teléfono"])
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success(f"¡{nombre} registrado con éxito!")
            st.rerun()

# --- ESTADÍSTICAS ---
boletos_vendidos = df["Boletos"].sum()
progreso = min(boletos_vendidos / 1000, 1.0)

st.subheader(f"Progreso: {boletos_vendidos} / 1000 boletos")
st.progress(progreso)

# --- LISTA DE REGISTRADOS ---
st.subheader("Lista de Participantes")
if not df.empty:
    # Mostramos la lista invertida para ver los últimos registros arriba
    st.dataframe(df.iloc[::-1], use_container_width=True)
else:
    st.info("Aún no hay nadie registrado.")
