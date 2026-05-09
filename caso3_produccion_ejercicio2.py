import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ── Configuración de página ────────────────────────────────────
st.set_page_config(
    page_title="MetalParts Analytics",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Estilos CSS ────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
  h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

  [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0f2027 0%, #1a2f1a 50%, #2a3d2a 100%);
  }
  [data-testid="stSidebar"] * { color: #e0f5e0 !important; }

  .kpi-card {
      background: linear-gradient(135deg, #1a2e1a 0%, #162616 100%);
      border: 1px solid rgba(0,200,80,0.2);
      border-radius: 12px;
      padding: 0.7rem 1rem;
      text-align: center;
      box-shadow: 0 4px 24px rgba(0,200,80,0.08);
      transition: transform 0.2s;
  }
  .kpi-card:hover { transform: translateY(-3px); }
  .kpi-value {
      font-family: 'Syne', sans-serif;
      font-size: 1.2rem;
      font-weight: 800;
      color: #00e066;
      line-height: 1.1;
  }
  .kpi-label {
      font-size: 0.68rem;
      color: #7a9980;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-top: 0.2rem;
  }
  .kpi-icon { font-size: 1rem; margin-bottom: 0.2rem; }

  .alerta-baja {
      background: linear-gradient(135deg, #3d2000, #1a0f00);
      border: 1px solid #ff8800;
      border-radius: 12px;
      padding: 1rem 1.4rem;
      color: #ffcc88;
      font-size: 0.9rem;
  }
  .section-title {
      font-family: 'Syne', sans-serif;
      font-size: 1.05rem;
      font-weight: 700;
      color: #00e066;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      border-left: 3px solid #00e066;
      padding-left: 0.7rem;
      margin-bottom: 0.8rem;
  }
  [data-testid="stAppViewContainer"] { background: #0a1a0a; }
  [data-testid="stHeader"] { background: transparent; }
  hr { border-color: rgba(0,200,80,0.15); }
</style>
""", unsafe_allow_html=True)

# ── Carga de datos ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_csv('caso3_produccion_dataset.csv')
    df['fecha_produccion'] = pd.to_datetime(df['fecha_produccion'])
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("⚠️ No se encontró 'caso3_produccion_dataset.csv'. Asegúrate de que esté en el mismo directorio.")
    st.stop()

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 MetalParts")
    st.markdown("**Analytics Dashboard**")
    st.divider()
    st.markdown("### 🔍 Filtros")

    lineas = st.multiselect(
        "Línea de producción",
        options=sorted(df['linea_produccion'].unique()),
        default=sorted(df['linea_produccion'].unique())
    )
    turnos = st.multiselect(
        "Turno",
        options=sorted(df['turno'].unique()),
        default=sorted(df['turno'].unique())
    )
    maquinas = st.multiselect(
        "Máquina",
        options=sorted(df['maquina'].unique()),
        default=sorted(df['maquina'].unique())
    )

    st.divider()
    solo_baja_eficiencia = st.checkbox("⚠️ Solo baja eficiencia (<70% y defectos >5%)")
    st.divider()
    st.caption("MetalParts Manufacturing · 4 líneas de producción")

# ── Filtrar datos ──────────────────────────────────────────────
df_f = df[
    df['linea_produccion'].isin(lineas) &
    df['turno'].isin(turnos) &
    df['maquina'].isin(maquinas)
]

if solo_baja_eficiencia:
    df_f = df_f[(df_f['eficiencia_pct'] < 70) & (df_f['tasa_defectos_pct'] > 5)]

# ── HEADER ─────────────────────────────────────────────────────
st.markdown("# 🏭 MetalParts Analytics")
st.markdown(f"**MetalParts Manufacturing** · `{len(df_f):,}` registros filtrados de `{len(df):,}` totales")
st.divider()

# ── KPIs ───────────────────────────────────────────────────────
total_unidades      = df_f['unidades_producidas'].sum()
eficiencia_promedio = df_f['eficiencia_pct'].mean() if len(df_f) else 0
total_defectuosas   = df_f['unidades_defectuosas'].sum()
costo_total         = df_f['costo_produccion_cop'].sum()
baja_ef_count       = len(df_f[(df_f['eficiencia_pct'] < 70) & (df_f['tasa_defectos_pct'] > 5)])

c1, c2, c3, c4, c5 = st.columns(5)
for col, icon, val, label in [
    (c1, "📦", f"{total_unidades:,}",          "Unidades Producidas"),
    (c2, "⚙️", f"{eficiencia_promedio:.1f}%",  "Eficiencia Promedio"),
    (c3, "❌", f"{total_defectuosas:,}",        "Unidades Defectuosas"),
    (c4, "💰", f"${costo_total/1e6:.1f}M",      "Costo Producción COP"),
    (c5, "⚠️", str(baja_ef_count),             "Órdenes Críticas"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── FILA 1: Barras eficiencia + Pie causas paro ────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown('<div class="section-title">⚙️ Eficiencia Promedio por Línea</div>', unsafe_allow_html=True)
    eficiencia_linea = (
        df_f.groupby('linea_produccion')
            .agg(
                eficiencia_promedio=('eficiencia_pct', 'mean'),
                unidades_producidas=('unidades_producidas', 'sum'),
                unidades_defectuosas=('unidades_defectuosas', 'sum')
            )
            .round(2).reset_index()
    )
    fig1 = px.bar(
        eficiencia_linea,
        x='linea_produccion', y='eficiencia_promedio',
        color='eficiencia_promedio', color_continuous_scale='RdYlGn',
        text_auto='.1f',
        labels={'linea_produccion': 'Línea', 'eficiencia_promedio': 'Eficiencia (%)'}
    )
    fig1.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', coloraxis_showscale=False,
        height=320, margin=dict(l=0, r=10, t=10, b=30)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.markdown('<div class="section-title">⏱️ Causas de Paro</div>', unsafe_allow_html=True)
    paros_causa = (
        df_f.groupby('causa_paro')
            .agg(tiempo_total_min=('tiempo_paro_min', 'sum'))
            .reset_index()
    )
    fig2 = px.pie(
        paros_causa, names='causa_paro', values='tiempo_total_min',
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.45
    )
    fig2.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        height=320, margin=dict(l=0, r=0, t=10, b=10),
        legend=dict(font=dict(size=11))
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── FILA 2: Serie de tiempo ────────────────────────────────────
st.markdown('<div class="section-title">📅 Evolución Mensual de Eficiencia</div>', unsafe_allow_html=True)
eficiencia_mes = (
    df_f.groupby(df_f['fecha_produccion'].dt.to_period('M'))['eficiencia_pct']
        .mean().reset_index()
)
eficiencia_mes['fecha_produccion'] = eficiencia_mes['fecha_produccion'].astype(str)
fig3 = px.line(
    eficiencia_mes, x='fecha_produccion', y='eficiencia_pct', markers=True,
    labels={'fecha_produccion': 'Mes', 'eficiencia_pct': 'Eficiencia (%)'}
)
fig3.update_traces(line_color='#00e066', line_width=2.5, marker_size=6)
fig3.update_layout(
    template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)', height=280,
    margin=dict(l=0, r=0, t=10, b=40)
)
st.plotly_chart(fig3, use_container_width=True)

# ── FILA 3: Scatter + Heatmap ──────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="section-title">🔍 Tiempo de Paro vs Tasa de Defectos</div>', unsafe_allow_html=True)
    fig4 = px.scatter(
        df_f, x='tiempo_paro_min', y='tasa_defectos_pct',
        color='linea_produccion',
        hover_data=['producto', 'turno', 'maquina'],
        labels={
            'tiempo_paro_min': 'Tiempo de Paro (min)',
            'tasa_defectos_pct': 'Tasa de Defectos (%)'
        },
        opacity=0.7
    )
    fig4.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=340,
        margin=dict(l=0, r=0, t=10, b=40),
        legend=dict(title='', font=dict(size=10))
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    st.markdown('<div class="section-title">🌡️ Eficiencia por Línea y Turno</div>', unsafe_allow_html=True)
    if len(df_f) > 0:
        pivot = df_f.pivot_table(
            values='eficiencia_pct', index='linea_produccion',
            columns='turno', aggfunc='mean'
        ).round(1)
        fig5 = px.imshow(
            pivot, color_continuous_scale='RdYlGn', text_auto='.1f',
            labels={'color': 'Eficiencia (%)'}
        )
        fig5.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            height=340, margin=dict(l=0, r=0, t=10, b=40)
        )
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Sin datos para mostrar.")

# ── TABLA: Órdenes con baja eficiencia ────────────────────────
st.divider()
st.markdown('<div class="section-title">⚠️ Órdenes Críticas — Eficiencia &lt;70% y Defectos &gt;5%</div>', unsafe_allow_html=True)

baja_ef_df = (
    df_f[(df_f['eficiencia_pct'] < 70) & (df_f['tasa_defectos_pct'] > 5)]
    [['id_orden', 'linea_produccion', 'producto', 'turno', 'maquina',
      'eficiencia_pct', 'tasa_defectos_pct', 'causa_paro']]
    .sort_values('eficiencia_pct')
    .reset_index(drop=True)
)

if len(baja_ef_df) > 0:
    st.markdown(f'<div class="alerta-baja">⚠️ Se encontraron <strong>{len(baja_ef_df)}</strong> órdenes con baja eficiencia y alta tasa de defectos.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(
        baja_ef_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "eficiencia_pct": st.column_config.ProgressColumn(
                "Eficiencia (%)", min_value=0, max_value=100, format="%.1f%%"
            ),
            "tasa_defectos_pct": st.column_config.NumberColumn("Tasa Defectos (%)", format="%.2f%%")
        }
    )
else:
    st.success("✅ No hay órdenes críticas con los filtros actuales.")

st.divider()
st.caption("MetalParts Analytics · MetalParts Manufacturing · Desarrollado con Streamlit + Plotly")