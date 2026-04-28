import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Dashboard de KPIs de Ventas", layout="wide")

# --- SISTEMA DE AUTENTICACIÓN SIMPLE ---
# En un entorno real, usa streamlit-authenticator para mayor seguridad
def check_password():
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "12345":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Usuario", on_change=None, key="username")
        st.text_input("Contraseña", type="password", on_change=None, key="password")
        st.button("Ingresar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Usuario", on_change=None, key="username")
        st.text_input("Contraseña", type="password", on_change=None, key="password")
        st.button("Ingresar", on_click=password_entered)
        st.error("Usuario o contraseña incorrectos")
        return False
    else:
        return True

if check_password():
    st.title("📊 Reporte de KPIs de Ventas - Repuestos")

    # --- CARGA DE ARCHIVO ---
    uploaded_file = st.file_uploader("Sube tu archivo Excel o CSV", type=['xlsx', 'csv'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Limpieza básica de datos basada en tu archivo
            df['fecha'] = pd.to_datetime(df['fecha'])
            
            # --- FILTROS LATERALES ---
            st.sidebar.header("Filtros")
            sucursal = st.sidebar.multiselect("Sucursal", options=df["Sucursal"].unique(), default=df["Sucursal"].unique())
            tipo_cliente = st.sidebar.multiselect("Tipo de Cliente", options=df["Tipo Cliente"].unique(), default=df["Tipo Cliente"].unique())

            df_selection = df.query("Sucursal == @sucursal & `Tipo Cliente` == @tipo_cliente")

            # --- KPIs PRINCIPALES ---
            total_ventas = df_selection["Venta Total"].sum()
            utilidad_promedio = df_selection["(%) Utilidad"].mean()
            cantidad_operaciones = df_selection.shape[0]
            utilidad_total = df_selection["Utilidad"].sum()

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ventas Totales", f"$ {total_ventas:,.2f}")
            col2.metric("Utilidad Total", f"$ {utilidad_total:,.2f}")
            col3.metric("% Utilidad Promedio", f"{utilidad_promedio:.2f}%")
            col4.metric("Operaciones", cantidad_operaciones)

            st.markdown("""---""")

            # --- GRÁFICOS ---
            c1, c2 = st.columns(2)

            with c1:
                st.subheader("Ventas por Mes")
                ventas_mes = df_selection.groupby(by=["Mes"]).sum(numeric_only=True)[["Venta Total"]].reset_index()
                fig_ventas = px.bar(ventas_mes, x="Mes", y="Venta Total", template="plotly_white", color_discrete_sequence=["#0083B8"])
                st.plotly_chart(fig_ventas, use_container_width=True)

            with c2:
                st.subheader("Distribución por Vendedor (Corredor)")
                ventas_vendedor = df_selection.groupby(by=["Corredor"]).sum(numeric_only=True)[["Venta Total"]].reset_index()
                fig_vendedor = px.pie(ventas_vendedor, values="Venta Total", names="Corredor", hole=0.4)
                st.plotly_chart(fig_vendedor, use_container_width=True)

            # --- EXPORTAR RESULTADOS ---
            st.subheader("Descargar Reporte Procesado")
            
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_selection.to_excel(writer, index=False, sheet_name='KPI_Reporte')
            
            st.download_button(
                label="📥 Descargar datos filtrados en Excel",
                data=output.getvalue(),
                file_name="reporte_kpi_ventas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # --- TABLA DE DATOS ---
            with st.expander("Ver tabla de datos detallada"):
                st.dataframe(df_selection)

        except Exception as e:
            st.error(f"Error al procesar el archivo: {e}")
    else:
        st.info("Esperando que se suba un archivo para generar el reporte.")