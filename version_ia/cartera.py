import streamlit as st
import pandas as pd
import io
import requests
import json

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="AI Strategic Portfolio Scorecard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS PREMIUM (HIGH-END MINIMALISM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    :root { --primary-color: #3b82f6; }
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    .stApp { background: radial-gradient(circle at top right, #0F172A, #020617); color: #F8FAFC; }
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #3b82f6 !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 4px 6px -1px rgba(59, 130, 246, 0.5) !important;
    }
    [data-baseweb="slider"] > div > div > div, 
    [data-testid="stTickBar"] > div { background-color: #3b82f6 !important; }
    [data-baseweb="thumb"], [role="slider"] {
        background-color: #FFFFFF !important;
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59, 130, 246, 0.4) !important;
    }
    .stSlider label, .stSelectSlider label, [data-testid="stWidgetLabel"] p { color: #F8FAFC !important; }
    .stAlert, [data-testid="stNotificationContent"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        color: #3b82f6 !important;
        border: 1px solid #3b82f6 !important;
    }
    h1, h2, h3, h4, h5, h6 { font-family: 'Outfit', sans-serif !important; color: #F8FAFC !important; }
    [data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid #1E293B !important;
    }
    .stContainer {
        background-color: rgba(30, 41, 59, 0.3);
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    /* Estilos para la jerarquía del sidebar */
    .obj-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #1E293B;
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .obj-text { font-size: 0.85rem; color: #F8FAFC; margin: 0; }
    .weight-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.75rem;
        padding: 4px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAR MEMORIA ---
if 'proyectos' not in st.session_state:
    st.session_state['proyectos'] = []

# Objetivos Estratégicos Base
OBJETIVOS_BASE = [
    "Facturación y Margen (+12-15%)",
    "Captación de Clientes (+20%)",
    "Control de Stock (-25% roturas)",
    "Agilidad Presupuestos (-30% tiempo)",
    "Periodo de Cobro (-15% tiempo)",
    "Visibilidad Digital (Web + SEO)",
    "Sistema BI y Decisiones"
]

if 'orden_obj' not in st.session_state:
    st.session_state['orden_obj'] = OBJETIVOS_BASE

# State para los scores temporales
claves = {
    "Facturación y Margen (+12-15%)": "fact",
    "Captación de Clientes (+20%)": "capt",
    "Control de Stock (-25% roturas)": "stock",
    "Agilidad Presupuestos (-30% tiempo)": "pres",
    "Periodo de Cobro (-15% tiempo)": "cobro",
    "Visibilidad Digital (Web + SEO)": "vis",
    "Sistema BI y Decisiones": "bi"
}

for k in claves.values():
    if f"tmp_{k}" not in st.session_state:
        st.session_state[f"tmp_{k}"] = 0
    if f"score_{k}" not in st.session_state:
        st.session_state[f"score_{k}"] = "Nulo"

st.title("AI Strategic Portfolio Scorecard")
st.markdown("<p style='color: #94A3B8; font-size: 1.1rem;'>Metodología de priorización asistida por Inteligencia Artificial Local (Qwen).</p>", unsafe_allow_html=True)

# --- SISTEMA DE RANKING TÁCTIL ---
def mover_arriba(index):
    if index > 0:
        lista = st.session_state['orden_obj']
        lista[index], lista[index-1] = lista[index-1], lista[index]
        st.session_state['orden_obj'] = lista
        st.session_state['proyectos'] = []

st.sidebar.markdown("### Jerarquía de Objetivos")
for i, obj in enumerate(st.session_state['orden_obj']):
    with st.sidebar.container():
        c_txt, c_btn = st.columns([4, 1])
        c_txt.markdown(f"""
            <div class="obj-card">
                <span class="obj-text">{i+1}. {obj}</span>
            </div>
        """, unsafe_allow_html=True)
        if i > 0:
            if c_btn.button("▲", key=f"up_{i}", use_container_width=True):
                mover_arriba(i)
                st.rerun()
        else:
            c_btn.empty()

PESOS = [22, 18, 16, 14, 12, 10, 8]
map_pesos = {obj: PESOS[i] for i, obj in enumerate(st.session_state['orden_obj'])}

st.sidebar.markdown("---")
st.sidebar.markdown("#### Distribución de Pesos")
for obj, p in map_pesos.items():
    st.sidebar.markdown(f"""
        <div class="weight-row">
            <span>{obj}</span>
            <span style="color:#3b82f6; font-weight:600;">{p}%</span>
        </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
impacto_mode = st.sidebar.toggle("Modo Cualitativo", value=True)

# --- CONFIGURACIÓN DE IA ---
DEFINICIONES_OBJETIVOS = {
    "fact": "Facturación y Margen: Impacto directo en ingresos, rentabilidad, reducción de costes o mejora de márgenes.",
    "capt": "Captación de Clientes: Atracción de leads, conversión, expansión de mercado o fidelización.",
    "stock": "Control de Stock: Optimización de inventario, reducción de roturas o mejora logística.",
    "pres": "Agilidad Presupuestos: Reducción de tiempo en ofertas, automatización o eficiencia en preventa.",
    "cobro": "Periodo de Cobro: Flujo de caja, reducción de DSO, gestión de cobros o automatización.",
    "vis": "Visibilidad Digital: SEO, tráfico web, redes sociales o marca online.",
    "bi": "Sistema BI y Decisiones: Dashboards, calidad de datos, analítica o soporte estratégico."
}

# --- INTEGRACIÓN CON IA (OLLAMA QWEN) ---
def consultar_ia(descripcion):
    contexto_objetivos = "\n".join([f"- {k}: {v}" for k, v in DEFINICIONES_OBJETIVOS.items()])
    
    prompt = f"""
    Eres un Consultor Estratégico Senior. Evalúa el impacto de este proyecto en los KPIs de la empresa.
    
    DEFINICIONES DE OBJETIVOS (KPIs):
    {contexto_objetivos}
    
    PROYECTO:
    "{descripcion}"
    
    SISTEMA DE IMPACTO (Escala 0-3):
    - "Nulo": Sin impacto (0).
    - "Secundario": Impacto indirecto o menor (1).
    - "Significativo": Impacto directo y fuerte (2).
    - "Crítico": Transformador o fundamental (3).
    
    INSTRUCCIONES CRÍTICAS:
    - Responde EXCLUSIVAMENTE con el JSON.
    - Los valores deben ser uno de los 4 términos: "Nulo", "Secundario", "Significativo", "Crítico".
    
    Ejemplo: {{"fact": "Nulo", "capt": "Significativo", "stock": "Secundario", "pres": "Crítico", "cobro": "Nulo", "vis": "Nulo", "bi": "Secundario"}}
    """
    try:
        # Primero verificamos si Ollama está respondiendo
        requests.get("http://localhost:11434", timeout=3)
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100,
                    "stop": ["\n\n"]
                }
            },
            timeout=90
        )
        if response.status_code == 200:
            raw_response = response.json()['response']
            # Limpieza agresiva de JSON
            clean_json = raw_response.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean_json)
            # Mapeo de términos a valores numéricos (Nueva escala 0-3)
            mapping_inv = {
                "Nulo": 0, 
                "Secundario": 1, 
                "Significativo": 2, 
                "Critico": 3, "Crítico": 3
            }
            result = {}
            for k, v in data.items():
                v_str = str(v).strip().capitalize()
                if v_str in mapping_inv:
                    result[k] = mapping_inv[v_str]
                else:
                    # Fallback por si devuelve números (0-5)
                    try:
                        val = int(float(v))
                        # En escala 0-5: 0=0, 1-2=1, 3-4=2, 5=3
                        if val == 0: result[k] = 0
                        elif val <= 2: result[k] = 1
                        elif val <= 4: result[k] = 2
                        else: result[k] = 3
                    except:
                        result[k] = 0
            return result
        return None
    except Exception as e:
        st.error(f"Error AI: {e}")
        return None

# Helper para mapear valores a etiquetas del slider (Escala 0-3)
def get_closest_label(val):
    mapping_inv = {0: "Nulo", 1: "Secundario", 2: "Significativo", 3: "Crítico"}
    if val in mapping_inv:
        return mapping_inv[val]
    # Fallback para valores fuera de rango
    labels = {"Nulo": 0, "Secundario": 1, "Significativo": 2, "Crítico": 3}
    distancias = {label: abs(v - val) for label, v in labels.items()}
    return min(distancias, key=distancias.get)

# --- EVALUACIÓN DE PROYECTO ---
with st.container():
    st.markdown("### Evaluación con Asistencia IA")
    
    proyectos_nombres = [p["Proyecto"] for p in st.session_state['proyectos']]
    seleccion = st.selectbox("Seleccionar Registro", ["Nuevo Registro"] + proyectos_nombres, label_visibility="collapsed")

    proyecto_edit = None
    if seleccion != "Nuevo Registro":
        proyecto_edit = next(p for p in st.session_state['proyectos'] if p["Proyecto"] == seleccion)
        for k in claves.values():
            st.session_state[f"tmp_{k}"] = proyecto_edit[k]

    nombre_def = proyecto_edit["Proyecto"] if proyecto_edit else ""
    desc_area = st.text_area("Descripción del Proyecto", placeholder="Introduce el alcance detallado...")
    
    col_btn, col_reset = st.columns([1, 1])
    if col_btn.button("🤖 Generar Sugerencia IA", use_container_width=True, type="primary"):
        if desc_area:
            with st.spinner("Analizando con Qwen local (esto puede tardar hasta 90s)..."):
                sugerencia = consultar_ia(desc_area)
                if sugerencia:
                    st.session_state['last_ai_response'] = sugerencia
                    for k, v in sugerencia.items():
                        if f"tmp_{k}" in st.session_state:
                            st.session_state[f"tmp_{k}"] = v
                        # Sincronizar widget state para que el slider detecte el cambio
                        st.session_state[f"score_{k}"] = get_closest_label(v)
                    st.rerun()
        else:
            st.warning("Escribe una descripción.")

    if col_reset.button("🧹 Resetear Puntuación", use_container_width=True):
        for k in claves.values():
            st.session_state[f"tmp_{k}"] = 0
            st.session_state[f"score_{k}"] = "Nulo"
        if 'last_ai_response' in st.session_state:
            del st.session_state['last_ai_response']
        st.rerun()

    if 'last_ai_response' in st.session_state:
        with st.expander("Ver Respuesta de la IA (Debug)"):
            st.json(st.session_state['last_ai_response'])

    if impacto_mode:
        OPCIONES = ["Nulo", "Secundario", "Significativo", "Crítico"]
        MAPPING = {"Nulo": 0, "Secundario": 1, "Significativo": 2, "Crítico": 3}
    else:
        OPCIONES = ["0", "1", "2", "3"]
        MAPPING = {i: int(i) for i in OPCIONES}
    
    INV_MAPPING = {v: k for k, v in MAPPING.items()}

    def get_closest_label(val):
        if val in INV_MAPPING:
            return INV_MAPPING[val]
        # Si no existe (ej. val=1 en modo cualitativo), buscar el más cercano
        distancias = {label: abs(v - val) for label, v in MAPPING.items()}
        return min(distancias, key=distancias.get)

    with st.form("form_score"):
        nombre = st.text_input("Identificación del Proyecto", value=nombre_def, placeholder="Ej. Automatización Logística Q3")
        
        c1, c2 = st.columns(2)
        scores_final = {}
        
        for idx, (obj_full, safe_key) in enumerate(claves.items()):
            col = c1 if idx < 4 else c2
            with col:
                # El valor del slider se controla 100% por el Session State Key
                val = st.select_slider(
                    obj_full,
                    options=OPCIONES,
                    key=f"score_{safe_key}"
                )
                scores_final[safe_key] = MAPPING[val]
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Sincronizar con Cartera", type="primary")

# --- LÓGICA DE PERSISTENCIA ---
if submit and nombre:
    total_w = sum(scores_final[claves[obj]] * map_pesos[obj] for obj in map_pesos)
    # Nueva escala: máximo posible es 3 * 100% = 300
    alineacion = (total_w / 300) * 100
    
    datos = {"Proyecto": nombre, "Alineación (%)": round(alineacion, 2)}
    for obj_full, safe_key in claves.items():
        datos[safe_key] = scores_final[safe_key]

    idx_existente = next((i for i, p in enumerate(st.session_state['proyectos']) if p["Proyecto"] == nombre), None)

    if idx_existente is not None:
        st.session_state['proyectos'][idx_existente] = datos
        st.toast(f"Actualizado: {nombre}")
    else:
        st.session_state['proyectos'].append(datos)
        st.toast(f"Registrado: {nombre}")
    
    st.rerun()

# --- ANÁLISIS ---
st.divider()
st.markdown("### Dashboard de Cartera")

if len(st.session_state['proyectos']) > 0:
    df = pd.DataFrame(st.session_state['proyectos'])
    df_main = df[["Proyecto", "Alineación (%)"]].sort_values(by="Alineación (%)", ascending=False).reset_index(drop=True)
    st.dataframe(df_main.style.background_gradient(subset=['Alineación (%)'], cmap='Blues'), use_container_width=True, height=250)
    st.bar_chart(data=df_main, x="Proyecto", y="Alineación (%)", color="#3b82f6")
    
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Descargar Informe (CSV)", data=csv, file_name='cartera_estrategica_ia.csv', mime='text/csv')
    if st.button("Vaciar Cartera"):
        st.session_state['proyectos'] = []
        st.rerun()
else:
    st.markdown("<p style='color: #64748B;'>No hay registros activos.</p>", unsafe_allow_html=True)