import type { Blueprint } from '../services/api';

interface ArchitectureCardProps {
  blueprint: Blueprint;
}

/**
 * ArchitectureCard Component
 * 
 * Displays a single architecture blueprint with its details including:
 * - Name and description
 * - Pros and cons
 * - Analysis results with severity indicators
 * 
 * @param blueprint - The blueprint object to display
 */
export default function ArchitectureCard({ blueprint }: ArchitectureCardProps) {
  /**
   * Get Tailwind CSS classes for analysis severity background color
   * Severity is on a 1-10 scale: 1-3 = low, 4-6 = medium, 7-10 = high
   */
  const getSeverityColor = (severity: number | string): string => {
    const severityNum = typeof severity === 'number' ? severity : 5;
    if (severityNum >= 7) {
      return 'bg-red-100 border-red-500 text-red-900';
    } else if (severityNum >= 4) {
      return 'bg-orange-100 border-orange-500 text-orange-900';
    } else {
      return 'bg-green-100 border-green-500 text-green-900';
    }
  };

  /**
   * Get Tailwind CSS classes for severity badge
   */
  const getSeverityBadge = (severity: number | string): string => {
    const severityNum = typeof severity === 'number' ? severity : 5;
    if (severityNum >= 7) {
      return 'bg-red-500 text-white';
    } else if (severityNum >= 4) {
      return 'bg-orange-500 text-white';
    } else {
      return 'bg-green-500 text-white';
    }
  };

  /**
   * Get icon for severity level
   */
  const getSeverityIcon = (severity: number | string): string => {
    const severityNum = typeof severity === 'number' ? severity : 5;
    if (severityNum >= 7) {
      return '🔴';
    } else if (severityNum >= 4) {
      return '🟡';
    } else {
      return '🟢';
    }
  };

  /**
   * Get severity label
   */
  const getSeverityLabel = (severity: number | string): string => {
    if (typeof severity === 'string') return severity;
    if (severity >= 7) return 'High';
    if (severity >= 4) return 'Medium';
    return 'Low';
  };

  /**
   * Convert Markdown description to HTML
   * Handles: ## Headings, **bold**, bullet lists, numbered lists, line breaks
   */
  const formatDescription = (text: string): string => {
    let formatted = text;
    
    // Convert ## Headings to <h3> with spacing
    formatted = formatted.replace(/^## (.+)$/gm, '<h3 class="text-lg font-bold text-gray-800 mt-4 mb-2">$1</h3>');
    
    // Convert **bold** to <strong>
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet lists (- item) to proper HTML list items
    // Match lines that start with "- " (with optional leading whitespace)
    formatted = formatted.replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>');
    
    // Convert numbered lists (1. item, 2. item) to proper HTML
    formatted = formatted.replace(/^(\d+)\.\s+(.+)$/gm, '<div class="ml-4 mb-1"><strong>$1.</strong> $2</div>');
    
    // Convert \n\n (double newlines) to paragraph breaks
    formatted = formatted.replace(/\n\n/g, '<br/><br/>');
    
    // Convert single \n to single line break
    formatted = formatted.replace(/\n/g, '<br/>');
    
    // Wrap consecutive <li> items in <ul> tags
    formatted = formatted.replace(/(<li class="ml-4">.*?<\/li>)(?:\s*<br\/>)*(?=<li class="ml-4">)/gs, '$1');
    formatted = formatted.replace(/(<li class="ml-4">.*?<\/li>)(?:\s*<br\/>)*/gs, '<ul class="list-disc list-inside mb-2">$1</ul>');
    
    return formatted;
  };

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 shadow-lg border border-indigo-100 hover:shadow-xl transition-shadow duration-300">
      {/* Blueprint Header */}
      <div className="mb-6">
        <h3 className="text-2xl font-bold text-gray-800 mb-4">
          {blueprint.name}
        </h3>
        
        {/* Description */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h4 className="text-sm font-bold text-gray-600 mb-4 uppercase tracking-wide">
            Architecture Overview
          </h4>
          <div 
            className="text-gray-700 text-sm leading-loose prose prose-sm max-w-none"
            style={{ lineHeight: '1.8' }}
            dangerouslySetInnerHTML={{ __html: formatDescription(blueprint.description) }}
          />
        </div>
      </div>

      {/* Pros and Cons */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Pros */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h4 className="text-lg font-bold text-green-700 mb-4 flex items-center gap-2">
            <span className="text-2xl">✅</span>
            Advantages
          </h4>
          <ul className="space-y-3">
            {blueprint.pros.map((pro, i) => (
              <li key={i} className="flex items-start gap-2 text-gray-700 text-sm">
                <span className="text-green-500 font-bold mt-1">•</span>
                <div>
                  <strong className="text-gray-900">{pro.point}:</strong>{' '}
                  <span>{pro.description}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Cons */}
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h4 className="text-lg font-bold text-orange-700 mb-4 flex items-center gap-2">
            <span className="text-2xl">⚠️</span>
            Considerations
          </h4>
          <ul className="space-y-3">
            {blueprint.cons.map((con, i) => (
              <li key={i} className="flex items-start gap-2 text-gray-700 text-sm">
                <span className="text-orange-500 font-bold mt-1">•</span>
                <div>
                  <strong className="text-gray-900">{con.point}:</strong>{' '}
                  <span>{con.description}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Analyses - Grouped by Agent */}
      {blueprint.analyses && blueprint.analyses.length > 0 && (() => {
        // Group analyses by agent_type
        const systemsAnalyses = blueprint.analyses.filter(a => a.agent_type === 'systems');
        const bizopsAnalyses = blueprint.analyses.filter(a => a.agent_type === 'bizops');
        const unknownAnalyses = blueprint.analyses.filter(a => !a.agent_type);

        return (
          <div className="space-y-6">
            {/* Systems Analyst Findings */}
            {systemsAnalyses.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border-2 border-blue-200">
                <h4 className="text-xl font-bold text-blue-800 mb-4 flex items-center gap-2">
                  <span className="text-2xl">🔧</span>
                  Systems Analyst Findings
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  Technical risks focusing on performance, security, scalability, and reliability
                </p>
                <div className="space-y-4">
                  {systemsAnalyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className={`border-l-4 rounded-lg p-4 transition-all duration-200 hover:scale-[1.01] ${getSeverityColor(
                        analysis.severity
                      )}`}
                    >
                      <div className="flex items-start justify-between mb-2 flex-wrap gap-2">
                        <span className="inline-block bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                          {analysis.category}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold uppercase flex items-center gap-1 ${getSeverityBadge(
                            analysis.severity
                          )}`}
                        >
                          <span>{getSeverityIcon(analysis.severity)}</span>
                          {getSeverityLabel(analysis.severity)}
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed">{analysis.finding}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* BizOps Analyst Findings */}
            {bizopsAnalyses.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm border-2 border-purple-200">
                <h4 className="text-xl font-bold text-purple-800 mb-4 flex items-center gap-2">
                  <span className="text-2xl">💼</span>
                  BizOps Analyst Findings
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  Business and operational risks focusing on cost, team structure, and compliance
                </p>
                <div className="space-y-4">
                  {bizopsAnalyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className={`border-l-4 rounded-lg p-4 transition-all duration-200 hover:scale-[1.01] ${getSeverityColor(
                        analysis.severity
                      )}`}
                    >
                      <div className="flex items-start justify-between mb-2 flex-wrap gap-2">
                        <span className="inline-block bg-purple-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                          {analysis.category}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold uppercase flex items-center gap-1 ${getSeverityBadge(
                            analysis.severity
                          )}`}
                        >
                          <span>{getSeverityIcon(analysis.severity)}</span>
                          {getSeverityLabel(analysis.severity)}
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed">{analysis.finding}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Unknown/Legacy Analyses (backward compatibility) */}
            {unknownAnalyses.length > 0 && (
              <div className="bg-white rounded-xl p-6 shadow-sm">
                <h4 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <span className="text-2xl">📊</span>
                  Additional Analysis
                </h4>
                <div className="space-y-4">
                  {unknownAnalyses.map((analysis) => (
                    <div
                      key={analysis.id}
                      className={`border-l-4 rounded-lg p-4 transition-all duration-200 hover:scale-[1.01] ${getSeverityColor(
                        analysis.severity
                      )}`}
                    >
                      <div className="flex items-start justify-between mb-2 flex-wrap gap-2">
                        <span className="inline-block bg-indigo-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                          {analysis.category}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold uppercase flex items-center gap-1 ${getSeverityBadge(
                            analysis.severity
                          )}`}
                        >
                          <span>{getSeverityIcon(analysis.severity)}</span>
                          {getSeverityLabel(analysis.severity)}
                        </span>
                      </div>
                      <p className="text-sm leading-relaxed">{analysis.finding}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })()}
    </div>
  );
}

