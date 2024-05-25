import random
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Ventas Dashboard", page_icon=":bar_chart:", layout="wide")

st.title("Ventas de Yerba Dashboard")
st.markdown("_Prototype v0.4.1_")

# Leer el archivo CSV
nombre_archivo = 'data-dummies-yerba.csv'
df = pd.read_csv(nombre_archivo)

all_months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# Convertir columnas a float
for month in all_months:
    df[month] = df[month].replace('[\$,]', '', regex=True).astype(float)

with st.expander("Data Preview"):
    st.dataframe(df)
    st.write("Tipos de datos de las columnas:")
    st.write(df.dtypes)

# Renombrar la columna
df = df.rename(columns={'Unidad de Negocio': 'Unidad_de_Negocio'})

#######################################
# VISUALIZATION METHODS
#######################################

#######################################
# VISUALIZATION METHODS
#######################################


def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font.size": 28,
            },
            title={
                "text": label,
                "font": {"size": 24},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={
                    "color": color_graph,
                },
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        margin=dict(t=30, b=0),
        showlegend=False,
        plot_bgcolor="white",
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_gauge(
    indicator_number, indicator_color, indicator_suffix, indicator_title, max_bound
):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 26,
            },
            gauge={
                "axis": {"range": [0, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title,
                "font": {"size": 28},
            },
        )
    )
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        height=200,
        margin=dict(l=10, r=10, t=50, b=10, pad=8),
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_top_right():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Escenario,
                    Unidad_de_Negocio,
                    {','.join(all_months)} 
                    FROM df 
                    WHERE  Año ='2023' 
                    AND Cuenta ='Ventas' 
                ) 
            ON {','.join(all_months)}
            INTO
                NAME Mes
                VALUE Ventas
        ),

        aggregated_sales AS (
            SELECT
                Escenario,
                Unidad_de_Negocio,
                SUM(Ventas) AS Ventas
            FROM sales_data
            GROUP BY Escenario, Unidad_de_Negocio
        )
        
        SELECT * FROM aggregated_sales
        """
    ).df()

    fig = px.bar(
        sales_data,
        x="Unidad_de_Negocio",
        y="Ventas",
        color="Escenario",
        barmode="group",
        text_auto=".2s",
        title="Ventas para el año 2023",
        height=400,
    )
    fig.update_traces(
        textfont_size=12, textangle=0, textposition="outside", cliponaxis=False
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_bottom_left():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            SELECT 
            Escenario,{','.join(all_months)} 
            FROM df 
            WHERE Año ='2023' 
            AND Cuenta ='Ventas'
            AND Unidad_de_Negocio ='Yerba Mate'
        )

        UNPIVOT sales_data 
        ON {','.join(all_months)}
        INTO
            NAME Mes
            VALUE Ventas
    """
    ).df()

    fig = px.line(
        sales_data,
        x="Mes",
        y="Ventas",
        color="Escenario",
        markers=True,
        text="Ventas",
        title="Presupuesto Mensual vs Previsión 2023",
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)


def plot_bottom_right():
    sales_data = duckdb.sql(
        f"""
        WITH sales_data AS (
            UNPIVOT ( 
                SELECT 
                    Cuenta,Año,{','.join([f'ABS({month}) AS {month}' for month in all_months])}
                    FROM df 
                    WHERE Escenario='Actual'
                    AND Cuenta!='Ventas'
                ) 
            ON {','.join(all_months)}
            INTO
                NAME Año
                VALUE Ventas
        ),

        aggregated_sales AS (
            SELECT
                Cuenta,
                Año,
                SUM(Ventas) AS Ventas
            FROM sales_data
            GROUP BY Cuenta, Año
        )
        
        SELECT * FROM aggregated_sales
    """
    ).df()

    fig = px.bar(
        sales_data,
        x="Año",
        y="Ventas",
        color="Cuenta",
        title="Gastos Anuales",
    )
    st.plotly_chart(fig, use_container_width=True)

#######################################
# STREAMLIT LAYOUT
#######################################


top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)


with top_left_column:
    column_1, column_2, column_3, column_4 = st.columns(4)

    with column_1:
        plot_metric(
            "Cuentas por cobrar",
            6621280,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(0, 104, 201, 0.2)",
        )
        plot_gauge(1.86, "#0068C9", "%", "Current Ratio", 3)

    with column_2:
        plot_metric(
            "Cuentas por pagar",
            1630270,
            prefix="$",
            suffix="",
            show_graph=True,
            color_graph="rgba(255, 43, 43, 0.2)",
        )
        plot_gauge(10, "#FF8700", " days", "In Stock", 31)

    with column_3:
        plot_metric("Relación de capital", 75.38, prefix="", suffix=" %", show_graph=False)
        plot_gauge(7, "#FF2B2B", " days", "Out Stock", 31)
        
    with column_4:
        plot_metric("Capital de deuda", 1.10, prefix="", suffix=" %", show_graph=False)
        plot_gauge(28, "#29B09D", " days", "Delay", 31)


with top_right_column:
    plot_top_right()


with bottom_left_column:
    plot_bottom_left()


with bottom_right_column:
    plot_bottom_right()