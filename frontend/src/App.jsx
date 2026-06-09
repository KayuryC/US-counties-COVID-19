import React, { useEffect, useState } from 'react'
import Plot from 'react-plotly.js'

const BASE_URL = 'http://127.0.0.1:8000'
const API_URL = 'http://127.0.0.1:8000/predict'
const fallbackStateTotals = [
  { state: 'California', casos: 9351630, mortes: 90959 },
  { state: 'Texas', casos: 6792002, mortes: 88439 },
  { state: 'Florida', casos: 5997998, mortes: 74178 },
  { state: 'New York', casos: 5267378, mortes: 67938 },
  { state: 'Illinois', casos: 3215032, mortes: 35734 },
]
const fallbackClassBalance = [
  { classe: 'low', pct: 34.21 },
  { classe: 'medium', pct: 31.93 },
  { classe: 'high', pct: 33.86 },
]
const fallbackTrendCases = [8, 12, 18, 26, 38, 54, 72, 70, 64, 82, 98, 91, 76, 58, 48, 55, 68, 75, 63, 50]
const fallbackTrendDeaths = [2, 4, 5, 8, 11, 18, 24, 23, 21, 28, 31, 30, 27, 22, 18, 19, 22, 24, 20, 17]
const fallbackTrendDates = fallbackTrendCases.map((_, i) => `T-${fallbackTrendCases.length - i}`)
const riskClasses = ['low', 'medium', 'high']
const methodLabels = {
  bayes: 'Bayes',
  logistic_regression: 'Regressao Logistica',
  decision_tree: 'Arvore de Decisao',
}
const fallbackModelMetrics = {
  class_order: riskClasses,
  validation: {
    cutoff: '2021-11-26',
    train_sample: 360000,
    test_sample: 90000,
  },
  priors: {
    low: 0.3531,
    medium: 0.33,
    high: 0.317,
  },
  models: {
    bayes: {
      label: 'Bayes Manual',
      accuracy: 0.5925,
      precision_weighted: 0.6897,
      recall_weighted: 0.5925,
      f1_weighted: 0.5874,
      confusion_matrix: [[24889, 2144, 78], [14318, 10159, 999], [12557, 6579, 18277]],
    },
    logistic_regression: {
      label: 'Regressao Logistica',
      accuracy: 0.6037,
      precision_weighted: 0.6551,
      recall_weighted: 0.6037,
      f1_weighted: 0.5963,
      confusion_matrix: [[23110, 3790, 211], [12585, 8306, 4585], [12505, 1988, 22920]],
    },
    decision_tree: {
      label: 'Arvore de Decisao',
      accuracy: 0.6594,
      precision_weighted: 0.6713,
      recall_weighted: 0.6594,
      f1_weighted: 0.6586,
      confusion_matrix: [[21018, 5310, 783], [8785, 11770, 4921], [6196, 4663, 26554]],
    },
  },
}

const formatNumber = (n) => new Intl.NumberFormat('en-US').format(n)
const formatMetric = (n) => Number(n || 0).toFixed(4)

function toPolylinePoints(data, width, height, pad = 12) {
  const min = Math.min(...data)
  const max = Math.max(...data)
  const scaleX = (width - pad * 2) / (data.length - 1)
  const scaleY = (height - pad * 2) / (max - min || 1)
  return data
    .map((v, i) => {
      const x = pad + i * scaleX
      const y = height - pad - (v - min) * scaleY
      return `${x},${y}`
    })
    .join(' ')
}

