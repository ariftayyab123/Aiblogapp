/**
 * Blog Detail Page - displays a single blog post with engagement.
 */
import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useBlogPost } from '../hooks/useBlogPosts';
import BlogViewer from '../components/blog/BlogViewer';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { decryptBlogId } from '../utils/blogIdCrypto';
import { blogApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import Swal from 'sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';
import { useAuth } from '../contexts/AuthContext';

export default function BlogDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { success, error } = useToast();
  const { isAuthenticated } = useAuth();
  const postId = id ? decryptBlogId(id) : null;
  const { post, isLoading } = useBlogPost(postId);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!post?.id || isDeleting) return;

    const result = await Swal.fire({
      title: 'Delete blog post?',
      text: 'This action cannot be undone.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonText: 'Delete',
      cancelButtonText: 'Cancel',
      reverseButtons: true,
      focusCancel: true,
      buttonsStyling: false,
      customClass: {
        popup: 'rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800',
        title: 'text-gray-900 dark:text-white',
        htmlContainer: 'text-gray-600 dark:text-gray-300',
        actions: 'gap-2',
        confirmButton:
          'px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors disabled:opacity-60',
        cancelButton:
          'px-4 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 transition-colors dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700',
      },
    });

    if (!result.isConfirmed) return;

    setIsDeleting(true);
    try {
      await blogApi.delete(post.id);
      success('Blog post deleted');
      navigate('/blogs');
    } catch (err) {
      error(err?.message || 'Failed to delete blog post');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleShare = async () => {
    if (!post?.slug) return;
    const shareUrl = `${window.location.origin}/share/${post.slug}`;
    try {
      await navigator.clipboard.writeText(shareUrl);
      success('Share link copied');
    } catch {
      error('Failed to copy share link');
    }
  };

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <div className="flex items-center justify-between gap-3">
        <Link
          to="/blogs"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
          Back to Blog Posts
        </Link>
        {!isLoading && post && isAuthenticated && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={handleShare}
              className="inline-flex items-center px-3 py-2 rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
            >
              Share Blog
            </button>
            <button
              type="button"
              onClick={handleDelete}
              disabled={isDeleting}
              className="inline-flex items-center px-3 py-2 rounded-lg border border-red-300 text-red-700 hover:bg-red-50 disabled:opacity-60 disabled:cursor-not-allowed dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/20 transition-colors"
            >
              {isDeleting ? 'Deleting...' : 'Delete Blog'}
            </button>
          </div>
        )}
      </div>

      {/* Blog Content */}
      <BlogViewer blogPost={post} isLoading={isLoading} />
    </div>
  );
}
