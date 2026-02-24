/**
 * Blog Card component - for displaying blog posts in lists.
 */
import { Link } from 'react-router-dom';
import { ClockIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { encryptBlogId } from '../../utils/blogIdCrypto';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';

export default function BlogCard({ blogPost }) {
  const { isAuthenticated } = useAuth();
  const { success, error } = useToast();
  const statusColors = {
    completed: 'green',
    generating: 'yellow',
    failed: 'red',
    draft: 'gray',
  };

  const encryptedId = encryptBlogId(blogPost.id);
  const sharedUrl = `${window.location.origin}/share/${blogPost.slug}`;

  const copyShareLink = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(sharedUrl);
      success('Share link copied');
    } catch {
      error('Failed to copy share link');
    }
  };

  return (
    <Card className="hover:shadow-md transition-shadow h-full">
      <CardContent>
        <Link to={`/blog/${encryptedId}`} className="block">
          {/* Header */}
          <div className="flex items-start justify-between gap-3 mb-3">
            <h3 className="font-semibold text-gray-900 dark:text-white line-clamp-2">
              {blogPost.title}
            </h3>
            <Badge variant={statusColors[blogPost.status] || 'gray'}>
              {blogPost.status}
            </Badge>
          </div>

          {/* Topic */}
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {blogPost.topic_input}
          </p>

          {/* Footer */}
          <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-500">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                <span>{blogPost.reading_time} min</span>
              </div>
              {blogPost.persona && (
                <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">
                  {blogPost.persona}
                </span>
              )}
            </div>

            <div className="flex items-center gap-1">
              <ChatBubbleLeftRightIcon className="w-4 h-4" />
              <span className={blogPost.sentiment_score >= 0 ? 'text-green-600' : 'text-red-600'}>
                {blogPost.sentiment_score > 0 ? '+' : ''}{blogPost.sentiment_score}
              </span>
            </div>
          </div>
        </Link>

        {isAuthenticated && blogPost.slug && (
          <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
            <button
              type="button"
              onClick={copyShareLink}
              className="text-sm px-3 py-1.5 rounded-md border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              Share Link
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
