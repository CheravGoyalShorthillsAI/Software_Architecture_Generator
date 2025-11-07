import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';
import type { Blueprint } from '../services/api';

interface ArchitectureDiagramProps {
  blueprint: Blueprint;
}

/**
 * ArchitectureDiagram Component
 * 
 * Generates and displays an interactive architecture diagram
 * based on the blueprint description using Mermaid.js
 * 
 * @param blueprint - The architecture blueprint data
 */
export default function ArchitectureDiagram({ blueprint }: ArchitectureDiagramProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [diagramSvg, setDiagramSvg] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRawDiagram, setShowRawDiagram] = useState(false);

  useEffect(() => {
    // Initialize Mermaid with error suppression
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
      },
      logLevel: 'error', // Suppress verbose logging
      suppressErrors: true, // Don't display errors in UI
    });

    const generateDiagram = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Use LLM-generated diagram if available, otherwise generate from description
        const diagramDefinition = blueprint.mermaid_diagram 
          ? blueprint.mermaid_diagram 
          : generateMermaidSyntax(blueprint);
        
        console.log('Mermaid diagram definition:', diagramDefinition);
        console.log('Diagram length:', diagramDefinition.length, 'characters');
        console.log('Source:', blueprint.mermaid_diagram ? 'LLM-generated (Gemini)' : 'Client-side fallback');

        // Clean up diagram definition - remove any problematic characters
        let cleanedDiagram = diagramDefinition.trim();
        
        // Remove any HTML/XML tags that might cause issues
        cleanedDiagram = cleanedDiagram.replace(/<br\s*\/?>/gi, '<br/>');
        
        // Validate diagram starts correctly
        if (!cleanedDiagram.startsWith('graph ')) {
          console.error('Invalid diagram syntax - must start with "graph TB" or "graph TD"');
          throw new Error('Invalid Mermaid syntax: diagram must start with "graph TB" or "graph TD"');
        }

        // Generate unique ID for the diagram
        const id = `mermaid-${Date.now()}`;
        
        console.log('Attempting to render diagram with ID:', id);
        
        // Render the diagram
        const { svg } = await mermaid.render(id, cleanedDiagram);
        setDiagramSvg(svg);
        console.log('✅ Diagram rendered successfully');
      } catch (err: any) {
        console.error('❌ Error generating diagram:', err);
        console.error('Error message:', err.message);
        console.error('Error details:', err);
        setError(`Failed to generate diagram: ${err.message || 'Unknown error'}. Check browser console for details.`);
      } finally {
        setIsLoading(false);
      }
    };

    generateDiagram();
  }, [blueprint]);

  return (
    <div className="bg-white rounded-2xl p-8 shadow-xl border border-gray-200">
      <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
        <span className="text-3xl">🏗️</span>
        Architecture Diagram
      </h3>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="flex items-center gap-3 text-purple-600">
            <svg className="animate-spin h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="font-medium">Generating architecture diagram...</span>
          </div>
        </div>
      )}

      {error && (
        <div className="space-y-4">
          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-lg">
            <div className="flex items-start gap-3">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="text-yellow-900 font-bold text-lg mb-2">Diagram Generation Issue</p>
                <p className="text-yellow-800 mb-3">{error}</p>
                <p className="text-sm text-yellow-700 bg-yellow-100 p-3 rounded">
                  <strong>Note:</strong> This project was generated with an older version. 
                  Generate a new project to see the improved architecture diagrams with correct syntax.
                </p>
              </div>
            </div>
          </div>
          
          {blueprint.mermaid_diagram && (
            <div className="bg-gray-50 border border-gray-300 rounded-lg p-4">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-semibold text-gray-900">🔍 Raw Mermaid Diagram (for debugging)</h4>
                <button
                  onClick={() => setShowRawDiagram(!showRawDiagram)}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium px-3 py-1 bg-blue-100 rounded"
                >
                  {showRawDiagram ? 'Hide' : 'Show'} Raw Code
                </button>
              </div>
              {showRawDiagram && (
                <pre className="bg-white p-4 rounded border border-gray-200 overflow-x-auto text-xs font-mono max-h-96 overflow-y-auto">
                  {blueprint.mermaid_diagram}
                </pre>
              )}
            </div>
          )}
        </div>
      )}

      {!isLoading && !error && diagramSvg && (
        <div
          ref={containerRef}
          className="diagram-container overflow-x-auto bg-gradient-to-br from-gray-50 to-blue-50 p-6 rounded-xl border-2 border-gray-200"
          dangerouslySetInnerHTML={{ __html: diagramSvg }}
        />
      )}

      <div className="mt-4 text-sm text-gray-600 bg-gradient-to-r from-blue-50 to-indigo-50 p-5 rounded-xl border-2 border-blue-200 shadow-sm">
        <p className="font-bold text-blue-900 mb-3 text-base">💡 Diagram Legend</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-pink-500 rounded"></div>
            <span className="font-medium">Clients</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-orange-500 rounded"></div>
            <span className="font-medium">Gateway/LB</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-blue-500 rounded"></div>
            <span className="font-medium">Services</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-green-500 rounded"></div>
            <span className="font-medium">Databases</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-purple-500 rounded"></div>
            <span className="font-medium">Queues</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-cyan-500 rounded"></div>
            <span className="font-medium">Cache</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-lime-500 rounded"></div>
            <span className="font-medium">Storage</span>
          </div>
          <div className="flex items-center gap-2 bg-white px-3 py-2 rounded-lg shadow-sm">
            <div className="w-4 h-4 bg-orange-600 rounded"></div>
            <span className="font-medium">Monitoring</span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Generate Mermaid diagram syntax from blueprint description
 */
