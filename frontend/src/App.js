import React, { useState } from 'react';
import './App.css';

function App() {
  const [prompt, setPrompt] = useState('');
  const [projectId, setProjectId] = useState(null);
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [project, setProject] = useState(null);
  const [error, setError] = useState(null);

  const API_BASE_URL = 'http://localhost:8000';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setProjectId(null);
    setProject(null);

    try {
      const response = await fetch(`${API_BASE_URL}/projects`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_prompt: prompt }),
      });

      if (!response.ok) {
        throw new Error('Failed to create project');
      }

      const data = await response.json();
      setProjectId(data.project_id);
      setStatus(data.status);
      
      // Start polling for project status
      pollProjectStatus(data.project_id);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const pollProjectStatus = async (id) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/projects/${id}/status`);
        const data = await response.json();
        setStatus(data.status);

        if (data.status === 'completed') {
          clearInterval(pollInterval);
          fetchProject(id);
        } else if (data.status === 'error') {
          clearInterval(pollInterval);
          setError('Project analysis failed');
          setLoading(false);
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 3000); // Poll every 3 seconds
  };

  const fetchProject = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/projects/${id}`);
      const data = await response.json();
      setProject(data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch project details');
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🚀 The Genesis Engine</h1>
          <p className="subtitle">AI-Powered Software Architecture Generator</p>
        </header>

        <div className="content">
          <form onSubmit={handleSubmit} className="prompt-form">
            <textarea
              className="prompt-input"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your software project... (e.g., 'Build a real-time chat application with user authentication and message history')"
              rows="6"
              required
            />
            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading || !prompt.trim()}
            >
              {loading ? 'Generating Architecture...' : 'Generate Architecture'}
            </button>
          </form>

          {error && (
            <div className="error-message">
              <p>❌ {error}</p>
            </div>
          )}

          {projectId && (
            <div className="status-card">
              <h3>Project ID: {projectId}</h3>
              <p className="status">
                Status: <span className={`status-badge ${status}`}>{status}</span>
              </p>
              {loading && (
                <div className="loader">
                  <div className="spinner"></div>
                  <p>Analyzing architecture blueprints...</p>
                </div>
              )}
            </div>
          )}

          {project && project.blueprints && project.blueprints.length > 0 && (
            <div className="results">
              <h2>Architecture Blueprints</h2>
              {project.blueprints.map((blueprint, index) => (
                <div key={index} className="blueprint-card">
                  <h3>{blueprint.name}</h3>
                  <p className="description">{blueprint.description}</p>
                  
                  <div className="pros-cons">
                    <div className="pros">
                      <h4>✅ Pros</h4>
                      <ul>
                        {blueprint.pros?.map((pro, i) => (
                          <li key={i}>{pro}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="cons">
                      <h4>⚠️ Cons</h4>
                      <ul>
                        {blueprint.cons?.map((con, i) => (
                          <li key={i}>{con}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {blueprint.analyses && blueprint.analyses.length > 0 && (
                    <div className="analyses">
                      <h4>📊 Analysis Results</h4>
                      {blueprint.analyses.map((analysis, i) => (
                        <div key={i} className={`analysis-item ${analysis.severity}`}>
                          <span className="category">{analysis.category}</span>
                          <p>{analysis.finding}</p>
                          <span className="severity">{analysis.severity}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

