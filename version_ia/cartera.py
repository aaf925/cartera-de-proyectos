import streamlit as st
import pandas as pd
import io
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import concurrent.futures
import time

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

if 'tmp_complejidad' not in st.session_state:
    st.session_state['tmp_complejidad'] = "Media"

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
    if f"reason_{k}" not in st.session_state:
        st.session_state[f"reason_{k}"] = ""

st.title("AI Strategic Portfolio Scorecard")
st.markdown("<p style='color: #94A3B8; font-size: 1.1rem;'>Metodología de priorización asistida por Inteligencia Artificial Local (Llama 3.1).</p>", unsafe_allow_html=True)

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

# --- IA CONFIGURABLE ---
st.sidebar.markdown("---")
st.sidebar.markdown("### Configuración LLM")
model_ia = st.sidebar.text_input("Modelo Ollama", value="qwen2.5:3b", help="Asegúrate de haber hecho 'ollama pull [modelo]' antes.")

# --- IA: RECOMENDACIÓN ESTRATÉGICA GLOBAL ---
def analizar_cartera_global(df_cartera, model):
    proyectos_str = "\n".join([
        f"- {row['Proyecto']}: Alineación {row['Alineación (%)']}%, Complejidad {row['Complejidad']}" 
        for _, row in df_cartera.iterrows()
    ])
    
    prompt = f"""
    Responde como un Senior Strategist.
    CARTERA:
    {proyectos_str}
    
    TAREA: Proporciona una recomendación de 3 puntos (con iconos) sobre esta cartera.
    REGLA: Máximo 30 palabras en total.
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 256}
            },
            timeout=60
        )
        if response.status_code == 200:
            return response.json()['response']
    except:
        pass
    return "Error al conectar con Ollama."

# --- INTEGRACIÓN CON IA (OLLAMA QWEN) ---
# --- INTEGRACIÓN CON IA (OLLAMA BATCH) ---

def apply_strategic_guardrails(nombre, desc, scores):
    """Filtro algorítmico POST-IA para asegurar coherencia de negocio (Fase 1 vs Fase 2)"""
    n = str(nombre).lower()
    d = str(desc).lower()
    
    is_crm = "crm" in n or "crm" in d
    is_erp = "erp" in n or "wms" in n or "gestión empresarial" in n
    is_bi = "bi" in n or "business intelligence" in n or "dashboard" in n or "cuadro de mando" in d
    is_doc = "documental" in n or "gestor documental" in d or "documentos" in n
    
    # 1. BI y Documental (Soporte/Analítica) -> Tope 1 (Secundario) en Motores de Ingresos y Stock
    if is_bi or is_doc:
        for k in ['fact', 'stock', 'capt', 'pres']:
            if k in scores and scores[k] > 1:
                scores[k] = 1 # Nerfeo a soporte operativo real
                
    # 2. CRM (Motor de Ventas) -> Obligatorio 3 (Crítico) en Captación y Presupuestos
    if is_crm:
        for k in ['capt', 'pres']:
            if k in scores and scores[k] < 3:
                scores[k] = 3
                
    # 3. ERP (Motor Operativo) -> Obligatorio 3 en Facturación y Stock
    if is_erp:
        for k in ['fact', 'stock']:
            if k in scores and scores[k] < 3:
                scores[k] = 3
                
    return scores

def consultar_ia_batch(descripcion, objetivos_dict, model):
    """
    Realiza una única consulta con reintentos.
    """
    kpis_context = "\n".join([f"- {slug.upper()}: {desc}" for slug, desc in objetivos_dict.items()])
    
    prompt = f"""
    Actúa como un Socio Director de Consultoría Estratégica.
    Evalúa el impacto del PROYECTO en los KPIs (Escala 0 a 3).
    
    PROYECTO: "{descripcion}"
    KPIs: {kpis_context}
    
    PROHIBICIONES ESTRATÉGICAS (MANDATORIO):
    1. BI/DASHBOARD: Prohibido puntuar más de 1 (Secundario) en FACT, STOCK, CAPT o PRES. El BI solo mide, no genera.
    2. GESTIÓN DOCUMENTAL: Prohibido puntuar más de 1 en FACT, STOCK o CAPT.
    3. CRM/COMERCIAL: Obligatorio puntuar 3 (Crítico) en CAPT y PRES.
    4. ERP/WMS: Impacto 3 (Crítico) en STOCK y FACT.
    
    PUNTUACIÓN: 0: Nulo, 1: Secundario, 2: Significativo, 3: Crítico.
    
    RESPONDE EXCLUSIVAMENTE CON UN JSON PLANO:
    {{
      "fact": 3,
      "capt": 2,
      ... (usa los slugs de arriba)
    }}
    """
    
    for intento in range(2): # 2 Intentos
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {"temperature": 0.0, "num_predict": 1024}
                },
                timeout=180
            )
            if response.status_code == 200:
                raw_response = response.json()['response']
                try:
                    clean_json = raw_response.strip().replace("```json", "").replace("```", "")
                    data = json.loads(clean_json)
                    data_clean = {str(k).lower(): v for k, v in data.items()}
                    val_map = {
                        "nulo": 0, "secundario": 1, "significativo": 2, "critico": 3, "crítico": 3,
                        "0": 0, "1": 1, "2": 2, "3": 3, 0: 0, 1: 1, 2: 2, 3: 3
                    }
                    resultados = {}
                    for slug in objetivos_dict:
                        val_raw = data_clean.get(slug.lower(), 0)
                        if isinstance(val_raw, dict):
                            val_raw = val_raw.get("impacto", 0)
                        score = val_map.get(str(val_raw).lower() if not isinstance(val_raw, (int, float)) else val_raw, 0)
                        resultados[slug] = {"score": score, "reason": "Evaluado."}
                    return resultados
                except Exception as e:
                    if intento == 1:
                        st.error(f"Error procesando JSON de `{descripcion[:20]}`...")
                        with st.expander("Ver Respuesta Raw"):
                            st.code(raw_response)
        except Exception as e:
            if intento == 1:
                st.error(f"⚠️ Error técnico: {e}")
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
        st.session_state['tmp_complejidad'] = proyecto_edit.get("Complejidad", "Media")

    nombre_def = proyecto_edit["Proyecto"] if proyecto_edit else ""
    desc_area = st.text_area("Descripción del Proyecto", placeholder="Introduce el alcance detallado...")
    complejidad = st.select_slider("Complejidad Estimada", options=["Baja", "Media", "Alta"], value=st.session_state['tmp_complejidad'])
    
    col_btn, col_reset = st.columns([1, 1])
    if col_btn.button("Generar Sugerencia IA", width="stretch", type="primary"):
        if desc_area:
            with st.status("**Analizando proyecto con Inteligencia Artificial...**", expanded=True) as status:
                st.write("Generando auditoría estratégica multicriterio...")
                start_time = time.time()
                
                res_dict = consultar_ia_batch(desc_area, DEFINICIONES_OBJETIVOS, model_ia)
                
                elapsed = time.time() - start_time
                
                if res_dict:
                    # Sincronizar Session State
                    for k in claves.values():
                        if k in res_dict:
                            st.session_state[f"tmp_{k}"] = res_dict[k]["score"]
                            st.session_state[f"score_{k}"] = get_closest_label(res_dict[k]["score"])
                            st.session_state[f"reason_{k}"] = res_dict[k]["reason"]
                    
                    st.session_state['last_ai_analysis'] = {
                        "global": "Completado.",
                        "time": elapsed
                    }
                    
                    status.update(label=f"¡Análisis completado en {elapsed:.1f}s!", state="complete", expanded=False)
                    st.rerun()
                else:
                    status.update(label="Error en el análisis. Inténtalo de nuevo.", state="error")
        else:
            st.warning("Escribe una descripción.")

    # --- CARGA MASIVA ---
    with st.expander("Carga Masiva y Procesamiento por Lotes"):
        uploaded_file = st.file_uploader("Subir CSV de Proyectos (Columnas: Proyecto, Descripcion, Complejidad)", type=["csv"])
        if uploaded_file:
            # Detectar separador automáticamente
            content = uploaded_file.getvalue().decode('utf-8')
            first_line = content.splitlines()[0] if content else ""
            sep = ';' if ';' in first_line else ','
            df_upload = pd.read_csv(io.StringIO(content), sep=sep)
            
            st.info(f"📂 Se han detectado {len(df_upload)} proyectos en el archivo.")
            st.dataframe(df_upload)
            
            if st.button("Analizar Todo el Archivo"):
                total_p = len(df_upload)
                with st.status(f"Procesando {total_p} proyectos...", expanded=True) as status:
                    audit_log = []
                    for idx, row in df_upload.iterrows():
                        p_nombre = str(row.get("Proyecto", f"Proyecto {idx+1}"))
                        p_desc = str(row.get("Descripción", row.get("Descripcion", "")))
                        p_compl = str(row.get("Complejidad", "Media"))
                        
                        if p_desc.strip():
                            msg_placeholder = status.empty()
                            msg_placeholder.write(f"🔄 **[{idx+1}/{total_p}]** Analizando: `{p_nombre}`...")
                            
                            res_dict = consultar_ia_batch(p_desc, DEFINICIONES_OBJETIVOS, model_ia)
                            
                            if res_dict:
                                scores_raw = {k: res_dict[k]["score"] for k in claves.values()}
                                
                                # Aplicar Salvavidas Algorítmico
                                scores_final_batch = apply_strategic_guardrails(p_nombre, p_desc, scores_raw)
                                
                                audit_row = {"Proyecto": p_nombre}
                                audit_row.update(scores_final_batch)
                                audit_log.append(audit_row)
                                
                                total_w = sum(scores_final_batch[claves[obj]] * map_pesos[obj] for obj in map_pesos)
                                alineacion = (total_w / 300) * 100
                                
                                datos = {
                                    "Proyecto": p_nombre, 
                                    "Alineación (%)": round(alineacion, 2),
                                    "Complejidad": p_compl
                                }
                                for obj_full, safe_key in claves.items():
                                    datos[safe_key] = scores_final_batch[safe_key]
                                
                                # Actualizar o añadir
                                idx_existente = next((i for i, p in enumerate(st.session_state['proyectos']) if p["Proyecto"] == p_nombre), None)
                                if idx_existente is not None:
                                    st.session_state['proyectos'][idx_existente] = datos
                                else:
                                    st.session_state['proyectos'].append(datos)
                                
                                msg_placeholder.write(f"🟢 **[{idx+1}/{total_p}]** Completado: `{p_nombre}`")
                            else:
                                msg_placeholder.write(f"🔴 **[{idx+1}/{total_p}]** Error en: `{p_nombre}`")
                    
                    status.update(label="¡Carga masiva finalizada!", state="complete")
                    if audit_log:
                        st.session_state['audit_log'] = audit_log
                    st.rerun()

    # Mostrar Auditoría si existe
    if 'audit_log' in st.session_state:
        with st.expander("📊 Ver Detalle de Auditoría IA (Puntuación por KPI)"):
            st.dataframe(st.session_state['audit_log'])
            if st.button("Limpiar Registro de Auditoría"):
                del st.session_state['audit_log']
                st.rerun()

    if col_reset.button("Resetear Puntuación", use_container_width=True):
        for k in claves.values():
            st.session_state[f"tmp_{k}"] = 0
            st.session_state[f"score_{k}"] = "Nulo"
            st.session_state[f"reason_{k}"] = ""
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
                if st.session_state[f"reason_{safe_key}"]:
                    st.markdown(f"> **IA:** *{st.session_state[f'reason_{safe_key}']}*")
                scores_final[safe_key] = MAPPING[val]
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Sincronizar con Cartera", type="primary")

# --- LÓGICA DE PERSISTENCIA ---
if submit and nombre:
    total_w = sum(scores_final[claves[obj]] * map_pesos[obj] for obj in map_pesos)
    # Nueva escala: máximo posible es 3 * 100% = 300
    alineacion = (total_w / 300) * 100
    
    datos = {
        "Proyecto": nombre, 
        "Alineación (%)": round(alineacion, 2),
        "Complejidad": complejidad
    }
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
    
    c_tab, c_graph = st.columns([1, 1])
    
    with c_tab:
        st.dataframe(
            df_main,
            column_config={
                "Proyecto": st.column_config.TextColumn("Proyecto", width="medium"),
                "Alineación (%)": st.column_config.ProgressColumn(
                    "Alineación",
                    help="Grado de ajuste estratégico",
                    format="%.2f%%",
                    min_value=0,
                    max_value=100,
                ),
            },
            hide_index=True,
            width="stretch"
        )

    with c_graph:
        # Gráfico Burbuja: Valor vs Complejidad
        mapping_compl = {"Baja": 1, "Media": 2, "Alta": 3}
        df["compl_num"] = df["Complejidad"].map(mapping_compl).fillna(2)
        
        fig = px.scatter(
            df, 
            x="Alineación (%)", 
            y="compl_num", 
            size="Alineación (%)",
            text="Proyecto",
            color="Alineación (%)",
            color_continuous_scale="RdYlGn",
            labels={"compl_num": "Complejidad (1=Baja, 3=Alta)"},
            template="plotly_dark",
            title="Matriz de Decisión Estratégica"
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            height=400,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False
        )
        fig.add_hline(y=2, line_dash="dot", line_color="gray", annotation_text="Complejidad Media")
        fig.add_vline(x=50, line_dash="dot", line_color="gray", annotation_text="Umbral Estratégico")
        
        st.plotly_chart(fig)

    # --- RECOMENDACIÓN GLOBAL IA ---
    st.markdown("#### 🤖 Advisor Estratégico IA")
    if st.button("Generar Recomendación de Cartera"):
        with st.spinner("IA analizando balance de cartera..."):
            rec = analizar_cartera_global(df, model_ia)
            st.info(rec)

    # Gráfico Radar para el Seleccionado (Si aplica)
    if seleccion != "Nuevo Registro":
        st.markdown(f"#### Perfil Estratégico: {seleccion}")
        proj_data = next(p for p in st.session_state['proyectos'] if p["Proyecto"] == seleccion)
        
        categories = list(claves.keys())
        values = [proj_data[k] for k in claves.values()]
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(59, 130, 246, 0.4)',
            line=dict(color='#3b82f6', width=2),
            name=seleccion
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 3], tickfont_size=8, gridcolor="rgba(255,255,255,0.1)"),
                angularaxis=dict(tickfont_size=10, gridcolor="rgba(255,255,255,0.1)"),
                bgcolor="rgba(0,0,0,0)"
            ),
            showlegend=False,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            height=400,
            margin=dict(l=80, r=80, t=40, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Descargar Informe (CSV)", data=csv, file_name='cartera_estrategica_ia.csv', mime='text/csv')
    if st.button("Vaciar Cartera"):
        st.session_state['proyectos'] = []
        st.rerun()
else:
    st.markdown("<p style='color: #64748B;'>No hay registros activos.</p>", unsafe_allow_html=True)