/**
 * Blog Card component - for displaying blog posts in lists.
 */
import { Link } from 'react-router-dom';
import { ClockIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { encryptBlogId } from '../../utils/blogIdCrypto';

export default function BlogCard({ blogPost }) {
  const statusColors = {
    completed: 'green',
    generating: 'yellow',
    failed: 'red',
    draft: 'gray',
  };

  const encryptedId = encryptBlogId(blogPost.id);

  return (
    <Link to={`/blog/${encryptedId}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer h-full">
        <CardContent>
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
        </CardContent>
      </Card>
    </Link>
  );
}
