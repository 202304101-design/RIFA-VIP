import streamlit as st
import pandas as pd
import os

# Configuración estilo iOS
st.set_page_config(page_title="Rifa Pro 1000", page_icon="🎟️")

# Estilo para que se vea premium
st.markdown("""
    <style>
    .stApp { background-color: #F2F2F7; }
    .ticket-box {
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
        font-weight: bold;
    }
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
df["Boleto"] = df["Boleto"].astype(int) # Asegurar que sea número

# --- LÓGICA DE NEGOCIO ---
total_boletos = 1000
vendidos = len(df)
porcentaje = (vendidos / total_boletos)

# --- INTERFAZ ---
st.title("🎟️ Control de Rifa 1000")

# 1. Porcentaje de progreso
st.subheader(f"Progreso de Venta: {vendidos} de {total_boletos}")
st.progress(porcentaje)
st.write(f"**{porcentaje*100:.1f}% vendido**")

# 2. Formulario de Registro
with st.expander("📝 Registrar Nueva Venta", expanded=True):
    with st.form("registro_form"):
        nombre = st.text_input("Nombre del Cliente").strip()
        tel = st.text_input("Teléfono").strip()
        
        # Selección de boletos disponibles
        boletos_ocupados = df["Boleto"].tolist()
        boletos_disponibles = [i for i in range(1, 1001) if i not in boletos_ocupados]
        
        numeros_elegidos = st.multiselect("Selecciona los números de boleto", boletos_disponibles)
        
        submit = st.form_submit_button("Confirmar Registro")
        
        if submit:
            if not nombre or not numeros_elegidos:
                st.error("Por favor ingresa el nombre y al menos un número de boleto.")
            else:
                try:
                    # Crear nuevos registros
                    nuevos_datos = pd.DataFrame({
                        "Boleto": numeros_elegidos,
                        "Nombre": [nombre] * len(numeros_elegidos),
                        "Teléfono": [tel] * len(numeros_elegidos)
                    })
                    df = pd.concat([df, nuevos_datos], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success(f"¡Registrado! Boletos: {numeros_elegidos}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Hubo un error al guardar. Intenta de nuevo.")

# 3. Pestañas para organizar la información
tab1, tab2 = st.tabs(["📋 Lista de Ventas", "🔢 Mapa de Boletos (1-1000)"])

with tab1:
    st.subheader("Ventas Registradas")
    if not df.empty:
        # Buscador por nombre
        busqueda = st.text_input("Buscar por nombre...")
        df_mostrar = df[df["Nombre"].str.contains(busqueda, case=False)] if busqueda else df
        st.dataframe(df_mostrar.sort_values("Boleto"), use_container_width=True)
    else:
        st.info("No hay ventas aún.")

with tab2:
    st.subheader("Estado de todos los números")
    col_v, col_d = st.columns(2)
    col_v.write("🔴 Vendido")
    col_d.write("🟢 Disponible")
    
    # Crear una cuadrícula visual de los 1000 boletos
    # Nota: Para no saturar la pantalla, mostramos una lista resumida o botones
    filas = 100
    for i in range(0, 1000, 10): # Grupos de 10 para que se vea limpio
        cols = st.columns(10)
        for j in range(10):
            num = i + j + 1
            if num <= 1000:
                if num in boletos_ocupados:
                    cols[j].markdown(f'<div class="ticket-box sold">{num}</div>', unsafe_allow_html=True)
                else:
                    cols[j].markdown(f'<div class="ticket-box available">{num}</div>', unsafe_allow_html=True)
