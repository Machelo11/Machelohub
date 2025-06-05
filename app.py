import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, date
import numpy as np

# Configuración general
st.set_page_config(page_title="Asesor Inmobiliario Zaragoza", layout="centered")
st.title("ASESOR INMOBILIARIO ZARAGOZA")
st.subheader("Bienvenido a tu plataforma de confianza para encontrar propiedades en Zapopan")

DB_PATH = "propiedadesmgz.db"

# Funciones auxiliares
def redondear_precios(valor, arriba=True):
    base = 50000
    return int(np.ceil(valor / base) * base) if arriba else int(np.floor(valor / base) * base)

def redondear_metros(valor, arriba=True):
    base = 10
    return int(np.ceil(valor / base) * base) if arriba else int(np.floor(valor / base) * base)

def calcular_pago_mensual(precio, enganche_pct, tasa_anual, plazo_anios):
    prestamo = precio * (1 - enganche_pct / 100)
    tasa_mensual = tasa_anual / 100 / 12
    n_meses = plazo_anios * 12
    if tasa_mensual == 0:
        return prestamo / n_meses
    pago = prestamo * tasa_mensual * (1 + tasa_mensual) ** n_meses / ((1 + tasa_mensual) ** n_meses - 1)
    return pago

def simulador_infonavit(salario_mensual):
    credito_estimado = salario_mensual * 25
    pago_estimado = calcular_pago_mensual(credito_estimado, 0, 9.0, 20)
    return credito_estimado, pago_estimado

# Simulamos coordenadas de propiedades
data_mapa = {
    "tipo": ["Casa", "Departamento", "Terreno"],
    "lat": [20.6843, 20.6781, 20.6932],
    "lon": [-103.3920, -103.3673, -103.3815],
    "precio": [2500000, 1800000, 1200000],
    "ubicacion": ["Zapopan Centro", "Valle Real", "Ciudad Granja"]
}
df_mapa = pd.DataFrame(data_mapa)

