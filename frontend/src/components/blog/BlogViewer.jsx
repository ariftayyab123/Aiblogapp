/**
 * Blog Viewer component - displays generated blog post content.
 */
import { useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { ClockIcon, EyeIcon } from '@heroicons/react/24/outline';
import { useEngagement } from '../../hooks/useEngagement';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import EngagementBar from './EngagementBar';
import SourceList from './SourceList';

export default function BlogViewer({ blogPost, isLoading }) {
  const { state: engagementState, like, dislike } = useEngagement(blogPost?.id);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-3/4" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full" />
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-5/6" />
        </div>
      </div>
    );
  }

  if (!blogPost) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600 dark:text-gray-400">Blog post not found.</p>
      </div>
    );
  }

  const structure = blogPost.content_structure || {};

  return (
    <article className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <header className="space-y-4">
        <div className="flex items-center gap-2 flex-wrap">
          {blogPost.persona && (
            <Badge variant="blue">{blogPost.persona.name}</Badge>
          )}
          <Badge variant={blogPost.status === 'completed' ? 'green' : 'yellow'}>
            {blogPost.status}
          </Badge>
        </div>

        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">
          {blogPost.title}
        </h1>

        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-1">
            <ClockIcon className="w-4 h-4" />
            <span>{structure.reading_time_minutes || blogPost.reading_time || 1} min read</span>
          </div>
          <div className="flex items-center gap-1">
            <EyeIcon className="w-4 h-4" />
            <span>{structure.word_count || blogPost.word_count || 0} words</span>
          </div>
        </div>

        <p className="text-gray-700 dark:text-gray-300">
          <span className="font-medium">Topic:</span> {blogPost.topic_input}
        </p>
      </header>

      {/* Engagement Bar */}
      <EngagementBar
        likes={engagementState.likes}
        dislikes={engagementState.dislikes}
        userAction={engagementState.userEngagement}
        onLike={like}
        onDislike={dislike}
        isLoading={engagementState.isSubmitting}
      />

      {/* Content */}
      <Card>
        <div className="prose-content">
          <ReactMarkdown>{blogPost.generated_content || ''}</ReactMarkdown>
        </div>
      </Card>

      {/* Sources */}
      {blogPost.sources && blogPost.sources.length > 0 && (
        <SourceList sources={blogPost.sources} />
      )}

      {/* Metadata (expandable) */}
      {blogPost.metadata && Object.keys(blogPost.metadata).length > 0 && (
        <details className="text-sm">
          <summary className="cursor-pointer text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            Generation Metadata
          </summary>
          <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-x-auto">
            {JSON.stringify(blogPost.metadata, null, 2)}
          </pre>
        </details>
      )}
    </article>
  );
}
