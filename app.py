import streamlit as st
import pandas as pd
import os

# Configuración de la App
st.set_page_config(page_title="Rifa VIP Dark", page_icon="🎟️", layout="centered")

# CSS para forzar MODO OSCURO ELEGANTE (Estilo Apple Midnight)
st.markdown("""
    <style>
    /* Fondo principal oscuro profundo */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    /* Encabezados y textos */
    h1, h2, h3, p, span {
        color: #FFFFFF !important;
    }

    /* Estilo de las tarjetas de entrada */
    .stForm, div[data-testid="stExpander"] {
        background-color: #1C1C1E !important;
        border: 1px solid #3A3A3C !important;
        border-radius: 15px !important;
    }

    /* Inputs y campos de texto */
    input, div[data-baseweb="select"] > div {
        background-color: #2C2C2E !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* Cuadrícula de boletos */
    .ticket-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(42px, 1fr)); 
        gap: 6px; 
        margin-top: 20px;
    }
    .t-node { 
        padding: 10px 0; 
        border-radius: 10px; 
        text-align: center; 
        font-size: 0.75rem; 
        font-weight: bold; 
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Colores del Mapa */
    .sold { background-color: #30D158; box-shadow: 0 0 10px rgba(48, 209, 88, 0.3); } /* Verde Neón iOS */
    .pending { background-color: #FF9F0A; box-shadow: 0 0 10px rgba(255, 159, 10, 0.3); } /* Naranja iOS */
    .available { background-color: #3A3A3C; color: #8E8E93; } /* Gris Oscuro */

    /* Botones */
    .stButton>button {
        background-color: #0A84FF !important; /* Azul iOS */
        color: white !important;
        border-radius: 12px !important;
        border: none !important;
        height: 3em !important;
        width: 100% !important;
    }
    
    /* Estilo para el Radio Menú */
    div[data-testid="stMarkdownContainer"] > p { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE DATOS ---
DB_FILE = "rifa_data.csv"
COLUMNAS = ["Boleto", "Nombre", "Telefono", "Estado"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if not all(col in df.columns for col in COLUMNAS):
                return pd.DataFrame(columns=COLUMNAS)
            df["Boleto"] = pd.to_numeric(df["Boleto"], errors='coerce')
            return df
        except:
            return pd.DataFrame(columns=COLUMNAS)
    else:
        return pd.DataFrame(columns=COLUMNAS)

df = load_data()

# --- INTERFAZ ---
st.title("🎟️ Rifa VIP Manager")

# Métricas
if not df.empty:
    total_v = len(df[df["Estado"] == "Pagado"])
    total_p = len(df[df["Estado"] == "Pendiente"])
else:
    total_v = 0
    total_p = 0

total_v_p = total_v + total_p
st.write(f"### Progreso: {total_v_p} / 1000")
st.progress(total_v_p / 1000)

# Menú 
menu = st.radio("Ir a:", ["Registrar", "Gestionar", "Mapa de Boletos", "Descargar"], horizontal=True)

if menu == "Registrar":
    with st.form("reg_form", clear_on_submit=True):
        st.subheader("📝 Nuevo Cliente")
        nombre = st.text_input("Nombre completo")
        tel = st.text_input("WhatsApp")
        estado = st.selectbox("Estado inicial", ["Pagado", "Pendiente"])
        
        ocupados = df["Boleto"].tolist() if not df.empty else []
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        seleccion = st.multiselect("Números de boleto", disponibles)
        
        if st.form_submit_button("REGISTRAR AHORA"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion, "Nombre": [nombre]*len(seleccion),
                    "Telefono": [tel]*len(seleccion), "Estado": [estado]*len(seleccion)
                })
                df = pd.concat([df, nuevos], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ ¡Registro completado!")
                st.rerun()

elif menu == "Gestionar":
    st.subheader("🔍 Administrar Lista")
    if not df.empty:
        search = st.text_input("Buscar por nombre o número...")
        df_view = df[df["Nombre"].str.contains(search, case=False, na=False) | df["Boleto"].astype(str).contains(search)] if search else df.sort_values("Boleto", ascending=False).head(10)

        for index, row in df_view.iterrows():
            with st.expander(f"📌 {int(row['Boleto'])} - {row['Nombre']}"):
                with st.form(f"f_{index}"):
                    n_nom = st.text_input("Nombre", value=row["Nombre"])
                    n_est = st.selectbox("Estado", ["Pagado", "Pendiente"], index=0 if row["Estado"]=="Pagado" else 1)
                    col1, col2 = st.columns(2)
                    if col1.form_submit_button("💾 Actualizar"):
                        df.at[index, "Nombre"] = n_nom
                        df.at[index, "Estado"] = n_est
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
                    if col2.form_submit_button("🗑️ Borrar"):
                        df = df.drop(index)
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
    else:
        st.info("No hay registros.")

elif menu == "Mapa de Boletos":
    st.subheader("📍 Estado de la Hoja")
    st.write("🟢 Pagado | 🟠 Pendiente | ⚫ Libre")
    color_map = dict(zip(df.Boleto, df.Estado)) if not df.empty else {}
    grid_html = '<div class="ticket-grid">'
    for i in range(1, 1001):
        est = color_map.get(i, "Libre")
        clase = "sold" if est == "Pagado" else "pending" if est == "Pendiente" else "available"
        grid_html += f'<div class="t-node {clase}">{i}</div>'
    st.markdown(grid_html + '</div>', unsafe_allow_html=True)

elif menu == "Descargar":
    st.subheader("💾 Backup de Seguridad")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar CSV para Excel", data=csv, file_name='rifa_respaldo.csv', mime='text/csv')
