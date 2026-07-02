import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# Librerías oficiales de Google para Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuración inicial
st.set_page_config(page_title="Mi Life OS", page_icon="🧠", layout="centered")

# Definir alcances de permisos para Google
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# RUTAS ABSOLUTAS (Tus archivos seguros)
BASE_DATOS = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\mis_ideas.csv"
BASE_FINANZAS = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\mis_finanzas.csv"
CREDENTIALS_FILE = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\credentials.json.json"
TOKEN_FILE = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\token.json"

# Asegurar que existan archivos CSV iniciales
if not os.path.exists(BASE_DATOS):
    pd.DataFrame(columns=["Idea", "Categoria"]).to_csv(BASE_DATOS, index=False)
if not os.path.exists(BASE_FINANZAS):
    pd.DataFrame(columns=["Tipo", "Ambito", "Concepto", "Monto"]).to_csv(BASE_FINANZAS, index=False)

# --- DICCIONARIO DE TUS CALENDARIOS REALES DE GOOGLE ---
DICCIONARIO_CALENDARIOS = {
    "👤 Personal": "gabsmtz250@gmail.com", 
    "📱 Creación de contenido": "2d64962c73e2e400b80d434f8bfe25e2af893fa2869b5e7a5a727e19a4b7f45e@group.calendar.google.com",
    "🌱 Desarrollo personal": "b634372c034812ab13385d7736e3d99854c89a560ae5572a2b7e3f6acba19d5d@group.calendar.google.com",
    "🎓 Escuela": "62a1e5e2e52e138c7da86579436eb3f44c2fccf7c67255b6979af3a355aabd6b@group.calendar.google.com",
    "🍋 LeM": "c6e28a534696e0e9650232a5adced1027560a83c4a2f154a48f8cb6dccf3203b@group.calendar.google.com",
    "💻 Tecnolochicas": "c2dc5b93f56610e1e28b36acd30f8630ff24bf37e72010ff219d7398967e7a68@group.calendar.google.com"
}

# Función de conexión a Google
def obtener_servicio_calendar():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                st.error("⚠️ No se encontró el archivo credentials.json")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

# Racha motivacional
st.markdown("<h3 style='text-align: right;'>🔥 Racha: 3 días</h3>", unsafe_allow_html=True)

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["🏠 Inicio", "💰 Finanzas", "🗄️ Mis Listas"])

# --- PESTAÑA 1: INICIO (OMNIBAR) ---
with tab1:
    st.title("Mi Centro de Control 🚀")
    
    todo_texto = st.text_input(
        "¿Qué tienes en mente?", 
        placeholder="Escribe una idea, pendiente, reunión o algo para buscar...",
        label_visibility="collapsed",
        key="omnibar_input"
    )
    
    st.write("📅 *Configuración del Evento (Si vas a agendar en Google):*")
    
    # Fila 1: Fecha y Hora
    col_fecha, col_hora = st.columns(2)
    with col_fecha:
        fecha_elegida = st.date_input("Fecha", value=datetime.today(), key="fecha_agenda")
    with col_hora:
        hora_elegida = st.time_input("Hora de Inicio", key="hora_agenda")
        
    # Fila 2: Duración y Selección de Calendario destino
    col_duracion, col_destino = st.columns(2)
    with col_duracion:
        duracion_horas = st.number_input("Duración (Horas)", min_value=0.5, max_value=24.0, value=1.0, step=0.5)
    with col_destino:
        calendario_visual = st.selectbox("¿A qué pilar va?", list(DICCIONARIO_CALENDARIOS.keys()))
    
    st.write("")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        botón_guardar = st.button("📥 Guardar Idea", use_container_width=True)
    with col2:
        botón_agendar = st.button("📅 Agendar en Google", use_container_width=True)
    with col3:
        botón_buscar = st.button("🔍 Buscar", use_container_width=True)
        
    # Lógica Guardar Idea
    if "mostrando_pilares" not in st.session_state:
        st.session_state.mostrando_pilares = False
    if "texto_a_guardar" not in st.session_state:
        st.session_state.texto_a_guardar = ""

    if botón_guardar:
        if todo_texto.strip() == "":
            st.warning("¡Escribe algo en la barra primero!")
        else:
            st.session_state.mostrando_pilares = True
            st.session_state.texto_a_guardar = todo_texto

    if st.session_state.mostrando_pilares:
        st.subheader("¿Dónde lo guardamos?")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        def guardar_en_db(categoria_seleccionada):
            nueva_fila = pd.DataFrame([{"Idea": st.session_state.texto_a_guardar, "Categoria": categoria_seleccionada}])
            nueva_fila.to_csv(BASE_DATOS, mode='a', header=False, index=False)
            st.success(f"¡Guardado en {categoria_seleccionada}! 🎉")
            st.session_state.mostrando_pilares = False
            st.rerun()

        with c1: 
            if st.button("📱 Contenido"): guardar_en_db("Contenido")
        with c2: 
            if st.button("💼 Negocios"): guardar_en_db("Negocios")
        with c3: 
            if st.button("🎓 Estudios"): guardar_en_db("Estudios")
        with c4: 
            if st.button("🌱 Personal"): guardar_en_db("Personal")
        with c5: 
            if st.button("🎲 Random"): guardar_en_db("Random")

    # Lógica Agendar (¡Con Duración y Calendario Múltiple Real!)
    if botón_agendar:
        if todo_texto.strip() == "":
            st.warning("¡Escribe el título del evento primero!")
        else:
            try:
                with st.spinner("Conectando con Google Calendar... 🚀"):
                    service = obtener_servicio_calendar()
                    
                    if service:
                        # Formatear inicio
                        fecha_str = fecha_elegida.strftime('%Y-%m-%d')
                        hora_str = hora_elegida.strftime('%H:%M:%S')
                        fecha_hora_str = f"{fecha_str}T{hora_str}"
                        
                        # Calcular fin exacto según las horas elegidas
                        dt_inicio = datetime.combine(fecha_elegida, hora_elegida)
                        dt_fin = dt_inicio + timedelta(minutes=int(duracion_horas * 60))
                        fecha_hora_fin_str = dt_fin.strftime('%Y-%m-%dT%H:%M:%S')
                        
                        # Obtener el ID real del mapa que armamos arriba
                        id_calendario_real = DICCIONARIO_CALENDARIOS[calendario_visual]
                        
                        event = {
                          'summary': todo_texto,
                          'start': {
                            'dateTime': fecha_hora_str,
                            'timeZone': 'America/Mexico_City', 
                          },
                          'end': {
                            'dateTime': fecha_hora_fin_str, 
                            'timeZone': 'America/Mexico_City',
                          },
                        }
                        
                        # Insertar usando el ID seleccionado dinámicamente
                        event = service.events().insert(calendarId=id_calendario_real, body=event).execute()
                        st.balloons()
                        st.success(f"¡Agendado en '{calendario_visual}' por {duracion_horas} hora(s)! ✨")
            except Exception as e:
                st.error(f"Hubo un detalle en la conexión: {e}")

    # Lógica Buscar
    if botón_buscar:
        if todo_texto.strip() == "":
            st.warning("¡Escribe una palabra clave primero!")
        else:
            df_completo = pd.read_csv(BASE_DATOS)
            resultados = df_completo[df_completo["Idea"].str.contains(todo_texto, case=False, na=False)]
            if resultados.empty:
                st.info(f"❌ No se encontró nada con '{todo_texto}'.")
            else:
                st.subheader(f"🔍 Resultados para: '{todo_texto}'")
                for idx, row in resultados.iterrows():
                    st.markdown(f"📌 **[{row['Categoria']}]** {row['Idea']}")

