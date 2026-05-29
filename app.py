import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de la App (Estilo iOS)
st.set_page_config(page_title="Rifa Pro Cloud", page_icon="🎟️", layout="centered")

# Estilos CSS para el mapa de boletos y botones grandes
st.markdown("""
    <style>
    .stApp { background-color: #F2F2F7; }
    .ticket-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(40px, 1fr)); 
        gap: 5px; 
        margin-top: 15px;
    }
    .t-node { 
        padding: 10px 2px; 
        border-radius: 8px; 
        text-align: center; 
        font-size: 0.75rem; 
        font-weight: bold; 
        color: white;
    }
    .sold { background-color: #34C759; } /* Verde - Pagado */
    .pending { background-color: #FF9500; } /* Naranja - Pendiente */
    .available { background-color: #AEAEB2; } /* Gris - Libre */
    
    /* Estilo para los botones del menú */
    div.stButtonGroup > button {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # ttl=0 para que no guarde caché y siempre lea lo último del Excel
    return conn.read(ttl=0)

df = load_data()

# Asegurar que la columna Boleto sea numérica para evitar errores de búsqueda
if not df.empty:
    df["Boleto"] = pd.to_numeric(df["Boleto"], errors='coerce')
    df = df.dropna(subset=["Boleto"])

# --- INTERFAZ ---
st.title("🎟️ Mi Control de Rifa")

# Resumen de ventas
total_boletos = 1000
vendidos_pagados = len(df[df["Estado"] == "Pagado"]) if not df.empty else 0
vendidos_pendientes = len(df[df["Estado"] == "Pendiente"]) if not df.empty else 0
total_vendidos = vendidos_pagados + vendidos_pendientes

st.metric("Total Vendidos", f"{total_vendidos} / {total_boletos}")
st.progress(total_vendidos / total_boletos)
st.write(f"✅ Pagados: **{vendidos_pagados}** | ⏳ Pendientes: **{vendidos_pendientes}**")

# Menú de Navegación (Optimizado para móvil)
menu = st.radio("Acciones:", ["Registrar", "Gestionar", "Mapa 1-1000"], horizontal=True)

# 1. SECCIÓN REGISTRAR
if menu == "Registrar":
    with st.container(border=True):
        st.subheader("📝 Nuevo Registro")
        with st.form("registro_form", clear_on_submit=True):
            nombre = st.text_input("👤 Nombre del Cliente")
            tel = st.text_input("📞 Teléfono (WhatsApp)")
            estado = st.selectbox("Estado del Pago", ["Pagado", "Pendiente"])
            
            ocupados = df["Boleto"].tolist() if not df.empty else []
            disponibles = [i for i in range(1, 1001) if i not in ocupados]
            seleccion = st.multiselect("🔢 Selecciona los números:", disponibles)
            
            if st.form_submit_button("Guardar en la Nube"):
                if nombre and seleccion:
                    # Crear nuevos registros
                    nuevos_datos = pd.DataFrame({
                        "Boleto": seleccion,
                        "Nombre": [nombre] * len(seleccion),
                        "Telefono": [tel] * len(seleccion),
                        "Estado": [estado] * len(seleccion)
                    })
                    updated_df = pd.concat([df, nuevos_datos], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success(f"¡{len(seleccion)} boletos registrados con éxito!")
                    st.rerun()
                else:
                    st.error("Falta el nombre o los números de boleto.")

# 2. SECCIÓN GESTIONAR (CRUD)
elif menu == "Gestionar":
    st.subheader("🔍 Editar o Borrar")
    if not df.empty:
        search = st.text_input("Buscar por nombre o número:")
        if search:
            df_view = df[df["Nombre"].str.contains(search, case=False) | df["Boleto"].astype(str).contains(search)]
        else:
            df_view = df.sort_values("Boleto", ascending=False).head(10) # Mostrar los últimos 10
            st.caption("Mostrando los últimos 10 registros...")

        for index, row in df_view.iterrows():
            with st.expander(f"Boleto {int(row['Boleto'])} - {row['Nombre']}"):
                with st.form(f"edit_{index}"):
                    nuevo_nombre = st.text_input("Nombre", value=row["Nombre"])
                    nuevo_tel = st.text_input("Teléfono", value=row["Telefono"])
                    nuevo_estado = st.selectbox("Estado", ["Pagado", "Pendiente"], 
                                               index=0 if row["Estado"]=="Pagado" else 1)
                    
                    c1, c2 = st.columns(2)
                    if c1.form_submit_button("💾 Guardar"):
                        df.at[index, "Nombre"] = nuevo_nombre
                        df.at[index, "Telefono"] = nuevo_tel
                        df.at[index, "Estado"] = nuevo_estado
                        conn.update(data=df)
                        st.success("Actualizado")
                        st.rerun()
                    
                    if c2.form_submit_button("🗑️ Eliminar"):
                        df = df.drop(index)
                        conn.update(data=df)
                        st.warning("Eliminado")
                        st.rerun()
    else:
        st.info("Aún no hay nadie registrado.")

# 3. SECCIÓN MAPA
else:
    st.subheader("🗺️ Mapa de la Rifa")
    st.write("🟢 Pagado | 🟠 Pendiente | ⚪ Disponible")
    
    # Diccionario rápido para colorear el mapa
    estados_map = dict(zip(df.Boleto, df.Estado)) if not df.empty else {}
    
    html_map = '<div class="ticket-grid">'
    for i in range(1, 1001):
        est = estados_map.get(i, "Libre")
        clase = "sold" if est == "Pagado" else "pending" if est == "Pendiente" else "available"
        html_map += f'<div class="t-node {clase}">{i}</div>'
    html_map += '</div>'
    st.markdown(html_map, unsafe_allow_html=True)
