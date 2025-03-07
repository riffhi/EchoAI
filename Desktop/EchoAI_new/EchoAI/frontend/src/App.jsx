import { useState } from 'react'
import './App.css'
import LiveKitModal from './components/LiveKitModal';

function App() {
  const [showSupport, setShowSupport] = useState(false);

  const handleSupportClick = () => {
    setShowSupport(true)
  }

  return (
    <div className="app">
      <header className="header">
        <div className="logo">SmartAgent AI</div>
        <nav>
          <a href="#">Home</a>
          <a href="#">Features</a>
          <a href="#">Help</a>
        </nav>
      </header>

      <main>
        <section className="hero">
          <h1>AI Assistant for Your Smartphone</h1>
          <p>Control your device with natural language commands</p>
          <div className="search-bar">
            <input type="text" placeholder='What would you like to do today?'></input>
            <button>Ask</button>
          </div>
        </section>

        <section className="features">
          <h2>What Our AI Agent Can Do</h2>
          <div className="categories">
            <div className="category-card">
              <div className="icon-placeholder app-switch"></div>
              <h3>App Switching</h3>
              <p>Navigate between apps and control them with voice commands</p>
            </div>
            <div className="category-card">
              <div className="icon-placeholder metrics"></div>
              <h3>Metrics Analysis</h3>
              <p>Run analysis on your device usage, battery life, and performance</p>
            </div>
            <div className="category-card">
              <div className="icon-placeholder transactions"></div>
              <h3>Transactions</h3>
              <p>Securely initiate and complete transactions with your approval</p>
            </div>
            <div className="category-card">
              <div className="icon-placeholder calendar"></div>
              <h3>Calendar Management</h3>
              <p>Schedule, view, and modify your appointments hands-free</p>
            </div>
          </div>
        </section>

        <button className="support-button" onClick={handleSupportClick}>
          Activate AI Agent
        </button>
      </main>

      {showSupport && <LiveKitModal setShowSupport={setShowSupport}/>}
    </div>
  )
}

export default App