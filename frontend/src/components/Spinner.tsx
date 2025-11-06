interface SpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  message?: string;
}

/**
 * Spinner Component
 * 
 * A simple, customizable loading spinner component
 * 
 * @param size - Size of the spinner: 'small', 'medium', or 'large'
 * @param color - Tailwind color class for the spinner (e.g., 'border-purple-600')
 * @param message - Optional message to display below the spinner
 */
export default function Spinner({ 
  size = 'medium', 
  color = 'border-purple-600',
  message 
}: SpinnerProps) {
  const sizeClasses = {
    small: 'h-6 w-6 border-2',
    medium: 'h-10 w-10 border-3',
    large: 'h-16 w-16 border-4',
  };

  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div
        className={`animate-spin rounded-full border-t-transparent ${sizeClasses[size]} ${color}`}
        role="status"
        aria-label="Loading"
      >
        <span className="sr-only">Loading...</span>
      </div>
      {message && (
        <p className="text-gray-600 text-sm font-medium animate-pulse">
          {message}
        </p>
      )}
    </div>
  );
}

