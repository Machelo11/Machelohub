import streamlit as st
import pandas as pd
import sqlite3
import os

# Configuración de la página
st.set_page_config(page_title="Asesor Inmobiliario Zaragoza", layout="centered")

# Título y bienvenida
st.title("ASESOR INMOBILIARIO ZARAGOZA")
st.subheader("Bienvenido a tu plataforma de confianza para encontrar propiedades en Zapopan")

# Intentar conectar con la base de datos
DB_PATH = "propiedadesmgz.db"

if not os.path.exists(DB_PATH):
    st.error("❌ No se encontró el archivo 'propiedadesmgz.db' en la carpeta del proyecto.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verificar que la tabla 'propiedades' exista
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='propiedades';")
        table_exists = cursor.fetchone()

        if not table_exists:
            st.error("❌ La base de datos está conectada, pero no contiene la tabla 'propiedades'.")
        else:
            df = pd.read_sql_query("SELECT * FROM propiedades", conn)

            # Barra lateral
            menu = st.sidebar.radio("Navegación", ["Inicio", "Sobre mí", "Contáctame", "Propiedades"])

            if menu == "Inicio":
                st.markdown("""
                ## 🏠 Encuentra tu nuevo hogar
                Esta plataforma está diseñada para ayudarte a encontrar propiedades en venta en Zapopan
                de forma rápida, sencilla y confiable.
                """)

            elif menu == "Sobre mí":
                st.markdown("""
                ## 🤝 Acerca de mí
                Mi nombre es [Tu Nombre] y soy un asesor inmobiliario con más de 10 años de experiencia.
                Me especializo en la zona de Zapopan y mi objetivo es ayudarte a encontrar la propiedad ideal.
                """)

            elif menu == "Contáctame":
                st.markdown("""
                ## 📢 Contáctame
                - 📧 **Correo:** tuemail@ejemplo.com  
                - 📞 **Teléfono:** +52 33 1234 5678  
                - 👤 **Instagram:** [@tuusuario](https://instagram.com/tuusuario)  
                - 📲 **Facebook:** [Asesor Inmobiliario Zaragoza](https://facebook.com/zaragozainmuebles)
                """)

            elif menu == "Propiedades":
                st.markdown("## 🏡 Propiedades en Venta")

                # Filtros
                tipo = st.selectbox("Tipo de propiedad", ["Todos"] + df["tipo"].unique().tolist())
                ubicacion = st.selectbox("Ubicación", ["Todas"] + df["ubicacion"].unique().tolist())
                colonia = st.selectbox("Colonia", ["Todas"] + sorted(df["colonia"].unique().tolist()))
                habitaciones = st.slider("Número de habitaciones", int(df.habitaciones.min()), int(df.habitaciones.max()), (int(df.habitaciones.min()), int(df.habitaciones.max())))
                precio = st.slider("Precio (MXN)", int(df.precio.min()), int(df.precio.max()), (int(df.precio.min()), int(df.precio.max())))
                metros = st.slider("Metros cuadrados", int(df.metros_cuadrados.min()), int(df.metros_cuadrados.max()), (int(df.metros_cuadrados.min()), int(df.metros_cuadrados.max())))

                # Filtros aplicados
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

        conn.close()

    except Exception as e:
        st.error(f"⚠️ Error al acceder a la base de datos: {e}")