# Verificación DB
if not os.path.exists(DB_PATH):
    st.error("❌ No se encontró el archivo 'propiedadesmgz.db'.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Crear tabla de citas si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                telefono TEXT,
                busqueda TEXT,
                fecha TEXT,
                horario TEXT,
                registrado_en TEXT
            );
        """)

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='propiedades';")
        table_exists = cursor.fetchone()

        if not table_exists:
            st.error("❌ La base de datos está conectada, pero no contiene la tabla 'propiedades'.")
        else:
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)

            menu = st.sidebar.radio("Navegación", [
                "Inicio", "Sobre mí", "Contáctame", "Propiedades", "Agendar Cita",
                "Calculadora Hipotecaria", "Simulador Infonavit", "Mapa de Propiedades", "Consejos" 
            ])

            if menu == "Inicio":
                st.markdown("## 🏠 Encuentra tu nuevo hogar")

            elif menu == "Sobre mí":
                st.markdown("## 🤝 Acerca de mí\nSoy Miguel Gonzalez Zaragoza, asesor inmobiliario especializado en Zapopan.")

            elif menu == "Contáctame":
                st.markdown("## 📢 Contáctame\n- 📧 **Correo:** miguel.zaragoza1211@gmail.com\n- 📞 **Teléfono:** +52 33 1309 6544\n- 👤 **Instagram:** @miguelgzr_")

            elif menu == "Propiedades":
                st.markdown("## 🏡 Propiedades en Venta")

                precio_min = redondear_precios(df.precio.min(), arriba=False)
                precio_max = redondear_precios(df.precio.max(), arriba=True)
                metros_min = redondear_metros(df.metros_cuadrados.min(), arriba=False)
                metros_max = redondear_metros(df.metros_cuadrados.max(), arriba=True)

                tipo = st.selectbox("Tipo de propiedad", ["Todos"] + df["tipo"].unique().tolist())
                ubicacion = st.selectbox("Ubicación", ["Todas"] + df["ubicacion"].unique().tolist())
                colonia = st.selectbox("Colonia", ["Todas"] + sorted(df["colonia"].unique().tolist()))
                habitaciones = st.slider("Número de habitaciones", int(df.habitaciones.min()), int(df.habitaciones.max()))
                precio = st.slider("Precio (MXN)", precio_min, precio_max, (precio_min, precio_max), step=50000)
                metros = st.slider("Metros cuadrados", metros_min, metros_max, (metros_min, metros_max), step=10)

                df_filtrado = df[
                    (df["habitaciones"] >= habitaciones) &
                    (df["precio"] >= precio[0]) & (df["precio"] <= precio[1]) &
                    (df["metros_cuadrados"] >= metros[0]) & (df["metros_cuadrados"] <= metros[1])
                ]
                if tipo != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["tipo"] == tipo]
                if ubicacion != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["ubicacion"] == ubicacion]
                if colonia != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["colonia"] == colonia]

                st.dataframe(df_filtrado.reset_index(drop=True))

            elif menu == "Agendar Cita":
                st.markdown("## 🗕️ Agenda una Cita")
                with st.form("form_cita"):
                    nombre = st.text_input("Nombre completo")
                    telefono = st.text_input("Número de teléfono")
                    busqueda = st.text_area("¿Qué tipo de propiedad estás buscando?")
                    fecha = st.date_input("Selecciona una fecha", min_value=date.today())
                    horario = st.selectbox("Selecciona un horario", [
                        "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM",
                        "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"
                    ])
                    enviar = st.form_submit_button("Agendar Cita")

                if enviar:
                    cursor.execute("""
                        INSERT INTO citas (nombre, telefono, busqueda, fecha, horario, registrado_en)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (nombre, telefono, busqueda, str(fecha), horario, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    conn.commit()
                    st.balloons()
                    st.success(f"""
                        🎉 ¡Gracias por agendar tu cita, {nombre}!  
                        🗓️ Te esperamos el **{fecha.strftime('%d/%m/%Y')}** a las **{horario}**.  
                        📍 Estamos emocionados por ayudarte a encontrar tu próximo hogar.  
                        ¡Nos vemos pronto!
                    """)

            elif menu == "Calculadora Hipotecaria":
                st.markdown("## 🧲 Calculadora Hipotecaria")
                precio = st.number_input("Precio de la propiedad (MXN)", min_value=100000, step=50000)
                enganche = st.slider("Enganche (%)", 0, 100, 20)
                tasa = st.slider("Tasa de interés anual (%)", 0.0, 20.0, 10.0)
                plazo = st.slider("Plazo (años)", 5, 30, 20)
                if st.button("Calcular pago mensual"):
                    pago = calcular_pago_mensual(precio, enganche, tasa, plazo)
                    st.success(f"💰 Tu pago mensual estimado es: ${pago:,.2f} MXN")

            elif menu == "Simulador Infonavit":
                st.markdown("## 🏦 Simulador Infonavit")
                salario = st.number_input("Tu salario mensual (MXN)", min_value=5000, step=1000)
                if st.button("Simular Crédito"):
                    credito, pago = simulador_infonavit(salario)
                    st.info(f"💸 Crédito estimado: ${credito:,.0f} MXN")
                    st.success(f"📆 Pago mensual estimado: ${pago:,.2f} MXN a 20 años")

            elif menu == "Mapa de Propiedades":
                st.markdown("## 🗌 Mapa de Propiedades")
                st.map(df_mapa.rename(columns={'lat': 'latitude', 'lon': 'longitude'}))

            elif menu == "Consejos":
                st.markdown("## 📘 Consejos para Comprar Propiedad")
                st.markdown("""
                - 🔍 **Define tu presupuesto.**
                - 🏦 **Consulta con tu banco o Infonavit.**
                - 📍 **Elige zonas con buena plusvalía.**
                - 📜 **Verifica documentos legales.**
                - 🕵️ **Visita varias opciones.**
                - 🤝 **Apóyate en un asesor confiable.**
                """)

            

    except Exception as e:
        st.error(f"⚠️ Error al acceder a la base de datos: {e}")