export default function App() {
  const sections = [
    { id: 'secao-1', label: '1. Analise dos Dados' },
    { id: 'secao-2', label: '2. Classificacao Probabilistica' },
    { id: 'secao-3', label: '3. Comparacao de Metricas' },
    { id: 'secao-4', label: '4. Conclusoes e Limitacoes' },
    { id: 'secao-5', label: '5. Metodologia e Fontes' },
    { id: 'secao-6', label: '6. IA Generativa e Aprendizados' },
  ]
  const [activeSection, setActiveSection] = useState('secao-1')
  const [menuOpen, setMenuOpen] = useState(false)
  const [metric, setMetric] = useState('casos')
  const [windowKey, setWindowKey] = useState('180')
  const [topN, setTopN] = useState(5)
  const [form, setForm] = useState({ month: 6, day_of_week: 1, new_cases: 10, new_deaths: 0, cfr: 0.01 })
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [modelMetrics, setModelMetrics] = useState(fallbackModelMetrics)
  const [overview, setOverview] = useState({
    kpis: {
      period_start: '2020-01-21',
      period_end: '2022-05-13',
      rows: 2502832,
      states: 56,
      counties: 3277,
      missing_deaths: 57605,
      missing_deaths_locations: ['Puerto Rico'],
    },
    state_totals: fallbackStateTotals,
    window_state_totals: {
      '30': fallbackStateTotals,
      '90': fallbackStateTotals,
      '180': fallbackStateTotals,
      '365': fallbackStateTotals,
      total: fallbackStateTotals,
    },
    state_heatmap: [
      { state: 'California', code: 'CA', casos: 9351630, mortes: 90959 },
      { state: 'Texas', code: 'TX', casos: 6792002, mortes: 88439 },
      { state: 'Florida', code: 'FL', casos: 5997998, mortes: 74178 },
      { state: 'New York', code: 'NY', casos: 5267378, mortes: 67938 },
      { state: 'Illinois', code: 'IL', casos: 3215032, mortes: 35734 },
    ],
    state_rates: fallbackStateTotals.map((d) => ({ ...d, cfr: Number(((d.mortes / d.casos) * 100).toFixed(3)) })),
    top_counties: [],
    class_balance: fallbackClassBalance,
    daily_distributions: {
      new_cases: { x: [], counts: [] },
      new_deaths: { x: [], counts: [] },
    },
    distribution_summary: {
      new_cases: {},
      new_deaths: {},
    },
    monthly_trend: [],
    weekday_profile: [],
    peak_summary: {
      peak_cases_date: '-',
      peak_cases_ma7: 0,
      peak_deaths_date: '-',
      peak_deaths_ma7: 0,
      state_cases_deaths_corr: 0,
    },
    trend_dates: fallbackTrendDates,
    trend_cases_ma7: fallbackTrendCases,
    trend_deaths_ma7: fallbackTrendDeaths,
  })

  const parseValue = (field, value) => {
    const normalized = String(value).replace(',', '.')
    const n = Number(normalized)
    return Number.isFinite(n) ? n : 0
  }
  const onChange = (field, value) => setForm((s) => ({ ...s, [field]: parseValue(field, value) }))

  useEffect(() => {
    const loadOverview = async () => {
      try {
        const res = await fetch(`${BASE_URL}/analytics/overview`)
        if (!res.ok) return
        const data = await res.json()
        setOverview(data)
      } catch (_) {
        // fallback local ja definido no estado inicial
      }
    }
    loadOverview()
  }, [])

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const res = await fetch(`${BASE_URL}/model/metrics`)
        if (!res.ok) return
        const data = await res.json()
        if (data.models) setModelMetrics(data)
      } catch (_) {
        // fallback local ja definido no estado inicial
      }
    }
    loadMetrics()
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      if (!res.ok) throw new Error('Falha ao consultar a API')
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError('Nao foi possivel conectar ao backend. Verifique se o FastAPI esta rodando na porta 8000.')
    }
  }

  const stateSource = overview.window_state_totals?.[windowKey] || overview.state_totals
  const topStates = [...stateSource]
    .sort((a, b) => (metric === 'casos' ? b.casos - a.casos : b.mortes - a.mortes))
    .slice(0, topN)
  const topMax = topStates[0] ? (metric === 'casos' ? topStates[0].casos : topStates[0].mortes) : 1
  const windowSize = windowKey === '30' ? 30 : windowKey === '90' ? 90 : windowKey === '180' ? 180 : windowKey === '365' ? 365 : overview.trend_dates.length
  const trendCases = overview.trend_cases_ma7.slice(-windowSize)
  const trendDeaths = overview.trend_deaths_ma7.slice(-windowSize)
  const trendDates = overview.trend_dates.slice(-windowSize)
  const stateCodeByName = Object.fromEntries((overview.state_heatmap || []).map((d) => [d.state, d.code]))
  const heatmapRows = (overview.window_state_totals?.[windowKey] || overview.state_totals || [])
    .filter((d) => stateCodeByName[d.state])
    .map((d) => ({
      code: stateCodeByName[d.state],
      state: d.state,
      value: metric === 'casos' ? d.casos : d.mortes,
    }))
  const metricLabel = metric === 'casos' ? 'Casos' : 'Mortes'
  const topCounties = [...(overview.top_counties || [])]
    .sort((a, b) => (metric === 'casos' ? b.casos - a.casos : b.mortes - a.mortes))
    .slice(0, 10)
  const cfrRank = [...(overview.state_rates || [])].sort((a, b) => b.cfr - a.cfr).slice(0, 10)
  const getProbabilities = (key) => result?.[key]?.probabilities || { low: 0, medium: 0, high: 0 }
  const modelEntries = Object.entries(modelMetrics.models || {}).map(([key, values]) => ({ key, ...values }))
  const bestModel = modelEntries.reduce(
    (best, current) => (!best || current.accuracy > best.accuracy ? current : best),
    null,
  )
  const distributionKey = metric === 'casos' ? 'new_cases' : 'new_deaths'
  const distribution = overview.daily_distributions?.[distributionKey] || { x: [], counts: [] }
  const distributionSummary = overview.distribution_summary?.[distributionKey] || {}
  const basePlotLayout = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)',
    margin: { l: 56, r: 20, t: 18, b: 48 },
    font: { family: 'Avenir Next, Segoe UI, sans-serif', size: 11 },
  }

  return (
    <main className="container">
      <button className="menuBtn" onClick={() => setMenuOpen((v) => !v)}>
        ☰ Menu
      </button>
      {menuOpen && (
        <aside className="drawer">
          {sections.map((s) => (
            <button
              key={s.id}
              className={activeSection === s.id ? 'drawerItem active' : 'drawerItem'}
              onClick={() => { setActiveSection(s.id); setMenuOpen(false) }}
            >
              {s.label}
            </button>
          ))}
        </aside>
      )}

      <header className="hero">
        <p className="eyebrow">Projeto de Estatistica e Probabilidade</p>
        <h1>US Counties COVID-19 Dashboard</h1>
        <p className="subtitle">
          Painel estruturado na ordem exigida: analise dos dados, interpretacao visual e classificacao probabilistica
          com comparacao entre Bayes, Regressao Logistica e Arvore de Decisao.
        </p>
      </header>
      <section className="globalFilters card reveal">
        <h3>Filtros Globais da Analise</h3>
        <div className="controls">
          <label>Periodo
            <select value={windowKey} onChange={(e) => setWindowKey(e.target.value)}>
              <option value="30">Ultimos 30 dias</option>
              <option value="90">Ultimos 90 dias</option>
              <option value="180">Ultimos 180 dias</option>
              <option value="365">Ultimos 365 dias</option>
              <option value="total">Periodo total</option>
            </select>
          </label>
          <label>Metrica
            <select value={metric} onChange={(e) => setMetric(e.target.value)}>
              <option value="casos">Casos</option>
              <option value="mortes">Mortes</option>
            </select>
          </label>
          <label>Top N estados
            <select value={topN} onChange={(e) => setTopN(Number(e.target.value))}>
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={15}>Top 15</option>
            </select>
          </label>
        </div>
      </section>
      <section className="kpis">
        <article className="kpi reveal"><span>Periodo</span><strong>{overview.kpis.period_start} a {overview.kpis.period_end}</strong></article>
        <article className="kpi reveal"><span>Registros</span><strong>{formatNumber(overview.kpis.rows)}</strong></article>
        <article className="kpi reveal"><span>Condados Unicos</span><strong>{formatNumber(overview.kpis.counties)}</strong></article>
        <article className="kpi reveal"><span>Estados/Territorios</span><strong>{formatNumber(overview.kpis.states)}</strong></article>
      </section>
      <aside className="qualityNotice reveal">
        <strong>Nota de qualidade dos dados:</strong> {formatNumber(overview.kpis.missing_deaths || 0)} registros
        sem mortes reportadas, concentrados em {(overview.kpis.missing_deaths_locations || []).join(', ') || 'local nao informado'}.
        Esses valores permanecem ausentes no dataset tratado.
      </aside>

      {activeSection === 'secao-1' && <section className="sectionBlock reveal" id="secao-1">
        <div className="sectionTitle">
          <h2>Secao 1 - Analise dos Dados</h2>
          <p>Graficos com objetivo analitico explicito, conforme a rubrica de avaliacao.</p>
        </div>
        <div className="layout">
          <article className="card chartCard">
            <h3>Objetivo: comparar os estados com maior carga acumulada de casos</h3>
            <div className="hBars">
              {topStates.map((s, i) => (
                <div key={s.state} className="hBarRow" style={{ animationDelay: `${i * 70}ms` }}>
                  <div className="hBarMeta">
                    <strong>{s.state}</strong>
                    <span>{formatNumber(s.casos)} casos</span>
                  </div>
                  <div className="hBarTrack">
                    <span style={{ width: `${((metric === 'casos' ? s.casos : s.mortes) / topMax) * 100}%` }} />
                  </div>
                  <small>{formatNumber(s.mortes)} mortes</small>
                </div>
              ))}
            </div>
          </article>

          <article className="card chartCard">
            <h3>Objetivo: verificar equilibrio entre as classes da variavel alvo</h3>
            <div className="explainBox">
              <p><strong>O que esta sendo medido:</strong> proporcao de registros em cada classe da variavel alvo <code>risk_level</code>.</p>
              <p><strong>Como a classe foi criada:</strong> com base em <code>new_cases_ma7</code> (media movel de 7 dias de novos casos por condado).</p>
              <p><strong>Regras:</strong> <code>low</code> ate q33 (1.7143), <code>medium</code> entre q33 e q66 (10.1429), <code>high</code> acima de q66.</p>
            </div>
            <div className="classBars">
              {overview.class_balance.map((c) => (
                <div key={c.classe} className="classRow">
                  <div className="classLabel">
                    <span className={`dot ${c.classe}`} />
                    <strong>{c.classe}</strong>
                  </div>
                  <div className="classTrack">
                    <span className={`fill ${c.classe}`} style={{ width: `${c.pct}%` }} />
                  </div>
                  <small>{c.pct}%</small>
                </div>
              ))}
            </div>
            <p className="legend">Leitura rapida: as tres classes estao proximas de 33%, indicando base balanceada.</p>
          </article>

          <article className="card chartCard full">
            <h3>Objetivo: analisar a distribuicao e a assimetria das variacoes diarias</h3>
            <Plot
              data={[
                {
                  type: 'bar',
                  x: distribution.x,
                  y: distribution.counts,
                  marker: { color: metric === 'casos' ? '#0f766e' : '#0b4f6c' },
                  hovertemplate: 'log(1 + valor): %{x:.2f}<br>Registros: %{y:,}<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: `log(1 + novos ${metric})` },
                yaxis: { title: 'Frequencia', gridcolor: '#dbe7ef' },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '320px' }}
            />
            <p className="legend">
              Mediana: {distributionSummary['0.5'] ?? '-'} | P90: {distributionSummary['0.9'] ?? '-'} |
              P99: {distributionSummary['0.99'] ?? '-'} | P99,9: {distributionSummary['0.999'] ?? '-'}.
              A escala logaritmica preserva valores extremos sem deixar a maior parte dos registros invisivel.
            </p>
          </article>

          <article className="card chartCard full">
            <h3>Objetivo: observar tendencias temporais de crescimento e desaceleracao</h3>
            <div className="lineChart">
              <Plot
                data={[
                  {
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Novos casos MA7',
                    x: trendDates,
                    y: trendCases,
                    line: { color: '#0f766e', width: 4 },
                    yaxis: 'y',
                    hovertemplate: 'Data: %{x}<br>Casos MA7: %{y:.2f}<extra></extra>',
                  },
                  {
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Novas mortes MA7',
                    x: trendDates,
                    y: trendDeaths,
                    line: { color: '#0b4f6c', width: 4 },
                    yaxis: 'y2',
                    hovertemplate: 'Data: %{x}<br>Mortes MA7: %{y:.2f}<extra></extra>',
                  },
                ]}
                layout={{
                  margin: { l: 48, r: 56, t: 30, b: 48 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                  plot_bgcolor: 'rgba(0,0,0,0)',
                  hovermode: 'x unified',
                  xaxis: { showgrid: false, tickfont: { size: 10 } },
                  yaxis: {
                    title: { text: 'Casos MA7', font: { size: 11 } },
                    gridcolor: '#d2dbe6',
                    zeroline: false,
                    tickfont: { size: 10 },
                  },
                  yaxis2: {
                    title: { text: 'Mortes MA7', font: { size: 11 } },
                    overlaying: 'y',
                    side: 'right',
                    showgrid: false,
                    zeroline: false,
                    tickfont: { size: 10 },
                  },
                  legend: { orientation: 'h', y: 1.15, x: 0, font: { size: 11 } },
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '340px' }}
              />
            </div>
            <p className="legend">Periodo exibido: {trendDates[0]} ate {trendDates[trendDates.length - 1]}</p>
            <p className="legend">Linha principal: novos casos MA7 | Linha secundaria: novas mortes MA7</p>
          </article>

          <article className="card chartCard full">
            <h3>Objetivo: mapa de calor dos EUA por intensidade de COVID-19 por estado</h3>
            <div className="mapWrap">
              <Plot
                data={[
                  {
                    type: 'choropleth',
                    locationmode: 'USA-states',
                    locations: heatmapRows.map((d) => d.code),
                    z: heatmapRows.map((d) => d.value),
                    text: heatmapRows.map((d) => d.state),
                    colorscale: 'YlOrRd',
                    marker: { line: { color: '#fff', width: 0.6 } },
                    colorbar: { title: metric === 'casos' ? 'Casos' : 'Mortes' },
                  },
                ]}
                layout={{
                  geo: { scope: 'usa', bgcolor: 'rgba(0,0,0,0)' },
                  margin: { l: 0, r: 0, t: 0, b: 0 },
                  paper_bgcolor: 'rgba(0,0,0,0)',
                }}
                config={{ displayModeBar: false, responsive: true }}
                style={{ width: '100%', height: '420px' }}
              />
            </div>
          </article>

          <article className="card chartCard full">
            <h3>Objetivo: destacar picos, associacao entre variaveis e momentos criticos</h3>
            <div className="insightGrid">
              <div><span>Pico de casos MA7</span><strong>{formatNumber(Math.round(overview.peak_summary.peak_cases_ma7))}</strong><small>{overview.peak_summary.peak_cases_date}</small></div>
              <div><span>Pico de mortes MA7</span><strong>{formatNumber(Math.round(overview.peak_summary.peak_deaths_ma7))}</strong><small>{overview.peak_summary.peak_deaths_date}</small></div>
              <div><span>Correlacao casos x mortes</span><strong>{overview.peak_summary.state_cases_deaths_corr}</strong><small>por estado, data final</small></div>
            </div>
          </article>

          <article className="card chartCard">
            <h3>Objetivo: comparar relacao entre casos e mortes por estado</h3>
            <Plot
              data={[
                {
                  type: 'scatter',
                  mode: 'markers',
                  x: (overview.state_rates || []).map((d) => d.casos),
                  y: (overview.state_rates || []).map((d) => d.mortes),
                  text: (overview.state_rates || []).map((d) => `${d.state}<br>CFR: ${d.cfr}%`),
                  marker: {
                    color: (overview.state_rates || []).map((d) => d.cfr),
                    colorscale: 'Viridis',
                    size: 10,
                    opacity: 0.82,
                    colorbar: { title: 'CFR %' },
                  },
                  hovertemplate: '%{text}<br>Casos: %{x:,}<br>Mortes: %{y:,}<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: 'Casos acumulados', gridcolor: '#dbe7ef' },
                yaxis: { title: 'Mortes acumuladas', gridcolor: '#dbe7ef' },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '330px' }}
            />
          </article>

          <article className="card chartCard">
            <h3>Objetivo: identificar estados com maior taxa de letalidade acumulada</h3>
            <Plot
              data={[
                {
                  type: 'bar',
                  orientation: 'h',
                  y: cfrRank.map((d) => d.state).reverse(),
                  x: cfrRank.map((d) => d.cfr).reverse(),
                  marker: { color: '#0b4f6c' },
                  hovertemplate: '%{y}<br>CFR: %{x:.2f}%<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: 'CFR (%)', gridcolor: '#dbe7ef' },
                yaxis: { automargin: true },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '330px' }}
            />
          </article>

          <article className="card chartCard">
            <h3>Objetivo: comparar a evolucao mensal de {metricLabel.toLowerCase()}</h3>
            <Plot
              data={[
                {
                  type: 'bar',
                  x: (overview.monthly_trend || []).map((d) => d.month),
                  y: (overview.monthly_trend || []).map((d) => metric === 'casos' ? d.casos : d.mortes),
                  marker: { color: metric === 'casos' ? '#0f766e' : '#0b4f6c' },
                  hovertemplate: 'Mes: %{x}<br>' + metricLabel + ': %{y:,}<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: 'Mes', tickangle: -35 },
                yaxis: { title: metricLabel, gridcolor: '#dbe7ef' },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '330px' }}
            />
          </article>

          <article className="card chartCard">
            <h3>Objetivo: listar condados que mais concentram {metricLabel.toLowerCase()}</h3>
            <Plot
              data={[
                {
                  type: 'bar',
                  orientation: 'h',
                  y: topCounties.map((d) => `${d.county}, ${d.state}`).reverse(),
                  x: topCounties.map((d) => metric === 'casos' ? d.casos : d.mortes).reverse(),
                  marker: { color: '#0ea5e9' },
                  hovertemplate: '%{y}<br>' + metricLabel + ': %{x:,}<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: metricLabel, gridcolor: '#dbe7ef' },
                yaxis: { automargin: true },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '330px' }}
            />
          </article>

          <article className="card chartCard full">
            <h3>Objetivo: observar padrao medio por dia da semana</h3>
            <Plot
              data={[
                {
                  type: 'bar',
                  x: (overview.weekday_profile || []).map((d) => d.weekday),
                  y: (overview.weekday_profile || []).map((d) => metric === 'casos' ? d.casos : d.mortes),
                  marker: { color: metric === 'casos' ? '#0f766e' : '#0b4f6c' },
                  hovertemplate: 'Dia: %{x}<br>Media de ' + metricLabel + ': %{y:.2f}<extra></extra>',
                },
              ]}
              layout={{
                ...basePlotLayout,
                xaxis: { title: 'Dia da semana' },
                yaxis: { title: `Media diaria de ${metricLabel}`, gridcolor: '#dbe7ef' },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '300px' }}
            />
          </article>
        </div>
      </section>}

      {activeSection === 'secao-2' && <section className="sectionBlock reveal" id="secao-2">
        <div className="sectionTitle">
          <h2>Secao 2 - Classificacao Probabilistica</h2>
          <p>Entrada de atributos, probabilidade posterior por Bayes e comparacao entre os tres metodos.</p>
        </div>

        <div className="classificationShell">
          <article className="card modelBrief">
            <h3>O que esta sendo classificado?</h3>
            <p>O alvo e <code>risk_level</code>, uma categoria criada a partir da media movel de 7 dias de novos casos por condado (<code>new_cases_ma7</code>).</p>
            <div className="riskLegend">
              <span><i className="dot low" /> Low: baixa intensidade</span>
              <span><i className="dot medium" /> Medium: intensidade intermediaria</span>
              <span><i className="dot high" /> High: alta intensidade</span>
            </div>
          </article>

          <div className="classificationGrid">
            <div className="card prediction">
              <h3>Atributos informados pelo usuario</h3>
              <form onSubmit={onSubmit} className="predictForm">
                <label>Mes do registro <input type="number" min="1" max="12" value={form.month} onChange={(e) => onChange('month', e.target.value)} /></label>
                <label>Dia da semana (0 a 6) <input type="number" min="0" max="6" value={form.day_of_week} onChange={(e) => onChange('day_of_week', e.target.value)} /></label>
                <label>Novos casos <input type="number" min="0" value={form.new_cases} onChange={(e) => onChange('new_cases', e.target.value)} /></label>
                <label>Novas mortes <input type="number" min="0" value={form.new_deaths} onChange={(e) => onChange('new_deaths', e.target.value)} /></label>
                <label>Taxa CFR (0 a 1) <input type="number" min="0" max="1" step="0.001" value={form.cfr} onChange={(e) => onChange('cfr', e.target.value)} /></label>
                <button type="submit">Calcular classificacao</button>
              </form>
              {error && <p className="error">{error}</p>}
            </div>

            <div className="card resultPanel">
              <h3>Resultado comparativo</h3>
              <div className="methodGrid">
                {Object.entries(methodLabels).map(([key, label]) => (
                  <article key={key} className={`methodCard ${result?.[key]?.predicted_class || ''}`}>
                    <span>{label}</span>
                    <strong>{result?.[key]?.predicted_class || 'Aguardando'}</strong>
                  </article>
                ))}
              </div>

              <div className="posteriorPanel">
                <h4>Distribuicao de probabilidades por metodo</h4>
                <div className="probabilityGrid">
                  {Object.entries(methodLabels).map(([key, label]) => {
                    const probabilities = getProbabilities(key)
                    return (
                      <div className="methodProb" key={key}>
                        <strong>{label}</strong>
                        {riskClasses.map((klass) => {
                          const value = Number(probabilities[klass] || 0)
                          const width = value <= 1 ? value * 100 : value
                          return (
                            <div className="posteriorRow" key={klass}>
                              <span>{klass}</span>
                              <div className="posteriorTrack"><i className={klass} style={{ width: `${width}%` }} /></div>
                              <small>{width ? `${width.toFixed(1)}%` : '-'}</small>
                            </div>
                          )
                        })}
                      </div>
                    )
                  })}
                </div>
                {result && <p className="modelStatus">Artefatos reais carregados: {result.model_status === 'real_artifacts_loaded' ? 'sim' : 'nao'}.</p>}
              </div>
            </div>
          </div>

          <article className="card formulaCard">
            <h3>Como a classificacao probabilistica e calculada?</h3>
            <div className="formulaGrid">
              <div>
                <span>1</span><strong>Priori P(C)</strong>
                <small>
                  low {(modelMetrics.priors.low * 100).toFixed(2)}% |
                  medium {(modelMetrics.priors.medium * 100).toFixed(2)}% |
                  high {(modelMetrics.priors.high * 100).toFixed(2)}%
                </small>
              </div>
              <div><span>2</span><strong>Verossimilhanca P(X|C)</strong><small>probabilidade dos atributos observados em cada classe</small></div>
              <div><span>3</span><strong>Posteriori P(C|X)</strong><small>classe mais provavel apos observar os atributos</small></div>
            </div>
            <p className="legend">
              O endpoint utiliza os artefatos treinados de Bayes Manual, Regressao Logistica e Arvore de Decisao.
              As probabilidades da Arvore e da Regressao complementam a comparacao, mas a posteriori exigida e calculada explicitamente pelo Bayes.
            </p>
          </article>
        </div>
      </section>}

      {activeSection === 'secao-3' && <section className="sectionBlock reveal" id="secao-3">
        <div className="sectionTitle">
          <h2>Secao 3 - Comparacao de Metricas</h2>
          <p>Acuracia, precisao, recall, F1-score e matriz de confusao entre Bayes e classificadores.</p>
        </div>
        <div className="metricsLayout">
          <article className="card metricsSummary">
            <h3>Painel de Metricas da Validacao Temporal</h3>
            <table className="metricsTable">
              <thead>
                <tr><th>Metodo</th><th>Acuracia</th><th>Precisao</th><th>Recall</th><th>F1</th></tr>
              </thead>
              <tbody>
                {modelEntries.map((model) => (
                  <tr key={model.key}>
                    <td>{model.label}</td>
                    <td>{formatMetric(model.accuracy)}</td>
                    <td>{formatMetric(model.precision_weighted)}</td>
                    <td>{formatMetric(model.recall_weighted)}</td>
                    <td>{formatMetric(model.f1_weighted)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
          <article className="card">
            <h3>Leitura rapida</h3>
            <ul className="plainList">
              <li>Melhor acuracia: {bestModel?.label} ({formatMetric(bestModel?.accuracy)}).</li>
              <li>Treino usa datas anteriores a {modelMetrics.validation.cutoff}; teste usa datas a partir desse corte.</li>
              <li>A amostra de teste possui {formatNumber(modelMetrics.validation.test_sample)} registros futuros.</li>
              <li>Bayes fornece a decomposicao explicita em priori, verossimilhanca e posteriori.</li>
            </ul>
          </article>
        </div>
        <div className="matrixGrid">
          {modelEntries.map((model) => (
            <article className="card matrixCard" key={model.key}>
              <h3>Matriz de confusao: {model.label}</h3>
              <table className="matrixTable">
                <thead>
                  <tr><th>Real \ Predito</th>{riskClasses.map((klass) => <th key={klass}>{klass}</th>)}</tr>
                </thead>
                <tbody>
                  {riskClasses.map((klass, rowIndex) => (
                    <tr key={klass}>
                      <th>{klass}</th>
                      {riskClasses.map((predicted, columnIndex) => (
                        <td key={predicted}>{formatNumber(model.confusion_matrix[rowIndex][columnIndex])}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          ))}
        </div>
      </section>}

      {activeSection === 'secao-4' && <section className="sectionBlock reveal" id="secao-4">
        <div className="sectionTitle">
          <h2>Secao 4 - Conclusoes e Limitacoes</h2>
          <p>Sintese dos achados da EDA e do desempenho dos modelos.</p>
        </div>
        <article className="card">
          <ul className="plainList">
            <li>Conclusao principal: {bestModel?.label} obteve a melhor acuracia temporal, com {formatMetric(bestModel?.accuracy)}.</li>
            <li>Avaliacao temporal e mais realista e resultou em metricas inferiores as obtidas com divisao aleatoria.</li>
            <li>Limitacao: variavel alvo derivada pode reduzir generalizacao fora do contexto observado.</li>
            <li>Limitacao de dados: mortes por condado em Porto Rico nao foram reportadas pela fonte.</li>
            <li>Proximo refinamento: calibrar probabilidades e incluir variaveis populacionais por condado.</li>
          </ul>
        </article>
      </section>}

      {activeSection === 'secao-5' && <section className="sectionBlock reveal" id="secao-5">
        <div className="sectionTitle">
          <h2>Secao 5 - Metodologia e Fontes</h2>
          <p>Rastreabilidade do pipeline, origem dos dados e decisoes tecnicas.</p>
        </div>
        <article className="card">
          <ul className="plainList">
            <li>Fonte do dataset: The New York Times COVID-19 Data, arquivo <code>us-counties.csv</code>.</li>
            <li>Periodo analisado: 2020-01-21 a 2022-05-13, com 2.502.832 registros.</li>
            <li>Pipeline: preprocessamento, limpeza, EDA, feature engineering, modelagem.</li>
            <li>Validacao: divisao temporal com teste em datas futuras.</li>
            <li>Relatorio tecnico e declaracao de IA disponiveis na pasta <code>reports</code>.</li>
          </ul>
        </article>
      </section>}

      {activeSection === 'secao-6' && <section className="sectionBlock reveal" id="secao-6">
        <div className="sectionTitle">
          <h2>Secao 6 - IA Generativa e Aprendizados</h2>
          <p>Declaracao de uso de IA conforme orientacao da disciplina.</p>
        </div>
        <article className="card">
          <ul className="plainList">
            <li>O que foi feito: apoio na estruturacao, depuracao, testes, interface e documentacao.</li>
            <li>Objetivo de aprendizado: compreender Bayes, validacao temporal e integracao entre dados, API e dashboard.</li>
            <li>Dificuldades: grande volume de dados, ausencias, valores extremos e sincronizacao dos artefatos com o frontend.</li>
            <li>Verificacao: todas as sugestoes foram conferidas por execucao do pipeline, testes e revisao dos resultados.</li>
          </ul>
        </article>
      </section>}
    </main>
  )
}
