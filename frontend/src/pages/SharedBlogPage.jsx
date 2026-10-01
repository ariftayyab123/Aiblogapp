import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import BlogViewer from '../components/blog/BlogViewer';
import { blogApi } from '../services/api';

export default function SharedBlogPage() {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    const run = async () => {
      setIsLoading(true);
      setLoadError('');
      if (!slug) {
        setPost(null);
        setIsLoading(false);
        return;
      }
      try {
        const response = await blogApi.getPublicBySlug(slug);
        setPost(response.data);
      } catch (err) {
        setPost(null);
        setLoadError(err?.status === 404 ? 'not_found' : (err?.message || 'network'));
      } finally {
        setIsLoading(false);
      }
    };
    run();
  }, [slug]);

  if (!isLoading && !post) {
    return (
      <section className="mx-auto max-w-measure py-16" aria-labelledby="share-error-heading">
        <div className="card-editorial p-10 text-center">
          <h1
            id="share-error-heading"
            className="font-display text-2xl font-semibold tracking-tight text-ink-950 dark:text-ink-50"
          >
            {loadError === 'not_found' ? 'Blog not found' : 'Unable to load blog'}
          </h1>
          <p className="mt-3 text-ink-600 dark:text-ink-400">
            {loadError === 'not_found'
              ? 'This shared link is invalid or the post is not publicly available.'
              : 'There was a problem reaching the server. Please try again later.'}
          </p>
        </div>
      </section>
    );
  }

  return (
    // Shared reading view: 1200px frame, content centered per the share spec.
    <section className="mx-auto max-w-shared">
      <div className="mb-8 flex items-center justify-between gap-3">
        <span className="eyebrow">Shared article</span>
        <span className="chip">AI generated</span>
      </div>

      <div className="rule mb-8" />

      <div className="mx-auto max-w-measure">
        <BlogViewer blogPost={post} isLoading={isLoading} />
      </div>
    </section>
  );
}
