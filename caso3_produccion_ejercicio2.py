import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

# ── Estilo matplotlib oscuro ───────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  '#0a1a0a',
    'axes.facecolor':    '#0a1a0a',
    'axes.edgecolor':    '#1e3a1e',
    'axes.labelcolor':   '#7a9980',
    'xtick.color':       '#7a9980',
    'ytick.color':       '#7a9980',
    'text.color':        '#e0f5e0',
    'grid.color':        '#1e3a1e',
    'grid.linestyle':    '--',
    'grid.alpha':        0.5,
})

# ── Carga de datos ─────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    df = pd.read_csv('caso3_produccion_dataset.csv')
    df['fecha_produccion'] = pd.to_datetime(df['fecha_produccion'])
    return df

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("⚠️ No se encontró 'caso3_produccion_dataset.csv'.")
    st.stop()

# ── SIDEBAR ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏭 MetalParts")
    st.markdown("**Analytics Dashboard**")
    st.divider()
    st.markdown("### 🔍 Filtros")

    lineas = st.multiselect("Línea de producción", options=sorted(df['linea_produccion'].unique()), default=sorted(df['linea_produccion'].unique()))
    turnos = st.multiselect("Turno", options=sorted(df['turno'].unique()), default=sorted(df['turno'].unique()))
    maquinas = st.multiselect("Máquina", options=sorted(df['maquina'].unique()), default=sorted(df['maquina'].unique()))

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
    (c1, "📦", f"{total_unidades:,}",         "Unidades Producidas"),
    (c2, "⚙️", f"{eficiencia_promedio:.1f}%", "Eficiencia Promedio"),
    (c3, "❌", f"{total_defectuosas:,}",       "Unidades Defectuosas"),
    (c4, "💰", f"${costo_total/1e6:.1f}M",     "Costo Producción COP"),
    (c5, "⚠️", str(baja_ef_count),            "Órdenes Críticas"),
]:
    with col:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Colores por línea ──────────────────────────────────────────
GREEN_SCALE   = ['#00e066', '#00b34d', '#008037', '#005522']
lineas_unicas = sorted(df_f['linea_produccion'].unique()) if len(df_f) else []
color_linea   = {l: GREEN_SCALE[i % len(GREEN_SCALE)] for i, l in enumerate(lineas_unicas)}

# ── FILA 1: Barras eficiencia + Pie causas paro ────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.markdown('<div class="section-title">⚙️ Eficiencia Promedio por Línea</div>', unsafe_allow_html=True)
    ef_linea = (
        df_f.groupby('linea_produccion')['eficiencia_pct']
            .mean().round(1).reset_index()
            .sort_values('eficiencia_pct')
    )
    fig, ax = plt.subplots(figsize=(7, 3.2))
    colores = ['#e05050' if v < 70 else '#f0c040' if v < 85 else '#00e066' for v in ef_linea['eficiencia_pct']]
    bars = ax.barh(ef_linea['linea_produccion'], ef_linea['eficiencia_pct'], color=colores, height=0.5)
    ax.bar_label(bars, fmt='%.1f%%', padding=4, color='#e0f5e0', fontsize=9)
    ax.set_xlabel('Eficiencia (%)', fontsize=8)
    ax.set_xlim(0, 115)
    ax.grid(axis='x')
    ax.spines[['top', 'right', 'left']].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_b:
    st.markdown('<div class="section-title">⏱️ Causas de Paro</div>', unsafe_allow_html=True)
    paros = df_f.groupby('causa_paro')['tiempo_paro_min'].sum()
    fig, ax = plt.subplots(figsize=(4, 3.2))
    wedge_colors = ['#00e066', '#f0c040', '#e05050', '#4488ff']
    wedges, texts, autotexts = ax.pie(
        paros.values, labels=paros.index, autopct='%1.1f%%',
        colors=wedge_colors[:len(paros)], wedgeprops=dict(width=0.6),
        startangle=90, textprops={'fontsize': 8, 'color': '#e0f5e0'}
    )
    for at in autotexts:
        at.set_color('#0a1a0a')
        at.set_fontsize(7)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

# ── FILA 2: Serie de tiempo ────────────────────────────────────
st.markdown('<div class="section-title">📅 Evolución Mensual de Eficiencia</div>', unsafe_allow_html=True)
ef_mes = (
    df_f.groupby(df_f['fecha_produccion'].dt.to_period('M'))['eficiencia_pct']
        .mean().reset_index()
)
ef_mes['fecha_produccion'] = ef_mes['fecha_produccion'].astype(str)
fig, ax = plt.subplots(figsize=(12, 2.8))
ax.plot(ef_mes['fecha_produccion'], ef_mes['eficiencia_pct'],
        color='#00e066', linewidth=2.5, marker='o', markersize=5)
ax.fill_between(ef_mes['fecha_produccion'], ef_mes['eficiencia_pct'], alpha=0.15, color='#00e066')
ax.axhline(y=70, color='#e05050', linestyle='--', linewidth=1, alpha=0.7, label='Meta mín. 70%')
ax.set_xlabel('Mes', fontsize=8)
ax.set_ylabel('Eficiencia (%)', fontsize=8)
ax.legend(fontsize=8, framealpha=0.2)
ax.grid(axis='y')
ax.spines[['top', 'right']].set_visible(False)
plt.xticks(rotation=45, ha='right', fontsize=7)
fig.tight_layout()
st.pyplot(fig)
plt.close()

# ── FILA 3: Scatter + Heatmap ──────────────────────────────────
col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<div class="section-title">🔍 Tiempo de Paro vs Tasa de Defectos</div>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    for linea in lineas_unicas:
        sub = df_f[df_f['linea_produccion'] == linea]
        ax.scatter(sub['tiempo_paro_min'], sub['tasa_defectos_pct'],
                   label=linea, color=color_linea[linea], alpha=0.6, s=20)
    ax.set_xlabel('Tiempo de Paro (min)', fontsize=8)
    ax.set_ylabel('Tasa de Defectos (%)', fontsize=8)
    ax.legend(fontsize=7, framealpha=0.2)
    ax.grid(True)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close()

with col_d:
    st.markdown('<div class="section-title">🌡️ Eficiencia por Línea y Turno</div>', unsafe_allow_html=True)
    if len(df_f) > 0:
        pivot = df_f.pivot_table(
            values='eficiencia_pct', index='linea_produccion',
            columns='turno', aggfunc='mean'
        ).round(1)
        fig, ax = plt.subplots(figsize=(5.5, 3.5))
        im = ax.imshow(pivot.values, cmap='RdYlGn', aspect='auto', vmin=50, vmax=100)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, fontsize=8)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8)
        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                val = pivot.values[i, j]
                ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                        fontsize=8, color='#0a1a0a')
        plt.colorbar(im, ax=ax, shrink=0.8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        st.info("Sin datos para mostrar.")

# ── TABLA: Órdenes críticas ────────────────────────────────────
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
        baja_ef_df, use_container_width=True, hide_index=True,
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
st.caption("MetalParts Analytics · MetalParts Manufacturing · Desarrollado con Streamlit + Matplotlib")