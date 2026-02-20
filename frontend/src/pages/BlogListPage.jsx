/**
 * Blog List Page - displays all generated blog posts.
 */
import { useBlogPosts } from '../hooks/useBlogPosts';
import BlogCard from '../components/blog/BlogCard';
import { useState } from 'react';

export default function BlogListPage() {
  const [filter, setFilter] = useState('completed');
  const { posts, isLoading } = useBlogPosts({ status: filter });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Blog Posts
        </h1>

        {/* Filter */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setFilter('completed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'completed'
                ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
            }`}
          >
            All
          </button>
        </div>
      </div>

      {/* Posts Grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded-lg" />
            </div>
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 dark:text-gray-400">
            No blog posts found. Generate your first one!
          </p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {posts.map(post => (
            <BlogCard key={post.id} blogPost={post} />
          ))}
        </div>
      )}
    </div>
  );
}
