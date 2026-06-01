import { useState } from 'react'

const API_URL = 'http://127.0.0.1:8000/predict'

export default function App() {
  const [form, setForm] = useState({ month: 6, day_of_week: 1, new_cases: 10, new_deaths: 0, cfr: 0.01 })
  const [result, setResult] = useState(null)

  const onChange = (field, value) => setForm((s) => ({ ...s, [field]: Number(value) }))

  const onSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const data = await res.json()
    setResult(data)
  }

  return (
    <main className="container">
      <h1>Classificacao Probabilistica COVID-19</h1>
      <form onSubmit={onSubmit} className="card">
        <label>Month <input type="number" min="1" max="12" value={form.month} onChange={(e) => onChange('month', e.target.value)} /></label>
        <label>Day of week <input type="number" min="0" max="6" value={form.day_of_week} onChange={(e) => onChange('day_of_week', e.target.value)} /></label>
        <label>New cases <input type="number" value={form.new_cases} onChange={(e) => onChange('new_cases', e.target.value)} /></label>
        <label>New deaths <input type="number" value={form.new_deaths} onChange={(e) => onChange('new_deaths', e.target.value)} /></label>
        <label>CFR <input type="number" step="0.0001" value={form.cfr} onChange={(e) => onChange('cfr', e.target.value)} /></label>
        <button type="submit">Prever</button>
      </form>

      {result && (
        <section className="card">
          <h2>Resultados</h2>
          <p>Bayes: <strong>{result.bayes.predicted_class}</strong></p>
          <p>Logistic Regression: <strong>{result.logistic_regression.predicted_class}</strong></p>
          <p>Decision Tree: <strong>{result.decision_tree.predicted_class}</strong></p>
          <pre>{JSON.stringify(result.bayes.probabilities, null, 2)}</pre>
        </section>
      )}
    </main>
  )
}
