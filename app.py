import streamlit as st
import pandas as pd
import os

# Configuración de la App
st.set_page_config(page_title="Rifa VIP Dark", page_icon="🎟️", layout="centered")

# CSS para MODO OSCURO (Midnight Apple)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    .stForm, div[data-testid="stExpander"] {
        background-color: #1C1C1E !important;
        border: 1px solid #3A3A3C !important;
        border-radius: 15px !important;
    }
    .ticket-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(42px, 1fr)); 
        gap: 6px; 
    }
    .t-node { 
        padding: 10px 0; border-radius: 10px; text-align: center; 
        font-size: 0.75rem; font-weight: bold; color: white;
    }
    .sold { background-color: #30D158; } 
    .pending { background-color: #FF9F0A; } 
    .available { background-color: #3A3A3C; color: #8E8E93; }
    .stButton>button {
        background-color: #0A84FF !important;
        color: white !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DB_FILE = "rifa_data.csv"
COLUMNAS = ["Boleto", "Nombre", "Telefono", "Estado"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            temp_df = pd.read_csv(DB_FILE)
            if temp_df.empty:
                return pd.DataFrame(columns=COLUMNAS)
            return temp_df
        except:
            return pd.DataFrame(columns=COLUMNAS)
    return pd.DataFrame(columns=COLUMNAS)

df = load_data()

# --- INTERFAZ ---
st.title("🎟️ Rifa VIP")

# Métricas
total_v = 0
total_p = 0
if not df.empty and "Estado" in df.columns:
    total_v = len(df[df["Estado"] == "Pagado"])
    total_p = len(df[df["Estado"] == "Pendiente"])

st.write(f"📊 **Ventas:** {total_v + total_p} / 1000")
st.progress((total_v + total_p) / 1000)

menu = st.radio("Menú:", ["Registrar", "Gestionar", "Mapa", "Respaldo"], horizontal=True)

if menu == "Registrar":
    with st.form("reg_form", clear_on_submit=True):
        st.subheader("📝 Nuevo Registro")
        nombre = st.text_input("Nombre")
        tel = st.text_input("WhatsApp")
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])
        
        ocupados = []
        if not df.empty and "Boleto" in df.columns:
            ocupados = df["Boleto"].dropna().tolist()
        
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        seleccion = st.multiselect("Toca para elegir números:", disponibles)
        
        if st.form_submit_button("FINALIZAR REGISTRO"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion, 
                    "Nombre": [nombre]*len(seleccion),
                    "Telefono": [tel]*len(seleccion), 
                    "Estado": [estado]*len(seleccion)
                })
                df = pd.concat([df, nuevos], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ ¡Registrado!")
                st.rerun()

elif menu == "Gestionar":
    st.subheader("🔍 Editar")
    if not df.empty:
        search = st.text_input("Buscar por nombre o número...")
        
        # Lógica de filtrado corregida
        df_view = df.copy()
        if search:
            mask = df_view["Nombre"].str.contains(search, case=False, na=False) | \
                   df_view["Boleto"].astype(str).contains(search)
            df_view = df_view[mask]
        
        # Ordenar solo si hay datos para evitar el AttributeError
        if not df_view.empty:
            df_view = df_view.sort_values("Boleto", ascending=False)
            
            for index, row in df_view.head(20).iterrows():
                with st.expander(f"Boleto {int(row['Boleto'])} - {row['Nombre']}"):
                    with st.form(f"f_{index}"):
                        n_nom = st.text_input("Nombre", value=row["Nombre"])
                        n_est = st.selectbox("Estado", ["Pagado", "Pendiente"], index=0 if row["Estado"]=="Pagado" else 1)
                        c1, c2 = st.columns(2)
                        if c1.form_submit_button("💾 Guardar"):
                            df.at[index, "Nombre"] = n_nom
                            df.at[index, "Estado"] = n_est
                            df.to_csv(DB_FILE, index=False)
                            st.rerun()
                        if c2.form_submit_button("🗑️ Borrar"):
                            df = df.drop(index)
                            df.to_csv(DB_FILE, index=False)
                            st.rerun()
        else:
            st.warning("No se encontraron resultados.")
    else:
        st.info("No hay registros aún.")

elif menu == "Mapa":
    st.subheader("📍 Estado de Boletos")
    color_map = {}
    if not df.empty:
        color_map = dict(zip(df.Boleto, df.Estado))
        
    grid_html = '<div class="ticket-grid">'
    for i in range(1, 1001):
        est = color_map.get(i, "Libre")
        clase = "sold" if est == "Pagado" else "pending" if est == "Pendiente" else "available"
        grid_html += f'<div class="t-node {clase}">{i}</div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

elif menu == "Respaldo":
    st.subheader("💾 Guardar Copia")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar Respaldo", data=csv, file_name='rifa_data.csv')
