/**
 * Blog Detail Page - displays a single blog post with engagement.
 */
import { useParams } from 'react-router-dom';
import { useBlogPost } from '../hooks/useBlogPosts';
import BlogViewer from '../components/blog/BlogViewer';
import { Link } from 'react-router-dom';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';
import { decryptBlogId } from '../utils/blogIdCrypto';

export default function BlogDetailPage() {
  const { id } = useParams();
  const postId = id ? decryptBlogId(id) : null;
  const { post, isLoading } = useBlogPost(postId);

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <Link
        to="/blogs"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors"
      >
        <ArrowLeftIcon className="w-5 h-5" />
        Back to Blog Posts
      </Link>

      {/* Blog Content */}
      <BlogViewer blogPost={post} isLoading={isLoading} />
    </div>
  );
}
