/**
 * Blog Detail Page - displays a single blog post with engagement.
 * Supports viewing, editing (title/topic/content), sharing, and deleting.
 */
import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArrowLeftIcon, PencilIcon, TrashIcon, ShareIcon } from '@heroicons/react/24/outline';
import { useBlogPost, useEditBlogPost } from '../hooks/useBlogPosts';
import BlogViewer from '../components/blog/BlogViewer';
import BlogEditor from '../components/blog/BlogEditor';
import ConfirmDialog from '../components/ui/ConfirmDialog';
import { decryptBlogId } from '../utils/blogIdCrypto';
import { blogApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';

export default function BlogDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { success, error } = useToast();
  const { isAuthenticated } = useAuth();
  const postId = id ? decryptBlogId(id) : null;
  const { post, isLoading, updatePost } = useBlogPost(postId);
  const { isSaving, savePost } = useEditBlogPost();

  const [isEditing, setIsEditing] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);

  useEffect(() => {
    if (searchParams.get('edit') === '1' && post) {
      setIsEditing(true);
      setSearchParams({}, { replace: true });
    }
  }, [searchParams, post, setSearchParams]);

  const handleSave = async (data) => {
    if (!post?.id) return;
    const updated = await savePost(post.id, data);
    if (updated) {
      updatePost(updated);
      setIsEditing(false);
    }
  };

  const handleDelete = async () => {
    if (!post?.id || isDeleting) return;
    setIsDeleting(true);
    try {
      await blogApi.delete(post.id);
      success('Blog post deleted');
      navigate('/blogs');
    } catch (err) {
      error(err?.message || 'Failed to delete blog post');
      setIsDeleting(false);
      setShowDeleteDialog(false);
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

  const ownedActions = !isLoading && post && isAuthenticated && (
    <div className="flex flex-wrap items-center gap-2">
      <button
        type="button"
        onClick={handleShare}
        className="btn btn-quiet inline-flex items-center gap-1.5 px-3 py-2 text-sm"
      >
        <ShareIcon className="h-4 w-4" aria-hidden="true" />
        Share
      </button>
      <button
        type="button"
        onClick={() => setIsEditing(true)}
        className="btn btn-quiet inline-flex items-center gap-1.5 px-3 py-2 text-sm"
      >
        <PencilIcon className="h-4 w-4" aria-hidden="true" />
        Edit
      </button>
      <button
        type="button"
        onClick={() => setShowDeleteDialog(true)}
        className="btn btn-danger-quiet inline-flex items-center gap-1.5 px-3 py-2 text-sm"
      >
        <TrashIcon className="h-4 w-4" aria-hidden="true" />
        Delete
      </button>
    </div>
  );

  return (
    // Page frame is 1400px per the blog-detail spec; the reading column stays
    // narrow so the measure holds at 65-75 characters.
    <div className="mx-auto max-w-wide space-y-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Link to="/blogs" className="link-quiet">
          <ArrowLeftIcon className="h-5 w-5" aria-hidden="true" />
          Back to Blog Posts
        </Link>
        {ownedActions}
      </div>

      <div className="rule" />

      <div className="mx-auto max-w-measure">
        {isEditing && post ? (
          <BlogEditor
            blogPost={post}
            isSaving={isSaving}
            onSave={handleSave}
            onCancel={() => setIsEditing(false)}
          />
        ) : (
          <BlogViewer blogPost={post} isLoading={isLoading} />
        )}
      </div>

      <ConfirmDialog
        open={showDeleteDialog}
        title="Delete blog post?"
        message="This action cannot be undone. The post and its feedback will be permanently removed."
        confirmText="Delete"
        isConfirming={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteDialog(false)}
      />
    </div>
  );
}