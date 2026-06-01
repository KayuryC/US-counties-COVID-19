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

const formatNumber = (n) => new Intl.NumberFormat('en-US').format(n)

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
  const [overview, setOverview] = useState({
    kpis: {
      period_start: '2020-01-21',
      period_end: '2022-05-13',
      rows: 2502832,
      states: 56,
      counties: 3277,
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
    class_balance: fallbackClassBalance,
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

      {activeSection === 'secao-1' && <section className="sectionBlock reveal" id="secao-1">
        <div className="sectionTitle">
          <h2>Secao 1 - Analise dos Dados</h2>
          <p>Graficos com objetivo analitico explicito, conforme a rubricade avaliacao.</p>
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
        </div>
      </section>}

      {activeSection === 'secao-2' && <section className="sectionBlock reveal" id="secao-2">
        <div className="sectionTitle">
          <h2>Secao 2 - Classificacao Probabilistica</h2>
          <p>Entrada de atributos, probabilidade bayesiana e comparacao visual entre os tres metodos.</p>
        </div>
        <div className="layout">
          <div className="card prediction">
            <h3>Entrada de Atributos</h3>
            <form onSubmit={onSubmit} className="formGrid">
              <label>Month <input type="number" min="1" max="12" value={form.month} onChange={(e) => onChange('month', e.target.value)} /></label>
              <label>Day of week <input type="number" min="0" max="6" value={form.day_of_week} onChange={(e) => onChange('day_of_week', e.target.value)} /></label>
              <label>New cases <input type="number" value={form.new_cases} onChange={(e) => onChange('new_cases', e.target.value)} /></label>
              <label>New deaths <input type="number" value={form.new_deaths} onChange={(e) => onChange('new_deaths', e.target.value)} /></label>
              <label>CFR (aceita 0.01 ou 0,01) <input type="text" value={String(form.cfr).replace('.', ',')} onChange={(e) => onChange('cfr', e.target.value)} /></label>
              <button type="submit">Calcular Predicao</button>
            </form>
            {error && <p className="error">{error}</p>}
          </div>

          <div className="card">
            <h3>Comparacao de Resultados</h3>
            <div className="results">
              <article><span>Bayes</span><strong>{result?.bayes?.predicted_class || '-'}</strong></article>
              <article><span>Regressao Logistica</span><strong>{result?.logistic_regression?.predicted_class || '-'}</strong></article>
              <article><span>Arvore de Decisao</span><strong>{result?.decision_tree?.predicted_class || '-'}</strong></article>
            </div>
            <div className="probBox">
              <p>Probabilidades Bayes (posteriori):</p>
              <pre>{JSON.stringify(result?.bayes?.probabilities || { low: '-', medium: '-', high: '-' }, null, 2)}</pre>
            </div>
          </div>
        </div>
      </section>}

      {activeSection === 'secao-3' && <section className="sectionBlock reveal" id="secao-3">
        <div className="sectionTitle">
          <h2>Secao 3 - Comparacao de Metricas</h2>
          <p>Acuracia, precisao, recall, F1-score e matriz de confusao entre Bayes e classificadores.</p>
        </div>
        <div className="layout">
          <article className="card">
            <h3>Painel de Metricas (base atual)</h3>
            <table className="metricsTable">
              <thead><tr><th>Metodo</th><th>Acuracia</th><th>F1 (weighted)</th></tr></thead>
              <tbody>
                <tr><td>Bayes Manual</td><td>0.6425</td><td>0.6328</td></tr>
                <tr><td>Regressao Logistica</td><td>0.6317</td><td>0.6341</td></tr>
                <tr><td>Arvore de Decisao</td><td>0.7304</td><td>0.7278</td></tr>
              </tbody>
            </table>
          </article>
          <article className="card">
            <h3>Leitura rapida</h3>
            <ul className="plainList">
              <li>Melhor acuracia: Arvore de Decisao.</li>
              <li>Bayes entrega interpretabilidade probabilistica.</li>
              <li>A comparacao visual sera expandida com matriz de confusao.</li>
            </ul>
          </article>
        </div>
      </section>}

      {activeSection === 'secao-4' && <section className="sectionBlock reveal" id="secao-4">
        <div className="sectionTitle">
          <h2>Secao 4 - Conclusoes e Limitacoes</h2>
          <p>Sintese dos achados da EDA e do desempenho dos modelos.</p>
        </div>
        <article className="card">
          <ul className="plainList">
            <li>Conclusao principal: modelos conseguem discriminar niveis de risco com desempenho moderado a bom.</li>
            <li>Limitacao: variavel alvo derivada pode reduzir generalizacao fora do contexto observado.</li>
            <li>Proximo refinamento: incluir validacao temporal e calibracao das probabilidades.</li>
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
            <li>Fonte do dataset: NYT US Counties COVID-19.</li>
            <li>Pipeline: preprocessamento, limpeza, EDA, feature engineering, modelagem.</li>
            <li>Repositorio GitHub com commits por etapa.</li>
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
            <li>Uso de IA para apoio em estruturacao de codigo e interface.</li>
            <li>Objetivo: acelerar prototipacao sem substituir entendimento conceitual.</li>
            <li>Dificuldades: desenho de pipeline, visualizacao e integracao backend/frontend.</li>
          </ul>
        </article>
      </section>}
    </main>
  )
}
