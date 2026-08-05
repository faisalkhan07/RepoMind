import { useState, useEffect } from 'react'
import './App.css'

const API_URL = 'https://repomind-production-1bd3.up.railway.app'

function App() {
  const [repoUrl, setRepoUrl] = useState('')
  const [question, setQuestion] = useState('')
  const [collectionName, setCollectionName] = useState('')
  const [ingestStatus, setIngestStatus] = useState('')
  const [isIngesting, setIsIngesting] = useState(false)
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [isAsking, setIsAsking] = useState(false)

  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', isDarkMode ? 'dark' : 'light')
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light')
  }, [isDarkMode])

  async function handleIngest() {
    if (!repoUrl) return

    setIsIngesting(true)
    setIngestStatus('Indexing repo... this may take a moment')

    try {
      const response = await fetch(`${API_URL}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl })
      })

      const data = await response.json()

      setCollectionName(data.collection_name)
      setIngestStatus(`Indexed ${data.repo_name} — ${data.chunks_stored} code chunks stored`)
    } catch (error) {
      setIngestStatus('Failed to index repo. Check the URL and try again.')
    } finally {
      setIsIngesting(false)
    }
  }

  async function handleAsk() {
    if (!question || !collectionName) return

    setIsAsking(true)
    setAnswer('')
    setSources([])

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          collection_name: collectionName,
          n_results: 3
        })
      })

      const data = await response.json()

      setAnswer(data.answer)
      setSources(data.sources)
    } catch (error) {
      setAnswer('Something went wrong. Please try again.')
    } finally {
      setIsAsking(false)
    }
  }

  return (
    <div className="app">
      <button
        className="theme-toggle"
        onClick={() => setIsDarkMode(!isDarkMode)}
        aria-label="Toggle dark mode"
      >
        {isDarkMode ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        )}
      </button>

      <header className="header">
        <h1>RepoMind</h1>
        <p>Ask questions about any GitHub codebase</p>
      </header>

      <section className="ingest-section">
        <input
          type="text"
          placeholder="Paste a GitHub repo URL..."
          value={repoUrl}
          onChange={(e) => setRepoUrl(e.target.value)}
        />
        <button onClick={handleIngest} disabled={isIngesting}>
          {isIngesting ? 'Indexing...' : 'Index repo'}
        </button>
      </section>

      {ingestStatus && <p className="status">{ingestStatus}</p>}

      <section className="chat-section">
        <input
          type="text"
          placeholder="Ask a question about the code..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={!collectionName}
        />
        <button onClick={handleAsk} disabled={isAsking || !collectionName}>
          {isAsking ? 'Thinking...' : 'Ask'}
        </button>
      </section>

      {answer && (
        <div className="answer-box">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}

      {sources.length > 0 && (
        <div className="sources-box">
          <h3>Sources</h3>
          {sources.map((source, i) => (
            <div key={i} className="source-card">
              <span className="source-number">[{i + 1}]</span>
              <span className="source-name">{source.name}</span>
              <span className="source-location">{source.file}:{source.line}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default App