/**
 * Source List component - displays blog post sources as clickable rows.
 */
import { ArrowTopRightOnSquareIcon, CheckCircleIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

export default function SourceList({ sources = [] }) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <section aria-labelledby="sources-heading" className="space-y-4">
      <h2
        id="sources-heading"
        className="font-display text-xl font-semibold tracking-tight text-ink-950 dark:text-ink-50"
      >
        Sources
      </h2>

      <ul className="rule border-b border-ink-200 dark:border-ink-800">
        {sources.map((source, index) => (
          <li key={source.url || index}>
            <a
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="row-editorial group flex items-start gap-3"
            >
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center gap-2">
                  <h3 className="truncate font-medium text-ink-950 transition-colors duration-200 group-hover:text-accent-600 dark:text-ink-50 dark:group-hover:text-accent-400">
                    {source.title}
                  </h3>
                  {source.is_verified ? (
                    <CheckCircleIcon
                      className="h-4 w-4 flex-shrink-0 text-emerald-600 dark:text-emerald-400"
                      title="Verified source"
                    />
                  ) : (
                    <QuestionMarkCircleIcon
                      className="h-4 w-4 flex-shrink-0 text-amber-600 dark:text-amber-500"
                      title="Unverified source"
                    />
                  )}
                </div>
                <div className="flex items-center gap-2 text-sm text-ink-600 dark:text-ink-400">
                  <span className="truncate">{source.domain}</span>
                  {source.relevance_score && (
                    <span className="chip">
                      {Math.round(source.relevance_score * 100)}% relevant
                    </span>
                  )}
                </div>
              </div>

              <ArrowTopRightOnSquareIcon
                className="h-5 w-5 flex-shrink-0 text-ink-400 transition-colors duration-200 group-hover:text-ink-900 dark:group-hover:text-ink-100"
                aria-hidden="true"
              />
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
