import { useState } from 'react'
import { ExplanationBody } from './ExplanationBody'
import { speakExplanation, stopSpeaking } from './speech'

const API_URL = 'http://127.0.0.1:8000/api/explain/'

const PERSONAS = [
  { value: 'intern', label: 'Intern', hint: 'Plain language, no jargon' },
  { value: 'professor', label: 'Professor', hint: 'Clear, calm, precise' },
  { value: 'journalist', label: 'Journalist', hint: 'Headline, facts, why it matters' },
  { value: 'executive', label: 'Executive', hint: 'Short, sharp, decision-ready' },
]

function App() {
  const [topic, setTopic] = useState('')
  const [persona, setPersona] = useState('professor')
  const [explanation, setExplanation] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setExplanation('')
    stopSpeaking()

    const trimmedTopic = topic.trim()
    if (!trimmedTopic) {
      setError('Please enter a topic first.')
      return
    }

    setIsLoading(true)
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: trimmedTopic, persona }),
      })
      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.error || 'The server could not explain this topic.')
      }
      setExplanation(data.explanation)
      speakExplanation(data.explanation, persona)
    } catch (err) {
      setError(err.message || 'Could not reach the server.')
    } finally {
      setIsLoading(false)
    }
  }

  const selectedPersona = PERSONAS.find((item) => item.value === persona)

  return (
    <div className="page">
      <div className="glow" aria-hidden="true" />

      <header className="hero">
        <p className="eyebrow">Explain studio</p>
        <h1>
          Explain like I&apos;m a<span className="ellipsis">…</span>
        </h1>
        <p className="lede">
          Choose a voice and get a short English explanation you can read and
          hear.
        </p>
      </header>

      <div className="layout">
        <form className="panel" onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="topic">What should we unpack?</label>
            <input
              id="topic"
              type="text"
              value={topic}
              onChange={(event) => setTopic(event.target.value)}
              placeholder="Black holes, photosynthesis, inflation…"
              autoComplete="off"
            />
          </div>

          <fieldset className="field">
            <legend>Explain like I&apos;m a…</legend>
            <div className="persona-grid">
              {PERSONAS.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  className={
                    persona === item.value ? 'persona active' : 'persona'
                  }
                  onClick={() => setPersona(item.value)}
                  aria-pressed={persona === item.value}
                >
                  <strong>{item.label}</strong>
                  <span>{item.hint}</span>
                </button>
              ))}
            </div>
          </fieldset>

          <button className="primary" type="submit" disabled={isLoading}>
            {isLoading ? 'Composing…' : 'Explain this'}
          </button>
          {error ? <p className="error">{error}</p> : null}
        </form>

        <section className="panel canvas" aria-live="polite">
          {!explanation && !isLoading ? (
            <div className="empty">
              <p className="empty-kicker">Waiting</p>
              <p>Your explanation will appear here as clean, readable English.</p>
            </div>
          ) : null}

          {isLoading ? (
            <div className="empty">
              <p className="empty-kicker pulse">Listening to Gemini</p>
              <p>Writing in the {selectedPersona?.label.toLowerCase()} voice…</p>
            </div>
          ) : null}

          {explanation ? (
            <>
              <div className="canvas-meta">
                <span>{selectedPersona?.label}</span>
                <span aria-hidden="true">·</span>
                <span>English</span>
              </div>
              <h2>Explanation</h2>
              <ExplanationBody text={explanation} />
              <div className="actions">
                <button
                  type="button"
                  className="ghost"
                  onClick={() => speakExplanation(explanation, persona)}
                >
                  Play voice
                </button>
                <button type="button" className="ghost" onClick={stopSpeaking}>
                  Stop
                </button>
              </div>
            </>
          ) : null}
        </section>
      </div>
    </div>
  )
}

export default App
