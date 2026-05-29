import streamlit as st
import pandas as pd
import os

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

# --- BASE DE DATOS LOCAL ---
DB_FILE = "rifa_data.csv"

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Boleto"] = pd.to_numeric(df["Boleto"], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["Boleto", "Nombre", "Telefono", "Estado"])

df = load_data()

# --- LÓGICA DE INTERFAZ ---
st.title("🎟️ Mi Control de Rifa")

# Resumen rápido
total_v = len(df[df["Estado"] == "Pagado"]) if not df.empty else 0
total_p = len(df[df["Estado"] == "Pendiente"]) if not df.empty else 0
total_v_p = total_v + total_p
st.progress(total_v_p / 1000)
st.write(f"📊 **{total_v}** Pagados | **{total_p}** Pendientes | **{1000 - total_v_p}** Libres")

# Menú inferior
menu = st.radio("Acción:", ["Registrar", "Gestionar", "Mapa", "Respaldo"], horizontal=True)

if menu == "Registrar":
    with st.form("reg_form", clear_on_submit=True):
        st.subheader("Nuevo Registro")
        nombre = st.text_input("👤 Nombre")
        tel = st.text_input("📞 Teléfono")
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])
        
        ocupados = df["Boleto"].tolist() if not df.empty else []
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        seleccion = st.multiselect("🔢 Números", disponibles)
        
        if st.form_submit_button("Guardar Registro"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion,
                    "Nombre": [nombre] * len(seleccion),
                    "Telefono": [tel] * len(seleccion),
                    "Estado": [estado] * len(seleccion)
                })
                df = pd.concat([df, nuevos], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ Guardado en el teléfono")
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
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
                    if c2.form_submit_button("🗑️ Eliminar"):
                        df = df.drop(index)
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
    else:
        st.info("No hay registros aún")

elif menu == "Mapa":
    st.subheader("📍 Mapa de Boletos")
    color_map = dict(zip(df.Boleto, df.Estado)) if not df.empty else {}
    grid_html = '<div class="ticket-grid">'
    for i in range(1, 1001):
        est = color_map.get(i, "Libre")
        clase = "sold" if est == "Pagado" else "pending" if est == "Pendiente" else "available"
        grid_html += f'<div class="t-node {clase}">{i}</div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

elif menu == "Respaldo":
    st.subheader("💾 Descargar Datos")
    st.write("Usa este botón para guardar una copia de tu lista en tu teléfono.")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Excel (CSV)",
            data=csv,
            file_name='rifa_backup.csv',
            mime='text/csv',
        )
    else:
        st.warning("No hay datos para descargar.")
