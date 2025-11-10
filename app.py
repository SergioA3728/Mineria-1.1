
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------------------------------
# Dashboard: Análisis de datos estudiantiles
# Diseño: orientado a robustez, validaciones y seguridad
# -----------------------------------------------------

st.set_page_config(page_title="Dashboard Estudiantes - UDC", layout="wide")
st.title("Dashboard Analítico - Universidad")
st.write("Interfaz para explorar indicadores: admisiones, retención y satisfacción.")

# ----------------- Config -----------------
DATA_PATHS = [
    "university_student_data.csv",            # ruta local (repo / Colab upload)
    "/mnt/data/university_student_data.csv"   # ruta en entorno proporcionado
]

# ----------------- Carga segura -----------------
@st.cache_data(ttl=600)
def load_data():
    # Intentar cargar desde varias rutas conocidas
    for p in DATA_PATHS:
        try:
            path = Path(p)
            if path.exists():
                df = pd.read_csv(path)
                return df
        except Exception:
            continue
    return None

df = load_data()
if df is None:
    st.error("No se encontró el archivo 'university_student_data.csv' en rutas esperadas. "
             "Sube el CSV en el entorno (Colab: Files -> Upload) o añade la ruta correcta.")
    st.stop()

df = df.melt(
    id_vars=["Year", "Term", "Applications", "Admitted", "Enrolled",
             "Retention Rate (%)", "Student Satisfaction (%)"],
    value_vars=["Engineering Enrolled", "Business Enrolled", "Arts Enrolled", "Science Enrolled"],
    var_name="Department",
    value_name="EnrollmentsDept"
)

# Limpiar el texto del nombre de la columna
df["Department"] = df["Department"].str.replace(" Enrolled", "", regex=False)

# Crear alias de columnas que espera el código
df = df.rename(columns={
    "Retention Rate (%)": "RetentionRate",
    "Student Satisfaction (%)": "SatisfactionScore"
})

# Crear columna 'Enrollments' 
df["Enrollments"] = df["EnrollmentsDept"]

# ----------------- Validación de columnas -----------------
expected_columns = {"Year", "Department", "Term", "Applications", "Enrollments",
                    "RetentionRate", "SatisfactionScore"}
missing = expected_columns - set(df.columns)
if missing:
    st.warning(f"Faltan columnas esperadas: {', '.join(sorted(missing))}. "
               "Verifica el formato del CSV.")
# Normalizar tipos básicos (int/float) con manejo de errores
for col in ["Year", "Applications", "Enrollments"]:
    if col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
        except Exception:
            df[col] = pd.to_numeric(df[col], errors="coerce")

for col in ["RetentionRate", "SatisfactionScore"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Mostrar resumen
st.subheader("Vista rápida del conjunto de datos")
st.dataframe(df.head().reset_index(drop=True), use_container_width=True)
st.write(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")

# ----------------- Sidebar: filtros -----------------
st.sidebar.header("Filtros")
years = sorted(df["Year"].dropna().unique().tolist())
depts = sorted(df["Department"].dropna().unique().tolist())
terms = sorted(df["Term"].dropna().unique().tolist())

year_sel = st.sidebar.multiselect("Año(s)", years, default=years if years else [])
dept_sel = st.sidebar.multiselect("Departamento(s)", depts, default=depts if depts else [])
term_sel = st.sidebar.multiselect("Periodo(s)", terms, default=terms if terms else [])

df_f = df.copy()
if year_sel:
    df_f = df_f[df_f["Year"].isin(year_sel)]
if dept_sel:
    df_f = df_f[df_f["Department"].isin(dept_sel)]
if term_sel:
    df_f = df_f[df_f["Term"].isin(term_sel)]

# Evitar operaciones costosas en datasets vacíos
if df_f.empty:
    st.warning("Los filtros seleccionados devuelven 0 filas. Ajusta los filtros.")
    st.stop()

# ----------------- KPI -----------------
st.subheader("Indicadores clave")
col1, col2, col3 = st.columns(3)
try:
    avg_ret = df_f["RetentionRate"].mean()
    avg_sat = df_f["SatisfactionScore"].mean()
    total_enr = int(df_f["Enrollments"].sum(min_count=1) or 0)
    col1.metric("Tasa de retención (avg)", f"{avg_ret:.2f}%" if pd.notna(avg_ret) else "N/A")
    col2.metric("Satisfacción (avg)", f"{avg_sat:.2f}/5" if pd.notna(avg_sat) else "N/A")
    col3.metric("Matrículas (total)", f"{total_enr}")
except Exception as e:
    st.error(f"Error calculando KPIs: {e}")

# ----------------- Gráfica 1: Retención por año -----------------
st.subheader("Tendencia: Retención por año")
try:
    df_ret = df_f.groupby("Year", as_index=False)["RetentionRate"].mean()
    fig1, ax1 = plt.subplots(figsize=(8,3.5))
    ax1.plot(df_ret["Year"], df_ret["RetentionRate"], marker='o')
    ax1.set_xlabel("Año"); ax1.set_ylabel("Retención (%)"); ax1.set_title("Retención promedio por año")
    ax1.grid(True)
    st.pyplot(fig1)
except Exception as e:
    st.error(f"No se pudo generar la gráfica de retención: {e}")

# ----------------- Gráfica 2: Satisfacción por año -----------------
st.subheader("Satisfacción promedio por año")
try:
    df_sat = df_f.groupby("Year", as_index=False)["SatisfactionScore"].mean()
    fig2, ax2 = plt.subplots(figsize=(8,3.5))
    ax2.bar(df_sat["Year"].astype(str), df_sat["SatisfactionScore"])
    ax2.set_xlabel("Año"); ax2.set_ylabel("Satisfacción"); ax2.set_title("Satisfacción promedio por año")
    st.pyplot(fig2)
except Exception as e:
    st.error(f"No se pudo generar la gráfica de satisfacción: {e}")

# ----------------- Gráfica 3: Distribución por periodo -----------------
st.subheader("Distribución de matrículas por periodo")
try:
    df_term = df_f.groupby("Term", as_index=False)["Enrollments"].sum()
    fig3, ax3 = plt.subplots(figsize=(6,4))
    ax3.pie(df_term["Enrollments"], labels=df_term["Term"], autopct="%1.1f%%", startangle=90)
    ax3.set_title("Matrículas por periodo")
    st.pyplot(fig3)
except Exception as e:
    st.error(f"No se pudo generar la gráfica de periodo: {e}")

# ----------------- Tabla de datos filtrados -----------------
st.subheader("Datos filtrados")
st.dataframe(df_f.reset_index(drop=True), height=300, use_container_width=True)


