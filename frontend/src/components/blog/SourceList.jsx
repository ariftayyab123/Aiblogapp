/**
 * Source List component - displays blog post sources as clickable cards.
 */
import { ArrowTopRightOnSquareIcon, CheckCircleIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

export default function SourceList({ sources = [] }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
        Sources
      </h2>

      <div className="grid gap-3">
        {sources.map((source, index) => (
          <a
            key={index}
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="source-card flex items-start gap-3 group"
          >
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-medium text-gray-900 dark:text-white group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                  {source.title}
                </h3>
                {source.is_verified ? (
                  <CheckCircleIcon className="w-4 h-4 text-green-500 flex-shrink-0" />
                ) : (
                  <QuestionMarkCircleIcon className="w-4 h-4 text-yellow-500 flex-shrink-0" />
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                <span className="truncate">{source.domain}</span>
                {source.relevance_score && (
                  <span className="px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded text-xs">
                    {Math.round(source.relevance_score * 100)}% relevant
                  </span>
                )}
              </div>
            </div>

            <ArrowTopRightOnSquareIcon className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors flex-shrink-0" />
          </a>
        ))}
      </div>
    </div>
  );
}
