import streamlit as st
import pandas as pd
import os

# Configuración que se adapta al sistema (Claro/Oscuro)
st.set_page_config(page_title="Rifa Pro", page_icon="📱", layout="centered")

# CSS para que parezca App Nativa
st.markdown("""
    <style>
    /* Estética de bordes redondeados y fuentes limpias */
    .stApp { border-radius: 15px; }
    
    /* Botones grandes para dedos */
    .stButton>button {
        height: 3em;
        border-radius: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Cuadrícula de boletos compacta para móvil */
    .ticket-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(45px, 1fr));
        gap: 5px;
        margin-top: 10px;
    }
    
    .t-node {
        padding: 10px 5px;
        border-radius: 8px;
        text-align: center;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    /* Colores modo claro/oscuro se manejan por el sistema de Streamlit */
    .sold { background-color: #FF3B30; color: white; }
    .available { background-color: #34C759; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- BASE DE DATOS ---
DB_FILE = "rifa_data.csv"
if not os.path.exists(DB_FILE):
    df = pd.DataFrame(columns=["Boleto", "Nombre", "Teléfono"])
    df.to_csv(DB_FILE, index=False)

df = pd.read_csv(DB_FILE)
df["Boleto"] = df["Boleto"].astype(int)

# --- LÓGICA ---
total_boletos = 1000
vendidos = len(df)
porcentaje = (vendidos / total_boletos)

# --- INTERFAZ MÓVIL ---
st.title("🎟️ Mi Rifa")

# Card de Resumen
with st.container():
    col1, col2 = st.columns(2)
    col1.metric("Vendidos", f"{vendidos}")
    col2.metric("Disponibles", f"{total_boletos - vendidos}")
    st.progress(porcentaje)
    st.caption(f"Progreso actual: {porcentaje*100:.1f}%")

# Formulario optimizado
with st.expander("➕ NUEVO REGISTRO", expanded=False):
    with st.form("registro"):
        nombre = st.text_input("👤 Nombre")
        tel = st.text_input("📞 Teléfono")
        
        ocupados = df["Boleto"].tolist()
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        
        # Multiselect más amigable
        seleccion = st.multiselect("🔢 Elige números:", disponibles)
        
        if st.form_submit_button("GUARDAR REGISTRO"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion,
                    "Nombre": [nombre] * len(seleccion),
                    "Teléfono": [tel] * len(seleccion)
                })
                df = pd.concat([df, nuevos], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Guardado!")
                st.rerun()

# Pestañas inferiores (estilo barra de navegación)
menu = st.radio("Ver:", ["Lista", "Mapa 1-1000"], horizontal=True)

if menu == "Lista":
    search = st.text_input("🔍 Buscar nombre...")
    if not df.empty:
        filtered_df = df[df["Nombre"].str.contains(search, case=False)] if search else df
        st.dataframe(filtered_df.sort_values("Boleto", ascending=False), use_container_width=True)
    else:
        st.info("No hay ventas.")

else:
    st.write("### Estado de Boletos")
    # Generar el mapa visual
    ticket_html = '<div class="ticket-grid">'
    for i in range(1, 1001):
        clase = "sold" if i in ocupados else "available"
        ticket_html += f'<div class="t-node {clase}">{i}</div>'
    ticket_html += '</div>'
    st.markdown(ticket_html, unsafe_allow_html=True)
