import streamlit as st
import pandas as pd
import os

# Configuración de la App
st.set_page_config(page_title="Rifa VIP Dark", page_icon="🎟️", layout="centered")

# CSS para MODO OSCURO y Bloqueo de scroll innecesario en móviles
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Estilo de las tarjetas */
    .stForm, div[data-testid="stExpander"] {
        background-color: #1C1C1E !important;
        border: 1px solid #3A3A3C !important;
        border-radius: 15px !important;
    }

    /* Ajuste para que el multiselect no sea un campo de texto gigante */
    div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    /* Cuadrícula de boletos */
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

    /* Botones estilo iOS */
    .stButton>button {
        background-color: #0A84FF !important;
        color: white !important;
        border-radius: 12px !important;
        height: 3.5em !important;
        font-weight: bold !important;
    }
    
    /* Ocultar barra de herramientas de gráficos si existiera */
    details { display: none !important; }
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
    return pd.DataFrame(columns=COLUMNAS)

df = load_data()

# --- INTERFAZ ---
st.title("🎟️ Rifa VIP")

# Métricas
total_v = len(df[df["Estado"] == "Pagado"]) if not df.empty else 0
total_p = len(df[df["Estado"] == "Pendiente"]) if not df.empty else 0
st.write(f"📊 **Ventas:** {total_v + total_p} / 1000")
st.progress((total_v + total_p) / 1000)

menu = st.radio("Menú:", ["Registrar", "Gestionar", "Mapa", "Respaldo"], horizontal=True)

if menu == "Registrar":
    with st.form("reg_form", clear_on_submit=True):
        st.subheader("📝 Nuevo Registro")
        nombre = st.text_input("Nombre")
        tel = st.text_input("WhatsApp")
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])
        
        # Lógica de boletos disponibles
        ocupados = df["Boleto"].tolist() if not df.empty else []
        disponibles = [i for i in range(1, 1001) if i not in ocupados]
        
        # Selección de boletos (Multiselect)
        # Nota: En móviles, al tocarlo se abrirá la lista de opciones.
        seleccion = st.multiselect("Toca para elegir números:", disponibles)
        
        if st.form_submit_button("FINALIZAR REGISTRO"):
            if nombre and seleccion:
                nuevos = pd.DataFrame({
                    "Boleto": seleccion, "Nombre": [nombre]*len(seleccion),
                    "Telefono": [tel]*len(seleccion), "Estado": [estado]*len(seleccion)
                })
                df = pd.concat([df, nuevos], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("✅ ¡Registrado!")
                st.rerun()

elif menu == "Gestionar":
    st.subheader("🔍 Editar")
    if not df.empty:
        search = st.text_input("Buscar...")
        df_view = df[df["Nombre"].str.contains(search, case=False, na=False) | df["Boleto"].astype(str).contains(search)] if search else df.sort_values("Boleto", ascending=False).head(10)
        for index, row in df_view.iterrows():
            with st.expander(f"Boleto {int(row['Boleto'])} - {row['Nombre']}"):
                with st.form(f"f_{index}"):
                    n_nom = st.text_input("Nombre", value=row["Nombre"])
                    n_est = st.selectbox("Estado", ["Pagado", "Pendiente"], index=0 if row["Estado"]=="Pagado" else 1)
                    if st.form_submit_button("💾 Guardar"):
                        df.at[index, "Nombre"] = n_nom
                        df.at[index, "Estado"] = n_est
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()
                    if st.form_submit_button("🗑️ Borrar"):
                        df = df.drop(index)
                        df.to_csv(DB_FILE, index=False)
                        st.rerun()

elif menu == "Mapa":
    st.subheader("📍 Estado de Boletos")
    color_map = dict(zip(df.Boleto, df.Estado)) if not df.empty else {}
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
