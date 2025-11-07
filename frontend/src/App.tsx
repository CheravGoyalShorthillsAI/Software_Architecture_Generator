import { useState } from 'react';
import {
  startProject,
  getProjectResults,
  pollProjectStatus,
  type ProjectResponse,
} from './services/api';
import { Spinner, ResultsDisplay, ProjectHistory } from './components';

function App() {
  // View state
  const [currentView, setCurrentView] = useState<'home' | 'history'>('home');
  
  // Application state
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<ProjectResponse | null>(null);
  
  // Additional state for enhanced UX
  const [error, setError] = useState<string | null>(null);

  /**
   * Handle Generate button click
   * Creates a new project and polls for completion
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setResults(null);

    // Real API integration
    try {
      console.log('Starting project with prompt:', prompt);
      const response = await startProject(prompt);
      
      console.log('Project started:', response);

      // Poll for completion
      await pollProjectStatus(
        response.project_id,
        (newStatus) => {
          console.log('Status update:', newStatus);
        },
        3000,
        100
      );

      // Fetch complete results
      await fetchProject(response.project_id);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to create project. Please ensure the backend is running.');
      }
      setIsLoading(false);
      console.error('Error:', err);
    }
  };

  const fetchProject = async (id: string) => {
    try {
      const data = await getProjectResults(id);
      setResults(data);
      setIsLoading(false);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to fetch project details');
      }
      setIsLoading(false);
      console.error(err);
    }
  };

  const handleViewHistory = () => {
    setCurrentView('history');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setResults(null);  // Clear results to show the input form
    setPrompt('');     // Clear the prompt
    setError(null);    // Clear any errors
  };

  const handleSelectHistoryProject = (project: ProjectResponse) => {
    setResults(project);
    setCurrentView('home');
  };

  // If in history view, render ProjectHistory component
  if (currentView === 'history') {
    return (
      <ProjectHistory
        onSelectProject={handleSelectHistoryProject}
        onBackToHome={handleBackToHome}
      />
    );
  }

  // Otherwise render home view
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-12 pt-8">
          <div className="flex justify-between items-center mb-4">
            {/* Left side - Back to History button (shown when viewing results) */}
            {results ? (
              <button
                onClick={handleViewHistory}
                className="text-white hover:text-purple-200 transition-colors flex items-center gap-2 bg-purple-800 bg-opacity-50 px-4 py-2 rounded-lg hover:bg-opacity-70"
              >
                <span className="text-xl">←</span>
                <span>📚</span>
                <span>Back to History</span>
              </button>
            ) : (
              <div></div>
            )}
            
            {/* Right side - View History button (shown when NOT viewing results) */}
            {!results && (
              <button
                onClick={handleViewHistory}
                className="text-white hover:text-purple-200 transition-colors flex items-center gap-2 bg-purple-800 bg-opacity-50 px-4 py-2 rounded-lg hover:bg-opacity-70"
              >
                <span>📚</span>
                <span>View History</span>
              </button>
            )}
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 drop-shadow-lg">
            🚀 The Genesis Engine
          </h1>
          <p className="text-xl md:text-2xl text-purple-100">
            AI-Powered Software Architecture Generator
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          <div className="bg-white rounded-2xl shadow-2xl p-8 md:p-12">
            {/* Main Input Form - Multi-Agent Prompts */}
            {!results && (
              <form onSubmit={handleSubmit} className="space-y-8">
                {/* Architect Agent Prompt (Required) */}
                <div>
                  <label className="block text-gray-800 text-xl font-bold mb-4">
                    <span className="flex items-center gap-3">
                      <span className="text-3xl">🏗️</span>
                      <span>Describe Your Project</span>
                      <span className="text-sm text-red-500 font-normal">*</span>
                    </span>
                  </label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Example: Build a scalable real-time video streaming platform with CDN integration, user authentication, payment processing, and real-time analytics..."
                    rows={5}
                    required
                    className="w-full px-6 py-4 border-2 border-gray-300 rounded-2xl focus:outline-none focus:ring-4 focus:ring-purple-200 focus:border-purple-500 resize-none text-gray-800 placeholder-gray-400 text-base shadow-sm transition-all duration-200"
                  />
                  <p className="text-sm text-gray-600 mt-3 flex items-start gap-2">
                    <span className="text-purple-600">💡</span>
                    <span>Our AI agents will analyze your requirements and generate a comprehensive microservices architecture with detailed analysis</span>
                  </p>
                </div>

                {/* Generate Button */}
                <button
                  type="submit"
                  disabled={isLoading || !prompt.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 hover:from-purple-700 hover:via-purple-800 hover:to-indigo-800 text-white font-bold py-5 px-8 rounded-2xl transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none shadow-xl text-lg"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center gap-3">
                      <Spinner size="small" color="border-white" />
                      <span>Generating Architecture...</span>
                    </span>
                  ) : (
                    <span className="flex items-center justify-center gap-3">
                      <span>✨</span>
                      <span>Generate Architecture</span>
                      <span>→</span>
                    </span>
                  )}
                </button>
              </form>
            )}

            {/* Agent Capabilities Section */}
            {!results && (
              <div className="mt-12 space-y-6">
                <div className="text-center">
                  <h3 className="text-3xl font-bold text-gray-900 mb-2">Agent Capabilities</h3>
                  <p className="text-gray-600">Powered by parallel AI agents working in isolated database forks</p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6 mt-8">
                  {/* Architect Agent */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-xl border-2 border-blue-200 hover:border-blue-400 hover:shadow-lg transition-all duration-300">
                    <div className="flex gap-4 items-start">
                      <div className="flex-shrink-0">
                        <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                          <span className="text-3xl">🏗️</span>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 mb-2 text-lg">Architect Agent</h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          Designs comprehensive microservices architecture with detailed technical specifications and infrastructure considerations
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Systems Analyst Agent */}
                  <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-xl border-2 border-green-200 hover:border-green-400 hover:shadow-lg transition-all duration-300">
                    <div className="flex gap-4 items-start">
                      <div className="flex-shrink-0">
                        <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-md">
                          <span className="text-3xl">🔧</span>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 mb-2 text-lg">Systems Analyst</h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          Analyzes technical risks including performance, security, scalability, and reliability concerns
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* BizOps Analyst Agent */}
                  <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-xl border-2 border-purple-200 hover:border-purple-400 hover:shadow-lg transition-all duration-300">
                    <div className="flex gap-4 items-start">
                      <div className="flex-shrink-0">
                        <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-md">
                          <span className="text-3xl">💼</span>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 mb-2 text-lg">BizOps Analyst</h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          Evaluates operational complexity, cost implications, team requirements, and deployment challenges
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Hybrid Search */}
                  <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-6 rounded-xl border-2 border-amber-200 hover:border-amber-400 hover:shadow-lg transition-all duration-300">
                    <div className="flex gap-4 items-start">
                      <div className="flex-shrink-0">
                        <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center shadow-md">
                          <span className="text-3xl">🔍</span>
                        </div>
                      </div>
                      <div>
                        <h4 className="font-bold text-gray-900 mb-2 text-lg">Hybrid Search</h4>
                        <p className="text-sm text-gray-700 leading-relaxed">
                          Combines keyword and AI-powered semantic search to find relevant insights across all analyses
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">❌</span>
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              </div>
            )}

            {/* If results are available, render ResultsDisplay component */}
            {!isLoading && results && (
              <>
                <ResultsDisplay results={results} />
                
                {/* Generate New Button */}
                <div className="mt-8 text-center">
                  <button
                    onClick={() => {
                      setResults(null);
                      setPrompt('');
                      setError(null);
                    }}
                    className="bg-white text-purple-600 border-2 border-purple-600 font-semibold py-3 px-8 rounded-xl hover:bg-purple-50 transition duration-200"
                  >
                    Generate New Architecture
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Footer - Technology Stack & Features */}
        {!results && (
          <div className="max-w-6xl mx-auto mt-16 mb-8">
            <div className="bg-gradient-to-br from-gray-50 to-purple-50 rounded-2xl shadow-xl p-10 border-2 border-purple-100">
              <div className="grid md:grid-cols-3 gap-10 text-sm">
                {/* Technology Stack */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">⚙️</span>
                    <h4 className="font-bold text-gray-900 text-lg">Technology Stack</h4>
                  </div>
                  <ul className="space-y-3 text-gray-700">
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Agentic Postgres (Tiger Cloud)</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Fast Database Forks (Zero-Copy)</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Hybrid Search (BM25 + pgvector)</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Google Gemini AI</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">FastAPI + React + TypeScript</span>
                    </li>
                  </ul>
                </div>

                {/* Features */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">✨</span>
                    <h4 className="font-bold text-gray-900 text-lg">Features</h4>
                  </div>
                  <ul className="space-y-3 text-gray-700">
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Multi-Agent Parallel Execution</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Semantic Search with Embeddings</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Database-per-Agent Isolation</span>
                    </li>
                    <li className="flex items-start gap-3 pl-2">
                      <span className="text-purple-600 font-bold mt-0.5">→</span>
                      <span className="leading-relaxed">Real-Time Analysis & Risk Detection</span>
                    </li>
                  </ul>
                </div>

                {/* Challenge */}
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-2xl">🏆</span>
                    <h4 className="font-bold text-gray-900 text-lg">Challenge</h4>
                  </div>
                  <p className="text-gray-700 leading-relaxed mb-3 pl-2">
                    Built for the <strong>Agentic Postgres Challenge</strong> by Tiger Data.
                  </p>
                  <p className="text-gray-700 leading-relaxed pl-2">
                    Showcasing innovative use of database forks, hybrid search, and multi-agent coordination for architecture generation.
                  </p>
                </div>
              </div>

              {/* Footer Bottom */}
              <div className="mt-8 pt-6 border-t-2 border-purple-200 text-center">
                <p className="text-sm text-gray-600 font-medium">
                  🚀 <strong className="text-purple-700">The Genesis Engine</strong> - Powered by Agentic Postgres & Tiger Data
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
