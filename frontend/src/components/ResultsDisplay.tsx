import { useState } from 'react';
import type { ProjectResponse, Analysis } from '../services/api';
import { searchProject } from '../services/api';
import ArchitectureCard from './ArchitectureCard';
import ArchitectureDiagram from './ArchitectureDiagram';
import SearchBar from './SearchBar';

interface ResultsDisplayProps {
  results: ProjectResponse;
}

/**
 * ResultsDisplay Component
 * 
 * Displays the microservices architecture analysis results.
 * Shows a single ArchitectureCard component with the generated
 * microservices design and its comprehensive analysis.
 * Includes semantic search functionality to find relevant analyses.
 * 
 * @param results - The complete project data including blueprint and analyses
 */
export default function ResultsDisplay({ results }: ResultsDisplayProps) {
  const [searchResults, setSearchResults] = useState<Analysis[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      // Clear search results
      setSearchResults(null);
      setSearchError(null);
      return;
    }

    setIsSearching(true);
    setSearchError(null);

    try {
      const searchData = await searchProject(results.project.id, query);
      
      // Filter results to only show analyses from the current blueprint
      const currentBlueprintId = results.blueprints && results.blueprints.length > 0 
        ? results.blueprints[0].id 
        : null;
      
      if (currentBlueprintId) {
        const filteredResults = searchData.filter(
          analysis => analysis.blueprint_id === currentBlueprintId
        );
        setSearchResults(filteredResults);
        console.log(`Search results: ${filteredResults.length} from current blueprint (${currentBlueprintId})`);
      } else {
        // No blueprint to filter by, show all results
        setSearchResults(searchData);
        console.log('Search results:', searchData);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchError(error instanceof Error ? error.message : 'Search failed');
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Results Header */}
      <div className="text-center">
        <h2 className="text-4xl font-bold text-gray-900 mb-3">
          🚀 Microservices Architecture Blueprint
        </h2>
        <p className="text-lg text-gray-600">
          AI-generated cloud-native microservices design for your project
        </p>
      </div>

      {/* Search Bar with Hybrid Search */}
      <div className="max-w-3xl mx-auto">
        <SearchBar
          placeholder="Search analyses by keyword or meaning (e.g., 'security concerns', 'scalability')..."
          onSearch={handleSearch}
        />
        {isSearching && (
          <div className="mt-2 text-sm text-purple-600 flex items-center gap-2">
            <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Searching...
          </div>
        )}
        {searchError && (
          <div className="mt-2 text-sm text-red-600">
            {searchError}
          </div>
        )}
        {searchResults && (
          <div className="mt-4 text-sm text-gray-600">
            Found {searchResults.length} relevant {searchResults.length === 1 ? 'analysis' : 'analyses'}
          </div>
        )}
      </div>

      {/* Original Prompt Card */}
      <div className="max-w-5xl mx-auto w-full">
        <OriginalPromptCard prompt={results.project.user_prompt} />
      </div>

      {/* Search Results (if any) */}
      {searchResults && searchResults.length > 0 && (
        <div className="max-w-5xl mx-auto bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">
            🔍 Search Results
          </h3>
          <div className="space-y-4">
            {searchResults.map((analysis) => (
              <div
                key={analysis.id}
                className="bg-white p-4 rounded-lg shadow-sm border border-gray-200"
              >
                <div className="flex items-start gap-3">
                  <span className="text-2xl">
                    {analysis.severity >= 8 ? '🔴' : analysis.severity >= 5 ? '🟡' : '🟢'}
                  </span>
                  <div className="flex-1">
                    <h4 className="font-bold text-gray-800 mb-1">
                      {analysis.category}
                    </h4>
                    <p className="text-gray-700 text-sm leading-relaxed">
                      {analysis.finding}
                    </p>
                    <div className="mt-2 text-xs text-gray-500">
                      Severity: {analysis.severity}/10
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={() => setSearchResults(null)}
            className="mt-4 text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            ← Back to full blueprint
          </button>
        </div>
      )}

      {/* Architecture Diagram */}
      {!searchResults && results.blueprints && results.blueprints.length > 0 && (
        <div className="max-w-7xl mx-auto mb-8">
          <ArchitectureDiagram blueprint={results.blueprints[0]} />
        </div>
      )}

      {/* Single Microservices Blueprint - Centered */}
      {!searchResults && results.blueprints && results.blueprints.length > 0 ? (
        <div className="max-w-5xl mx-auto">
          <ArchitectureCard blueprint={results.blueprints[0]} />
        </div>
      ) : !searchResults && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-xl">
            No blueprint available for this project.
          </p>
        </div>
      )}
    </div>
  );
}

function OriginalPromptCard({ prompt }: { prompt: string }) {
  const lines = prompt
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(Boolean);

  return (
    <div className="relative overflow-hidden rounded-3xl border border-purple-200 shadow-lg bg-gradient-to-br from-purple-50 via-white to-purple-100">
      <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_top_left,#a855f7,transparent_55%),radial-gradient(circle_at_bottom_right,#6366f1,transparent_55%)]" />
      <div className="relative p-6 md:p-8 flex flex-col gap-4">
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 rounded-3xl bg-white shadow-lg flex items-center justify-center text-3xl">
            📝
          </div>
          <div>
            <h3 className="text-xl md:text-2xl font-bold text-purple-900 leading-snug">Original Prompt</h3>
            <p className="text-sm md:text-base text-purple-500">The exact request that generated this architecture</p>
          </div>
        </div>
        <div className="bg-white/70 rounded-2xl p-5 md:p-6 border border-purple-100 shadow-inner">
          <p className="text-base md:text-lg text-gray-800 leading-relaxed font-medium whitespace-pre-wrap break-words">
            {prompt}
          </p>
        </div>
      </div>
    </div>
  );
}

