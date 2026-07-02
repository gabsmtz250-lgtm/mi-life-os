import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime, timedelta

# Librerías oficiales de Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuración inicial
st.set_page_config(page_title="Mi Life OS", page_icon="🧠", layout="centered")

# Modificamos los SCOPES para incluir Calendar Y Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/spreadsheets'
]

# RUTAS LOCALES (Solo se usan si corres la app en tu lap)
CREDENTIALS_FILE = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\credentials.json.json"
TOKEN_FILE = r"C:\Users\gabyc\OneDrive\Escritorio\Mi App\token.json"

# ID DE TU HOJA DE GOOGLE SHEETS
SPREADSHEET_ID = "1B7kBFaPcXAty2ITHgfZub_6vz_ATJ0wfAvQMf1j1f8M"

# --- DICCIONARIO DE TUS CALENDARIOS DE GOOGLE ---
DICCIONARIO_CALENDARIOS = {
    "👤 Personal": "gabsmtz250@gmail.com", 
    "📱 Creación de contenido": "2d64962c73e2e400b80d434f8bfe25e2af893fa2869b5e7a5a727e19a4b7f45e@group.calendar.google.com",
    "🌱 Desarrollo personal": "b634372c034812ab13385d7736e3d99854c89a560ae5572a2b7e3f6acba19d5d@group.calendar.google.com",
    "🎓 Escuela": "62a1e5e2e52e138c7da86579436eb3f44c2fccf7c67255b6979af3a355aabd6b@group.calendar.google.com",
    "🍋 LeM": "c6e28a534696e0e9650232a5adced1027560a83c4a2f154a48f8cb6dccf3203b@group.calendar.google.com",
    "💻 Tecnolochicas": "c2dc5b93f56610e1e28b36acd30f8630ff24bf37e72010ff219d7398967e7a68@group.calendar.google.com"
}

# Función híbrida de conexión (Local vs Nube Segura)
def obtener_credenciales_google():
    # Intento 1: Buscar en la caja fuerte de Streamlit Cloud (Celular)
    if "google_credentials" in st.secrets:
        try:
            info_token = json.loads(st.secrets["google_credentials"]["token_json"])
            return Credentials.from_authorized_user_info(info_token, SCOPES)
        except Exception as e:
            st.error(f"Error con las credenciales de la nube: {e}")
            return None

    # Intento 2: Si no está en la nube, corre en tu Laptop usando tus archivos
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
    return creds

# Inicializar estados de la pantalla
if "mostrar_formulario_agenda" not in st.session_state:
    st.session_state.mostrar_formulario_agenda = False
if "mostrando_pilares" not in st.session_state:
    st.session_state.mostrando_pilares = False
