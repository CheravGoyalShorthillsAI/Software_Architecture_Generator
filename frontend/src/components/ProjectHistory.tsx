import { useState, useEffect } from 'react';
import { listProjects, getProjectResults, type ProjectListItem, type ProjectResponse } from '../services/api';
import { Spinner } from './';

interface ProjectHistoryProps {
  onSelectProject: (project: ProjectResponse) => void;
  onBackToHome: () => void;
}

/**
 * ProjectHistory Component
 * 
 * Displays a list of all projects with their status and allows users to
 * view details of completed projects.
 */
export default function ProjectHistory({ onSelectProject, onBackToHome }: ProjectHistoryProps) {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'completed' | 'processing'>('all');
  const [loadingProject, setLoadingProject] = useState<string | null>(null);

  // Load projects on mount and when filter changes
  useEffect(() => {
    loadProjects();
  }, [filter]);

  const loadProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const statusFilter = filter === 'all' ? undefined : filter;
      const response = await listProjects(0, 50, statusFilter);
      
      // Filter out error projects from "All Projects" view
      const filteredProjects = filter === 'all' 
        ? response.projects.filter(project => project.status !== 'error')
        : response.projects;
      
      setProjects(filteredProjects);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
      console.error('Failed to load projects:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectClick = async (projectId: string) => {
    setLoadingProject(projectId);
    try {
      const projectData = await getProjectResults(projectId);
      onSelectProject(projectData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project details');
      console.error('Failed to load project:', err);
    } finally {
      setLoadingProject(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'processing':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'processing':
        return '⏳';
      case 'error':
        return '❌';
      default:
        return '⚪';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 via-purple-700 to-indigo-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <button
            onClick={onBackToHome}
            className="text-white hover:text-purple-200 transition-colors mb-4 flex items-center gap-2"
          >
            <span className="text-xl">←</span>
            <span>Back to Home</span>
          </button>
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
            📚 Project History
          </h1>
          <p className="text-purple-100">
            View and manage all your generated architecture projects
          </p>
        </header>

        {/* Filter Buttons */}
        <div className="mb-6 flex flex-wrap gap-3">
          {(['all', 'completed', 'processing'] as const).map((filterOption) => (
            <button
              key={filterOption}
              onClick={() => setFilter(filterOption)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === filterOption
                  ? 'bg-white text-purple-700 shadow-lg'
                  : 'bg-purple-800 bg-opacity-50 text-white hover:bg-opacity-70'
              }`}
            >
              {filterOption === 'all' ? 'All Projects' : filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
            </button>
          ))}
        </div>

        {/* Main Content */}
        <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8">
          {isLoading && (
            <div className="flex items-center justify-center py-20">
              <Spinner size="large" message="Loading projects..." />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-6">
              <div className="flex items-center">
                <span className="text-2xl mr-3">❌</span>
                <p className="text-red-700 font-medium">{error}</p>
              </div>
            </div>
          )}

          {!isLoading && !error && projects.length === 0 && (
            <div className="text-center py-20">
              <p className="text-2xl text-gray-400 mb-2">📭</p>
              <p className="text-gray-600 text-lg">No projects found</p>
              <p className="text-gray-500 text-sm mt-2">
                {filter !== 'all' ? `No ${filter} projects` : 'Create your first project to see it here!'}
              </p>
            </div>
          )}

          {!isLoading && !error && projects.length > 0 && (
            <div className="space-y-4">
              {projects.map((project) => (
                <div
                  key={project.id}
                  className={`border-2 rounded-xl p-5 transition-all hover:shadow-lg ${
                    project.status === 'completed'
                      ? 'cursor-pointer hover:border-purple-400'
                      : 'cursor-default opacity-75'
                  } ${loadingProject === project.id ? 'opacity-50' : ''}`}
                  onClick={() => project.status === 'completed' && handleProjectClick(project.id)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-bold border-2 ${getStatusColor(
                            project.status
                          )}`}
                        >
                          {getStatusIcon(project.status)} {project.status.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">
                          {formatDate(project.created_at)}
                        </span>
                      </div>
                      <p className="text-gray-800 text-base leading-relaxed">
                        {project.user_prompt}
                      </p>
                    </div>
                    {project.status === 'completed' && (
                      <div className="flex-shrink-0">
                        {loadingProject === project.id ? (
                          <div className="animate-spin h-6 w-6 border-2 border-purple-500 border-t-transparent rounded-full" />
                        ) : (
                          <span className="text-purple-600 text-2xl">→</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Refresh Button */}
          {!isLoading && (
            <div className="mt-6 text-center">
              <button
                onClick={loadProjects}
                className="text-purple-600 hover:text-purple-700 font-medium text-sm flex items-center gap-2 mx-auto"
              >
                <span className="text-lg">🔄</span>
                Refresh
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

