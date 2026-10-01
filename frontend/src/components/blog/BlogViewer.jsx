/**
 * Blog Viewer component - displays generated blog post content.
 */
import ReactMarkdown from 'react-markdown';
import { ClockIcon, EyeIcon } from '@heroicons/react/24/outline';
import { useEngagement } from '../../hooks/useEngagement';
import { Badge } from '../ui/Badge';
import EngagementBar from './EngagementBar';
import SourceList from './SourceList';

export default function BlogViewer({ blogPost, isLoading }) {
  const { state: engagementState, like, dislike } = useEngagement(blogPost?.id);

  if (isLoading) {
    // Skeleton mirrors the real layout so nothing shifts when content lands.
    return (
      <div className="space-y-5" aria-busy="true" aria-label="Loading article">
        <div className="skeleton h-5 w-32" />
        <div className="skeleton h-10 w-3/4" />
        <div className="skeleton h-4 w-64" />
        <div className="space-y-3 pt-6">
          <div className="skeleton h-4 w-full" />
          <div className="skeleton h-4 w-full" />
          <div className="skeleton h-4 w-5/6" />
        </div>
      </div>
    );
  }

  if (!blogPost) {
    return (
      <div className="py-16 text-center">
        <p className="text-ink-600 dark:text-ink-400">Blog post not found.</p>
      </div>
    );
  }

  const structure = blogPost.content_structure || {};

  return (
    <article className="space-y-8">
      <header className="space-y-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="chip">AI generated</span>
          {blogPost.persona && (
            <Badge variant="blue" dot={false}>{blogPost.persona.name}</Badge>
          )}
          <Badge variant={blogPost.status === 'completed' ? 'green' : 'yellow'}>
            {blogPost.status}
          </Badge>
        </div>

        <h1 className="font-display text-3xl font-semibold leading-tight tracking-tight text-ink-950 md:text-[2.75rem] dark:text-ink-50">
          {blogPost.title}
        </h1>

        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm text-ink-600 dark:text-ink-400">
          <span className="inline-flex items-center gap-1.5">
            <ClockIcon className="h-4 w-4" aria-hidden="true" />
            {structure.reading_time_minutes || blogPost.reading_time || 1} min read
          </span>
          <span className="inline-flex items-center gap-1.5">
            <EyeIcon className="h-4 w-4" aria-hidden="true" />
            {structure.word_count || blogPost.word_count || 0} words
          </span>
          <span className="inline-flex min-w-0 items-center gap-1.5">
            <span className="eyebrow">Topic</span>
            <span className="truncate">{blogPost.topic_input}</span>
          </span>
        </div>
      </header>

      <EngagementBar
        likes={engagementState.likes}
        dislikes={engagementState.dislikes}
        userAction={engagementState.userEngagement}
        onLike={like}
        onDislike={dislike}
        isLoading={engagementState.isSubmitting}
      />

      {/* Body. .prose-editorial caps the measure at 72ch per the detail spec. */}
      <div className="prose-editorial">
        <ReactMarkdown>{blogPost.generated_content || ''}</ReactMarkdown>
      </div>

      {blogPost.sources && blogPost.sources.length > 0 && (
        <SourceList sources={blogPost.sources} />
      )}
    </article>
  );
}
