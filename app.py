import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Auditoría Vespasiani - Repuestos", layout="wide")

# --- SISTEMA DE AUTENTICACIÓN ---
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "12345":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuario", key="username")
        st.text_input("Contraseña", type="password", key="password")
        st.button("Ingresar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.error("Usuario o contraseña incorrectos")
        return False
    return True

if check_password():
    st.title("📊 Auditoría de Repuestos Mostrador - Vespasiani")

    # CARGA AUTOMÁTICA DEL ARCHIVO
    file_path = "reporte_repuestos_mostrador.xlsx - MOSTRADOR.csv"
    
    try:
        # Saltamos la primera fila que es el título del reporte en tu CSV
        df = pd.read_csv(file_path, skiprows=1)
        
        # --- SIDEBAR / FILTROS ---
        st.sidebar.header("Filtros de Auditoría")
        sucursal = st.sidebar.multiselect("Seleccionar Sucursal:", options=df["Sucursal"].unique(), default=df["Sucursal"].unique())
        mes = st.sidebar.multiselect("Seleccionar Mes:", options=df["Mes"].unique(), default=df["Mes"].unique())

        df_selection = df.query("Sucursal == @sucursal & Mes == @mes")

        # --- KPIs PRINCIPALES ---
        col1, col2, col3 = st.columns(3)
        total_venta = df_selection["Venta Total"].sum()
        utilidad_promedio = df_selection["(%) Utilidad"].mean()
        cant_operaciones = len(df_selection)

        col1.metric("Venta Total", f"$ {total_venta:,.2f}")
        col2.metric("Utilidad Promedio", f"{utilidad_promedio:.2f}%")
        col3.metric("Operaciones", cant_operaciones)

        st.markdown("---")

        # --- TABLA INTERACTIVA ---
        st.subheader("Detalle de Ventas para Auditoría")
        st.dataframe(df_selection, use_container_width=True)

        # --- EXPORTAR ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_selection.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Descargar Auditoría en Excel",
            data=output.getvalue(),
            file_name="auditoria_vespasiani.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}. Asegúrate de que el CSV esté en el repositorio.")