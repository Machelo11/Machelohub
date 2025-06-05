import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, date
import numpy as np

# Configuración de la página
st.set_page_config(page_title="Asesor Inmobiliario Zaragoza", layout="centered")

# Título y bienvenida
st.title("ASESOR INMOBILIARIO ZARAGOZA")
st.subheader("Bienvenido a tu plataforma de confianza para encontrar propiedades en Zapopan")

# Ruta de la base de datos
DB_PATH = "propiedadesmgz.db"

# Funciones para redondear precios y metros
def redondear_precios(valor, arriba=True):
    base = 50000
    return int(np.ceil(valor / base) * base) if arriba else int(np.floor(valor / base) * base)

def redondear_metros(valor, arriba=True):
    base = 10
    return int(np.ceil(valor / base) * base) if arriba else int(np.floor(valor / base) * base)

if not os.path.exists(DB_PATH):
    st.error("❌ No se encontró el archivo 'propiedadesmgz.db' en la carpeta del proyecto.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Crear tabla citas si no existe
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

        # Verificar que la tabla 'propiedades' exista
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='propiedades';")
        table_exists = cursor.fetchone()

        if not table_exists:
            st.error("❌ La base de datos está conectada, pero no contiene la tabla 'propiedades'.")
        else:
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)

            menu = st.sidebar.radio("Navegación", ["Inicio", "Sobre mí", "Contáctame", "Propiedades", "Agendar Cita"])

            if menu == "Inicio":
                st.markdown("""
                ## 🏠 Encuentra tu nuevo hogar
                Esta plataforma está diseñada para ayudarte a encontrar propiedades en venta en Zapopan
                de forma rápida, sencilla y confiable.
                """)

            elif menu == "Sobre mí":
                st.markdown("""
                ## 🤝 Acerca de mí
                Mi nombre es Miguel Gonzalez Zaragoza y soy un asesor inmobiliario con más de 2 años de experiencia.
                Me especializo en la zona de Zapopan y mi objetivo es ayudarte a encontrar la propiedad ideal.
                """)

            elif menu == "Contáctame":
                st.markdown("""
                ## 📢 Contáctame
                - 📧 **Correo:** miguel.zaragoza1211@gmail.com 
                - 📞 **Teléfono:** +52 33 1309 6544  
                - 👤 **Instagram:** @miguelgzr_
                """)

            elif menu == "Propiedades":
                st.markdown("## 🏡 Propiedades en Venta")

                # Filtros redondeados
                precio_min = redondear_precios(df.precio.min(), arriba=False)
                precio_max = redondear_precios(df.precio.max(), arriba=True)
                metros_min = redondear_metros(df.metros_cuadrados.min(), arriba=False)
                metros_max = redondear_metros(df.metros_cuadrados.max(), arriba=True)

                tipo = st.selectbox("Tipo de propiedad", ["Todos"] + df["tipo"].unique().tolist())
                ubicacion = st.selectbox("Ubicación", ["Todas"] + df["ubicacion"].unique().tolist())
                colonia = st.selectbox("Colonia", ["Todas"] + sorted(df["colonia"].unique().tolist()))
                habitaciones = st.slider("Número de habitaciones", int(df.habitaciones.min()), int(df.habitaciones.max()), (int(df.habitaciones.min()), int(df.habitaciones.max())))
                precio = st.slider("Precio (MXN)", precio_min, precio_max, (precio_min, precio_max), step=50000)
                metros = st.slider("Metros cuadrados", metros_min, metros_max, (metros_min, metros_max), step=10)

                # Filtro aplicado
                df_filtrado = df[
                    (df["habitaciones"] >= habitaciones[0]) & (df["habitaciones"] <= habitaciones[1]) &
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
                st.markdown("## 📅 Agenda una Cita")

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

                    st.success(f"✅ Gracias {nombre}, tu cita ha sido agendada para el {fecha.strftime('%d/%m/%Y')} a las {horario}.")
                    st.info("Nos pondremos en contacto contigo al número proporcionado.")

        conn.close()

    except Exception as e:
        st.error(f"⚠️ Error al acceder a la base de datos: {e}")
        