# --- PESTAÑA 2: FINANZAS ---
with tab2:
    st.title("Control de Finanzas 💸")
    df_fin = pd.read_csv(BASE_FINANZAS)
    total_personal = 0.0
    total_empresa = 0.0
    if not df_fin.empty:
        for _, row in df_fin.iterrows():
            monto = float(row["Monto"])
            if row["Tipo"] == "Gasto": monto = -monto
            if row["Ambito"] == "Personal": total_personal += monto
            else: total_empresa += monto

    col_per, col_emp = st.columns(2)
    with col_per: st.metric(label="Balance Personal 👤", value=f"${total_personal:,.2f}")
    with col_emp: st.metric(label="Balance Emprendimiento 💼", value=f"${total_empresa:,.2f}")
    st.divider()
    
    with st.form("form_finanzas", clear_on_submit=True):
        c_t1, c_t2 = st.columns(2)
        with c_t1: tipo_mov = st.radio("Tipo:", ["Ingreso", "Gasto"], horizontal=True)
        with c_t2: ambito_mov = st.radio("Ámbito:", ["Personal", "Emprendimiento"], horizontal=True)
        concepto_mov = st.text_input("¿Qué fue?")
        monto_mov = st.number_input("Monto ($)", min_value=0.0, step=10.0)
        if st.form_submit_button("💰 Registrar Movimiento"):
            if concepto_mov.strip() != "" and monto_mov > 0:
                pd.DataFrame([{"Tipo": tipo_mov, "Ambito": ambito_mov, "Concepto": concepto_mov, "Monto": monto_mov}]).to_csv(BASE_FINANZAS, mode='a', header=False, index=False)
                st.rerun()

    if not df_fin.empty:
        st.write("### Últimos movimientos")
        for index, row in df_fin.iloc[::-1].iterrows():
            col_info, col_del = st.columns([4, 1])
            with col_info:
                color = "🟩" if row["Tipo"] == "Ingreso" else "🟥"
                st.markdown(f"{color} **{row['Concepto']}** | ${float(row['Monto']):,.2f} *({row['Ambito']})*")
            with col_del:
                if st.button("🗑️", key=f"btn_del_fin_{index}"):
                    pd.read_csv(BASE_FINANZAS).drop(index).to_csv(BASE_FINANZAS, index=False)
                    st.rerun()

# --- PESTAÑA 3: MIS LISTAS ---
with tab3:
    st.title("Tu Baúl de Ideas 🗄️")
    if os.path.exists(BASE_DATOS):
        df = pd.read_csv(BASE_DATOS)
        if df.empty:
            st.info("Tu baúl está vacío.")
        else:
            categoria_filtro = st.selectbox("Filtrar por pilar:", ["Todos", "Contenido", "Negocios", "Estudios", "Personal", "Random"])
            df_filtrado = df if categoria_filtro == "Todos" else df[df["Categoria"] == categoria_filtro]
            for index, row in df_filtrado.iterrows():
                col_idea, col_accion = st.columns([4, 1])
                with col_idea: st.markdown(f"**• {row['Idea']}** *(Pilar: {row['Categoria']})*")
                with col_accion:
                    if st.button("🗑️ Done", key=f"btn_borrar_{index}"):
                        pd.read_csv(BASE_DATOS).drop(index).to_csv(BASE_DATOS, index=False)
                        st.rerun()