if "texto_capturado" not in st.session_state:
    st.session_state.texto_capturado = ""

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
    
    st.write("")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Guardar Idea", use_container_width=True):
            if todo_texto.strip() == "": st.warning("¡Escribe algo primero!")
            else:
                st.session_state.mostrando_pilares = True
                st.session_state.mostrar_formulario_agenda = False
                st.session_state.texto_capturado = todo_texto
    with col2:
        if st.button("📅 Agendar en Google", use_container_width=True):
            if todo_texto.strip() == "": st.warning("¡Escribe el título del evento primero!")
            else:
                st.session_state.mostrar_formulario_agenda = True
                st.session_state.mostrando_pilares = False
                st.session_state.texto_capturado = todo_texto
    with col3:
        botón_buscar = st.button("🔍 Buscar", use_container_width=True)

    # LÓGICA GUARDAR IDEA
    if st.session_state.mostrando_pilares:
        st.subheader("¿Dónde lo guardamos?")
        c1, c2, c3, c4, c5 = st.columns(5)
        
        def guardar_en_sheets(categoria_seleccionada):
            try:
                creds = obtener_credenciales_google()
                sheets_service = build('sheets', 'v4', credentials=creds)
                valores = [[st.session_state.texto_capturado, categoria_seleccionada]]
                body = {'values': valores}
                sheets_service.spreadsheets().values().append(
                    spreadsheetId=SPREADSHEET_ID, range="Ideas!A:B",
                    valueInputOption="USER_ENTERED", body=body).execute()
                st.success(f"¡Guardado en {categoria_seleccionada} dentro de Google Sheets! 🎉")
                st.session_state.mostrando_pilares = False
                st.rerun()
            except Exception as e: st.error(f"Error al guardar en Sheets: {e}")

        with c1: 
            if st.button("📱 Contenido"): guardar_en_sheets("Contenido")
        with c2: 
            if st.button("💼 Negocios"): guardar_en_sheets("Negocios")
        with c3: 
            if st.button("🎓 Estudios"): guardar_en_sheets("Estudios")
        with c4: 
            if st.button("🌱 Personal"): guardar_en_sheets("Personal")
        with c5: 
            if st.button("🎲 Random"): guardar_en_sheets("Random")

    # LÓGICA AGENDAR EVENTO
    if st.session_state.mostrar_formulario_agenda:
        with st.form("formulario_agenda_oculto"):
            st.subheader(f"📅 Configurar Evento: '{st.session_state.texto_capturado}'")
            col_f, col_h = st.columns(2)
            with col_f: fecha_e = st.date_input("Fecha", value=datetime.today())
            with col_h: hora_e = st.time_input("Hora de Inicio")
            
            col_d, col_c = st.columns(2)
            with col_d: duracion_h = st.number_input("Duración (Horas)", min_value=0.5, max_value=24.0, value=1.0, step=0.5)
            with col_c: calendario_v = st.selectbox("¿A qué pilar va?", list(DICCIONARIO_CALENDARIOS.keys()))
            
            if st.form_submit_button("🚀 Mandar definitivamente a Google Calendar"):
                try:
                    with st.spinner("Mandando a Google..."):
                        creds = obtener_credenciales_google()
                        cal_service = build('calendar', 'v3', credentials=creds)
                        
                        fecha_str = fecha_e.strftime('%Y-%m-%d')
                        hora_str = hora_e.strftime('%H:%M:%S')
                        fecha_hora_str = f"{fecha_str}T{hora_str}"
                        
                        dt_inicio = datetime.combine(fecha_e, hora_e)
                        dt_fin = dt_inicio + timedelta(minutes=int(duracion_h * 60))
                        fecha_hora_fin_str = dt_fin.strftime('%Y-%m-%dT%H:%M:%S')
                        
                        id_cal = DICCIONARIO_CALENDARIOS[calendario_v]
                        event = {
                          'summary': st.session_state.texto_capturado,
                          'start': {'dateTime': fecha_hora_str, 'timeZone': 'America/Mexico_City'},
                          'end': {'dateTime': fecha_hora_fin_str, 'timeZone': 'America/Mexico_City'},
                        }
                        cal_service.events().insert(calendarId=id_cal, body=event).execute()
                        st.balloons()
                        st.success(f"¡Agendado con éxito en '{calendario_v}'! 🎉")
                        st.session_state.mostrar_formulario_agenda = False
                        st.rerun()
                except Exception as e: st.error(f"Error: {e}")

    # OMNIBUSCADOR
    if botón_buscar:
        if todo_texto.strip() == "": st.warning("¡Escribe una palabra clave primero!")
        else:
            encontró_algo = False
            st.markdown("---")
            
            with st.spinner("Escarbando en tus ideas... 🗄️"):
                try:
                    creds = obtener_credenciales_google()
                    sheets_service = build('sheets', 'v4', credentials=creds)
                    result = sheets_service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="Ideas!A:B").execute()
                    filas = result.get('values', [])
                    
                    if filas and len(filas) > 1:
                        df_completo = pd.DataFrame(filas[1:], columns=filas[0])
                        resultados_ideas = df_completo[df_completo["Idea"].str.contains(todo_texto, case=False, na=False)]
                        
                        if not resultados_ideas.empty:
                            encontró_algo = True
                            st.subheader("💡 Ideas encontradas en tu Baúl:")
                            for idx, row in resultados_ideas.iterrows():
                                st.markdown(f"📌 **[{row['Categoria']}]** {row['Idea']}")
                except Exception as e:
                    st.error(f"Detalle al buscar ideas: {e}")
            
            st.write("") 
            
            with st.spinner("Rastreando tus calendarios de Google... 📅"):
                try:
                    creds = obtener_credenciales_google()
                    cal_service = build('calendar', 'v3', credentials=creds)
                    
                    ahora_iso = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
                    un_mes_despues_iso = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
                    
                    eventos_encontrados = []
                    
                    for nombre_cal, id_cal in DICCIONARIO_CALENDARIOS.items():
                        try:
                            events_result = cal_service.events().list(
                                calendarId=id_cal, 
                                timeMin=ahora_iso, 
                                timeMax=un_mes_despues_iso,
                                singleEvents=True, 
                                orderBy='startTime',
                                q=todo_texto 
                            ).execute()
                            
                            items = events_result.get('items', [])
                            for e in items:
                                eventos_encontrados.append((nombre_cal, e))
                        except:
                            pass 
                    
                    if eventos_encontrados:
                        encontró_algo = True
                        st.subheader("📅 Eventos agendados en Google Calendar (Próximos 30 días):")
                        
                        for nombre_cal, ev in eventos_encontrados:
                            titulo = ev.get('summary', 'Sin título')
                            inicio_raw = ev.get('start', {}).get('dateTime', ev.get('start', {}).get('date', ''))
                            
                            try:
                                dt = datetime.strptime(inicio_raw[:19], '%Y-%m-%dT%H:%M:%S')
                                fecha_bonita = dt.strftime('%d de %b, %I:%M %p')
                            except:
                                fecha_bonita = inicio_raw 
                                
                            st.markdown(f"🗓️ **{titulo}** | `{fecha_bonita}` *({nombre_cal})*")
                except Exception as e:
                    st.error(f"Detalle al buscar en Google Calendar: {e}")
            
            if not encontró_algo:
                st.info(f"❌ No encontramos absolutamente nada con la palabra '{todo_texto}' ni en tus Listas ni en tus Calendarios.")

