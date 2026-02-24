import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import BlogViewer from '../components/blog/BlogViewer';
import { blogApi } from '../services/api';

export default function SharedBlogPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      if (!slug) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await blogApi.getPublicBySlug(slug);
        setPost(response.data);
      } catch {
        setPost(null);
      } finally {
        setIsLoading(false);
      }
    };
    run();
  }, [slug]);

  if (!isLoading && !post) {
    return (
      <div className="max-w-3xl mx-auto py-12 text-center">
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Blog not found</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          This shared link is invalid or the post is not publicly available.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <BlogViewer blogPost={post} isLoading={isLoading} />
    </div>
  );
}
