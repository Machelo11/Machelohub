            menu = st.sidebar.radio("Navegación", [
                "Inicio", "Sobre mí", "Contáctame", "Propiedades", "Agendar Cita",
                "Calculadora Hipotecaria", "Simulador Infonavit", "Mapa de Propiedades", "Consejos", "Plusvalía"
            ])

            if menu == "Inicio":
                st.markdown("## 🏠 Encuentra tu nuevo hogar")

            elif menu == "Sobre mí":
                st.markdown("## 🤝 Acerca de mí\nSoy Miguel Gonzalez Zaragoza, asesor inmobiliario especializado en Zapopan.")

            elif menu == "Contáctame":
                st.markdown("## 📢 Contáctame\n- 📧 **Correo:** miguel.zaragoza1211@gmail.com\n- 📞 **Teléfono:** +52 33 1309 6544\n- 👤 **Instagram:** @miguelgzr_")

            elif menu == "Propiedades":
                st.markdown("## 🏡 Propiedades en Venta")
                # ... (código ya existente sin cambios)

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
                    st.balloons()
                    st.success(f"""
                        🎉 ¡Gracias por agendar tu cita, {nombre}!  
                        📅 Te esperamos el **{fecha.strftime('%d/%m/%Y')}** a las **{horario}**.  
                        📍 Estamos emocionados por ayudarte a encontrar tu próximo hogar.  
                        ¡Nos vemos pronto!
                    """)

            elif menu == "Calculadora Hipotecaria":
                # ... (sin cambios)

            elif menu == "Simulador Infonavit":
                # ... (sin cambios)

            elif menu == "Mapa de Propiedades":
                # ... (sin cambios)

            elif menu == "Consejos":
                # ... (sin cambios)

            elif menu == "Plusvalía":
                st.markdown("## 📈 Consulta de Plusvalía")
                if not df.empty:
                    propiedad = st.selectbox("Selecciona una propiedad", df["direccion"])
                    # Valor simulado de plusvalía basado en zona
                    plusvalia = {
                        "Zapopan Centro": 0.12,
                        "Valle Real": 0.15,
                        "Ciudad Granja": 0.10
                    }
                    zona = df[df["direccion"] == propiedad]["ubicacion"].values[0]
                    tasa = plusvalia.get(zona, 0.08)
                    precio_actual = df[df["direccion"] == propiedad]["precio"].values[0]
                    estimacion = precio_actual * (1 + tasa)

                    st.info(f"🏘️ Zona: **{zona}**")
                    st.success(f"💹 Estimación de plusvalía anual: **{tasa*100:.1f}%**")
                    st.markdown(f"📊 Precio proyectado para el próximo año: **${estimacion:,.2f} MXN**")
                else:
                    st.warning("No hay propiedades cargadas para mostrar plusvalía.")
