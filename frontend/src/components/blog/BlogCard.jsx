/**
 * Blog Card component - for displaying blog posts in lists.
 */
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ClockIcon,
  ChatBubbleLeftRightIcon,
  PencilIcon,
  TrashIcon,
} from '@heroicons/react/24/outline';
import { Card, CardContent } from '../ui/Card';
import { Badge } from '../ui/Badge';
import ConfirmDialog from '../ui/ConfirmDialog';
import { encryptBlogId } from '../../utils/blogIdCrypto';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import { blogApi } from '../../services/api';

const statusVariants = {
  completed: 'green',
  generating: 'yellow',
  failed: 'red',
  draft: 'gray',
};

export default function BlogCard({ blogPost }) {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { success, error } = useToast();
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const encryptedId = encryptBlogId(blogPost.id);
  const sharedUrl = `${window.location.origin}/share/${blogPost.slug}`;
  const sentiment = blogPost.sentiment_score || 0;

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

  const handleDelete = async () => {
    if (isDeleting) return;
    setIsDeleting(true);
    try {
      await blogApi.delete(blogPost.id);
      success('Blog post deleted');
      navigate('/blogs', { state: { refresh: Date.now() } });
    } catch (err) {
      error(err?.message || 'Failed to delete blog post');
      setIsDeleting(false);
      setShowDeleteDialog(false);
    }
  };

  return (
    <Card className="flex h-full flex-col hover:border-ink-400 dark:hover:border-ink-600">
      <CardContent className="flex flex-1 flex-col">
        <Link to={`/blog/${encryptedId}`} className="group block flex-1">
          {/* Provenance and status, above the headline. */}
          <div className="mb-3 flex flex-wrap items-center gap-2">
            <span className="chip">AI generated</span>
            <Badge variant={statusVariants[blogPost.status] || 'gray'}>
              {blogPost.status}
            </Badge>
          </div>

          <h3 className="mb-2 font-display text-xl font-semibold leading-snug tracking-tight text-ink-950 line-clamp-2 transition-colors duration-200 group-hover:text-accent-600 dark:text-ink-50 dark:group-hover:text-accent-400">
            {blogPost.title}
          </h3>

          <p className="mb-5 text-sm leading-relaxed text-ink-600 line-clamp-2 dark:text-ink-400">
            {blogPost.topic_input}
          </p>

          {/* Footer */}
          <div className="flex items-center justify-between text-sm text-ink-500 dark:text-ink-400">
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center gap-1.5">
                <ClockIcon className="h-4 w-4" aria-hidden="true" />
                {blogPost.reading_time} min
              </span>
              {blogPost.persona && (
                <span className="chip" title="Writing persona">
                  {blogPost.persona}
                </span>
              )}
            </div>

            <span className="inline-flex items-center gap-1.5" title="Reader sentiment">
              <ChatBubbleLeftRightIcon className="h-4 w-4" aria-hidden="true" />
              <span
                className={
                  sentiment >= 0
                    ? 'font-medium text-emerald-700 dark:text-emerald-400'
                    : 'font-medium text-red-700 dark:text-red-400'
                }
              >
                {sentiment > 0 ? '+' : ''}{sentiment}
              </span>
            </span>
          </div>
        </Link>

        {isAuthenticated && blogPost.slug && (
          <div className="rule mt-5 pt-4">
            <div className="flex flex-wrap items-center gap-2">
              <button type="button" onClick={copyShareLink} className="btn btn-quiet px-3 py-1.5 text-sm">
                Share link
              </button>
              <button
                type="button"
                onClick={() => navigate(`/blog/${encryptedId}?edit=1`)}
                className="btn btn-quiet inline-flex items-center gap-1.5 px-3 py-1.5 text-sm"
              >
                <PencilIcon className="h-4 w-4" aria-hidden="true" />
                Edit
              </button>
              <button
                type="button"
                onClick={() => setShowDeleteDialog(true)}
                className="btn btn-danger-quiet inline-flex items-center gap-1.5 px-3 py-1.5 text-sm"
              >
                <TrashIcon className="h-4 w-4" aria-hidden="true" />
                Delete
              </button>
            </div>
          </div>
        )}
      </CardContent>

      <ConfirmDialog
        open={showDeleteDialog}
        title="Delete blog post?"
        message={`"${blogPost.title}" will be permanently removed. This cannot be undone.`}
        isConfirming={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteDialog(false)}
      />
    </Card>
  );
}