function generateMermaidSyntax(blueprint: Blueprint): string {
  const description = blueprint.description.toLowerCase();

  // Extract services from description
  const services: string[] = [];
  const servicePatterns = [
    'authentication service',
    'auth service',
    'task service',
    'workspace service',
    'notification service',
    'file storage service',
    'file service',
    'user service',
    'payment service',
    'order service',
    'api gateway',
    'gateway service',
  ];

  servicePatterns.forEach(pattern => {
    if (description.includes(pattern)) {
      services.push(pattern);
    }
  });

  // If no services found, extract from description using common patterns
  if (services.length === 0) {
    const matches = description.match(/(\w+)\s+service/g);
    if (matches) {
      services.push(...matches.slice(0, 6)); // Limit to 6 services
    }
  }

  // Detect infrastructure components
  const hasMessageBroker = description.includes('kafka') || description.includes('rabbitmq') || description.includes('message broker');
  const hasDatabase = description.includes('database') || description.includes('postgresql') || description.includes('mysql');
  const hasAPIGateway = description.includes('api gateway') || description.includes('gateway');
  const hasWebSocket = description.includes('websocket');
  const hasCache = description.includes('redis') || description.includes('cache');
  const hasServiceMesh = description.includes('istio') || description.includes('service mesh');

  // Build Mermaid flowchart
  let diagram = 'graph TB\n';
  diagram += '    %% Style definitions\n';
  diagram += '    classDef serviceClass fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff\n';
  diagram += '    classDef dbClass fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff\n';
  diagram += '    classDef queueClass fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff\n';
  diagram += '    classDef gatewayClass fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff\n';
  diagram += '    classDef clientClass fill:#ec4899,stroke:#db2777,stroke-width:2px,color:#fff\n\n';

  // Add client
  diagram += '    Client[👤 Client/Browser]:::clientClass\n\n';

  // Add API Gateway if mentioned
  if (hasAPIGateway) {
    diagram += '    Gateway[🌐 API Gateway]:::gatewayClass\n';
    diagram += '    Client --> Gateway\n\n';
  }

  // Add services
  const serviceIcons = ['🔐', '📋', '👥', '🔔', '📁', '💳', '📦', '⚙️'];
  services.forEach((service, index) => {
    const serviceName = service.replace(/\s+/g, '');
    const icon = serviceIcons[index % serviceIcons.length];
    const label = service.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    
    diagram += `    ${serviceName}[${icon} ${label}]:::serviceClass\n`;
    
    if (hasAPIGateway) {
      diagram += `    Gateway --> ${serviceName}\n`;
    } else {
      diagram += `    Client --> ${serviceName}\n`;
    }
  });

  diagram += '\n';

  // Add message broker
  if (hasMessageBroker) {
    diagram += '    MessageBroker[📨 Message Broker<br/>Kafka/RabbitMQ]:::queueClass\n';
    services.forEach(service => {
      const serviceName = service.replace(/\s+/g, '');
      diagram += `    ${serviceName} -.->|events| MessageBroker\n`;
    });
    diagram += '\n';
  }

  // Add databases
  if (hasDatabase) {
    services.forEach((service, index) => {
      const serviceName = service.replace(/\s+/g, '');
      const dbName = `DB${index + 1}`;
      diagram += `    ${dbName}[(🗄️ Database)]:::dbClass\n`;
      diagram += `    ${serviceName} --> ${dbName}\n`;
    });
    diagram += '\n';
  }

  // Add cache if mentioned
  if (hasCache) {
    diagram += '    Cache[⚡ Redis Cache]:::queueClass\n';
    const firstService = services[0]?.replace(/\s+/g, '');
    if (firstService) {
      diagram += `    ${firstService} -.-> Cache\n\n`;
    }
  }

  // Add WebSocket connection
  if (hasWebSocket) {
    diagram += '    WS[🔌 WebSocket Server]:::gatewayClass\n';
    diagram += '    Client -.->|real-time| WS\n';
    if (services.length > 0) {
      const firstService = services[0]?.replace(/\s+/g, '');
      diagram += `    WS -.-> ${firstService}\n`;
    }
    diagram += '\n';
  }

  // Add service mesh if mentioned
  if (hasServiceMesh) {
    diagram += '    subgraph ServiceMesh[🕸️ Service Mesh - Istio]\n';
    services.forEach(service => {
      const serviceName = service.replace(/\s+/g, '');
      diagram += `        ${serviceName}\n`;
    });
    diagram += '    end\n';
  }

  return diagram;
}

