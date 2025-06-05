import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, date
import numpy as np
from fpdf import FPDF

# ---------------- FUNCIONES PDF ------------------
def generar_pdf_cita(nombre, telefono, busqueda, fecha, horario):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Confirmación de Cita - Asesor Inmobiliario Zaragoza", ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Nombre: {nombre}", ln=1)
    pdf.cell(200, 10, txt=f"Teléfono: {telefono}", ln=1)
    pdf.multi_cell(0, 10, txt=f"¿Qué estás buscando?: {busqueda}")
    pdf.cell(200, 10, txt=f"Fecha agendada: {fecha}", ln=1)
    pdf.cell(200, 10, txt=f"Horario: {horario}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 12)
    pdf.multi_cell(0, 10, txt="¡Gracias por agendar tu cita!\nSerá un placer ayudarte a encontrar la propiedad ideal en Zapopan.")
    file_path = f"/mnt/data/Cita_{nombre}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_path)
    return file_path

def generar_pdf_simulacion(titulo, precio, enganche, tasa, plazo, pago):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=titulo, ln=1, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Precio de la propiedad: ${precio:,.2f}", ln=1)
    pdf.cell(200, 10, txt=f"Enganche: {enganche}%", ln=1)
    pdf.cell(200, 10, txt=f"Tasa de interés: {tasa}%", ln=1)
    pdf.cell(200, 10, txt=f"Plazo: {plazo} años", ln=1)
    pdf.cell(200, 10, txt=f"Pago mensual estimado: ${pago:,.2f}", ln=1)
    pdf.ln(10)
    pdf.set_font("Arial", "I", 12)
    pdf.multi_cell(0, 10, txt="Esta corrida es un estimado.\nConsulta con tu asesor para un plan personalizado.")
    file_path = f"/mnt/data/Simulacion_{titulo.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(file_path)
    return file_path

# ---------------- FUNCIONES AUXILIARES ------------------
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
