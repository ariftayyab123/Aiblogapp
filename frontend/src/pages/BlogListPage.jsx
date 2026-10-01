/**
 * Blog List Page - displays all generated blog posts.
 *
 * Single column capped at 800px per the blog-list spec (low density, one
 * decision per row).
 */
import { useBlogPosts } from '../hooks/useBlogPosts';
import BlogCard from '../components/blog/BlogCard';
import { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const FILTERS = [
  { value: 'completed', label: 'Completed' },
  { value: 'all', label: 'All' },
];

export default function BlogListPage() {
  const [filter, setFilter] = useState('completed');
  const listFilters = filter === 'all' ? {} : { status: filter };
  const { posts, isLoading, error, fetchPosts } = useBlogPosts(listFilters);
  const location = useLocation();

  useEffect(() => {
    if (location.state?.refresh) {
      fetchPosts();
    }
  }, [location.state?.refresh, fetchPosts]);

  return (
    <div className="mx-auto max-w-measure space-y-8">
      <header className="space-y-4">
        <div>
          <p className="eyebrow">Library</p>
          <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
            Blog Posts
          </h1>
        </div>

        {/* Segmented filter — hairline, one active state. */}
        <div
          role="group"
          aria-label="Filter posts by status"
          className="inline-flex rounded-lg border border-ink-200 p-0.5 dark:border-ink-800"
        >
          {FILTERS.map((option) => {
            const isActive = filter === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setFilter(option.value)}
                aria-pressed={isActive}
                className={`cursor-pointer rounded-md px-4 py-1.5 text-sm font-medium transition-colors duration-200 ${
                  isActive
                    ? 'bg-ink-900 text-white dark:bg-ink-50 dark:text-ink-950'
                    : 'text-ink-600 hover:text-ink-950 dark:text-ink-400 dark:hover:text-ink-50'
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </header>

      {isLoading ? (
        <div className="space-y-5" aria-busy="true" aria-label="Loading blog posts">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card-editorial space-y-3 p-6">
              <div className="skeleton h-4 w-24" />
              <div className="skeleton h-6 w-3/4" />
              <div className="skeleton h-4 w-full" />
              <div className="skeleton h-4 w-32" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="card-editorial p-8 text-center">
          <p className="font-medium text-red-700 dark:text-red-400">Failed to load blog posts.</p>
          <button type="button" onClick={fetchPosts} className="btn btn-quiet mt-4">
            Try again
          </button>
        </div>
      ) : posts.length === 0 ? (
        <div className="card-editorial space-y-4 p-10 text-center">
          <p className="text-ink-600 dark:text-ink-400">
            No blog posts yet. Generate your first one.
          </p>
          <Link to="/" className="btn btn-ink inline-flex">
            Generate a Blog Post
          </Link>
        </div>
      ) : (
        <div className="space-y-5">
          {posts.map((post) => (
            <BlogCard key={post.id} blogPost={post} />
          ))}
        </div>
      )}
    </div>
  );
}