# --- PESTAÑA 2: FINANZAS ---
with tab2:
    st.title("Control de Finanzas 💸")
    try:
        creds = obtener_credenciales_google()
        sheets_service = build('sheets', 'v4', credentials=creds)
        result_fin = sheets_service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="Finanzas!A:E").execute()
        filas_fin = result_fin.get('values', [])
        
        total_personal = 0.0
        total_empresa = 0.0
        df_fin = pd.DataFrame()
        
        if filas_fin and len(filas_fin) > 1:
            df_fin = pd.DataFrame(filas_fin[1:], columns=filas_fin[0])
            for _, row in df_fin.iterrows():
                monto = float(row["Monto"])
                if row["Tipo"] == "Gasto": monto = -monto
                if row["Ambito"] == "Personal": total_personal += monto
                else: total_empresa += monto

        col_per, col_emp = st.columns(2)
        with col_per: st.metric(label="Balance Personal 👤", value=f"${total_personal:,.2f}")
        with col_emp: st.metric(label="Balance Emprendimiento 💼", value=f"${total_empresa:,.2f}")
        st.divider()
        
        with st.form("form_finanzas_sheets", clear_on_submit=True):
            c_t1, c_t2 = st.columns(2)
            with c_t1: tipo_mov = st.radio("Tipo:", ["Ingreso", "Gasto"], horizontal=True)
            with c_t2: ambito_mov = st.radio("Ámbito:", ["Personal", "Emprendimiento"], horizontal=True)
            concepto_mov = st.text_input("¿Qué fue?")
            monto_mov = st.number_input("Monto ($)", min_value=0.0, step=10.0)
            if st.form_submit_button("💰 Registrar Movimiento"):
                if concepto_mov.strip() != "" and monto_mov > 0:
                    fecha_hoy_str = datetime.today().strftime('%Y-%m-%d')
                    valores = [[tipo_mov, ambito_mov, concepto_mov, str(monto_mov), fecha_hoy_str]]
                    body = {'values': valores}
                    sheets_service.spreadsheets().values().append(
                        spreadsheetId=SPREADSHEET_ID, range="Finanzas!A:E",
                        valueInputOption="USER_ENTERED", body=body).execute()
                    st.rerun()

        if not df_fin.empty:
            st.write("### Últimos movimientos")
            for index, row in df_fin.iloc[::-1].iterrows():
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    color = "🟩" if row["Tipo"] == "Ingreso" else "🟥"
                    f_reg = row["Fecha"] if "Fecha" in row else ""
                    st.markdown(f"{color} **{row['Concepto']}** | ${float(row['Monto']):,.2f} *({row['Ambito']})* {f_reg}")
                with col_del:
                    if st.button("🗑️", key=f"btn_del_fin_{index}"):
                        df_actualizado = df_fin.drop(index)
                        nuevos_valores_fin = [["Tipo", "Ambito", "Concepto", "Monto", "Fecha"]] + df_actualizado.values.tolist()
                        
                        sheets_service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range="Finanzas!A:E").execute()
                        body_limpio = {'values': nuevos_valores_fin}
                        sheets_service.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID, range="Finanzas!A:E", 
                            valueInputOption="USER_ENTERED", body=body_limpio).execute()
                        st.rerun()
                        
    except Exception as e: st.error(f"Error en Finanzas: {e}")

# --- PESTAÑA 3: MIS LISTAS ---
with tab3:
    st.title("Tu Baúl de Ideas 🗄️")
    try:
        creds = obtener_credenciales_google()
        sheets_service = build('sheets', 'v4', credentials=creds)
        result_listas = sheets_service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range="Ideas!A:B").execute()
        filas_listas = result_listas.get('values', [])
        
        if not filas_listas or len(filas_listas) <= 1: st.info("Tu baúl está vacío.")
        else:
            df_listas = pd.DataFrame(filas_listas[1:], columns=filas_listas[0])
            categoria_filtro = st.selectbox("Filtrar por pilar:", ["Todos", "Contenido", "Negocios", "Estudios", "Personal", "Random"])
            df_filtrado = df_listas if categoria_filtro == "Todos" else df_listas[df_listas["Categoria"] == categoria_filtro]
            
            for index, row in df_filtrado.iterrows():
                col_idea, col_accion = st.columns([4, 1])
                with col_idea: 
                    st.markdown(f"**• {row['Idea']}** *(Pilar: {row['Categoria']})*")
                with col_accion:
                    if st.button("🗑️ Done", key=f"btn_borrar_sheets_{index}"):
                        df_listas_nueva = df_listas.drop(index)
                        nuevos_valores = [["Idea", "Categoria"]] + df_listas_nueva.values.tolist()
                        sheets_service.spreadsheets().values().clear(spreadsheetId=SPREADSHEET_ID, range="Ideas!A:B").execute()
                        body_actualizado = {'values': nuevos_valores}
                        sheets_service.spreadsheets().values().update(
                            spreadsheetId=SPREADSHEET_ID, range="Ideas!A:B",
                            valueInputOption="USER_ENTERED", body=body_actualizado).execute()
                        st.rerun()
                        
    except Exception as e: st.error(f"Error en Listas: {e}")