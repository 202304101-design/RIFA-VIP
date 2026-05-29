import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la App
st.set_page_config(page_title="Rifa VIP Pro", page_icon="🎟️", layout="centered")

# Estilos estilo Apple / Móvil
st.markdown("""
    <style>
    .stApp { background-color: #F2F2F7; }
    .ticket-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); 
        gap: 5px; 
    }
    .t-node { 
        padding: 8px 0; 
        border-radius: 8px; 
        text-align: center; 
        font-size: 0.7rem; 
        font-weight: bold; 
        color: white;
    }
    .sold { background-color: #34C759; } 
    .pending { background-color: #FF9500; } 
    .available { background-color: #AEAEB2; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # ttl=0 asegura que siempre traiga los datos más nuevos del Excel
    return conn.read(ttl=0)

try:
    df = load_data()
    # Limpieza de datos básica
    if not df.empty:
        df = df.dropna(how='all')
        df["Boleto"] = pd.to_numeric(df["Boleto"], errors='coerce')
except:
    df = pd.DataFrame(columns=["Boleto", "Nombre", "Telefono", "Estado"])

# --- LÓGICA DE INTERFAZ ---
st.title("🎟️ Control de Rifa 1000")

# Resumen rápido
total_v = len(df[df["Estado"] == "Pagado"]) if not df.empty else 0
total_p = len(df[df["Estado"] == "Pendiente"]) if not df.empty else 0
st.progress((total_v + total_p) / 1000)
st.write(f"📊 **{total_v}** Pagados | **{total_p}** Pendientes | **{1000 - (total_v+total_p)}** Libres")

# Menú inferior
menu = st.radio("Acción:", ["Registrar", "Gestionar", "Mapa"], horizontal=True)

if menu == "Registrar":
    with st.form("reg_form", clear_on_submit=True):
        st.subheader("Nuevo Registro")
        nombre = st.text_input("👤 Nombre")
        tel = st.text_input("📞 Teléfono")
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])
        
        ocupados = df["Boleto"].tolist() if not df.empty else []
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        seleccion = st.multiselect("🔢 Números", disponibles)
        
        if st.form_submit_button("Guardar en Google Sheets"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion,
                    "Nombre": [nombre] * len(seleccion),
                    "Telefono": [tel] * len(seleccion),
                    "Estado": [estado] * len(seleccion)
                })
                # Combinar y subir
                updated_df = pd.concat([df, nuevos], ignore_index=True)
                conn.update(data=updated_df)
                st.success("✅ Guardado correctamente")
                st.rerun()
            else:
                st.warning("Completa nombre y números")

elif menu == "Gestionar":
    st.subheader("🔍 Editar o Eliminar")
    if not df.empty:
        search = st.text_input("Buscar nombre o número")
        if search:
            mask = df["Nombre"].str.contains(search, case=False, na=False) | df["Boleto"].astype(str).contains(search)
            df_view = df[mask]
        else:
            df_view = df.sort_values("Boleto", ascending=False).head(15)

        for index, row in df_view.iterrows():
            with st.expander(f"Boleto {int(row['Boleto'])} - {row['Nombre']}"):
                with st.form(f"f_{index}"):
                    n_nom = st.text_input("Nombre", value=row["Nombre"])
                    n_tel = st.text_input("Teléfono", value=row["Telefono"])
                    n_est = st.selectbox("Estado", ["Pagado", "Pendiente"], index=0 if row["Estado"]=="Pagado" else 1)
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Actualizar"):
                        df.at[index, "Nombre"] = n_nom
                        df.at[index, "Telefono"] = n_tel
                        df.at[index, "Estado"] = n_est
                        conn.update(data=df)
                        st.rerun()
                    if c2.form_submit_button("🗑️ Eliminar"):
                        df = df.drop(index)
                        conn.update(data=df)
                        st.rerun()
    else:
        st.info("No hay registros aún")

elif menu == "Mapa":
    st.subheader("📍 Mapa de Boletos")
    st.caption("🟢 Pagado | 🟠 Pendiente | ⚪ Libre")
    
    # Crear diccionario para colores
    color_map = dict(zip(df.Boleto, df.Estado)) if not df.empty else {}
    
    grid_html = '<div class="ticket-grid">'
    for i in range(1, 1001):
        est = color_map.get(i, "Libre")
        clase = "sold" if est == "Pagado" else "pending" if est == "Pendiente" else "available"
        grid_html += f'<div class="t-node {clase}">{i}</div>'
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)
