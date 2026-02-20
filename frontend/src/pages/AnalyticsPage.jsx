/**
 * Analytics Page - displays overall statistics.
 */
import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { analyticsApi } from '../services/api';
import {
  DocumentTextIcon,
  HeartIcon,
  HandThumbDownIcon,
  UserGroupIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { encryptBlogId } from '../utils/blogIdCrypto';

function AnalyticsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [sortBy, setSortBy] = useState('total_reactions');
  const [sortOrder, setSortOrder] = useState('desc');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await analyticsApi.get({
          sort:
            sortBy === 'total_reactions'
              ? 'reactions'
              : sortBy === 'sentiment_score'
                ? 'sentiment'
                : sortBy,
          order: sortOrder,
          limit: 20,
          from: fromDate || undefined,
          to: toDate || undefined,
        });
        setData(response.data);
        setLoadError('');
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
        setLoadError(err?.message || 'Failed to load analytics');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [sortBy, sortOrder, fromDate, toDate]);

  const stats = data || {
    total_posts: 0,
    total_engagements: 0,
    total_likes: 0,
    total_dislikes: 0,
    reaction_rate: 0,
    avg_sentiment_score: 0,
    top_posts: [],
  };

  const avgSentiment = Number.isFinite(Number(stats.avg_sentiment_score))
    ? Number(stats.avg_sentiment_score)
    : 0;

  const sortedPosts = useMemo(() => {
    const posts = [...(stats.top_posts || [])];
    posts.sort((a, b) => {
      const left = Number(a[sortBy] ?? 0);
      const right = Number(b[sortBy] ?? 0);
      return sortOrder === 'asc' ? left - right : right - left;
    });
    return posts;
  }, [stats.top_posts, sortBy, sortOrder]);

  const maxReactions = useMemo(() => {
    if (!sortedPosts.length) return 1;
    return Math.max(...sortedPosts.map((post) => post.total_reactions || 0), 1);
  }, [sortedPosts]);

  if (isLoading) {
    return (
      <div className="grid md:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
        Analytics Dashboard
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-4 md:gap-6">
        <StatCard title="Total Posts" value={stats.total_posts} icon={DocumentTextIcon} color="blue" />
        <StatCard title="Total Likes" value={stats.total_likes} icon={HeartIcon} color="green" />
        <StatCard title="Total Dislikes" value={stats.total_dislikes} icon={HandThumbDownIcon} color="red" />
        <StatCard title="Reaction Rate" value={stats.reaction_rate} icon={UserGroupIcon} color="indigo" />
        <StatCard
          title="Avg Sentiment"
          value={avgSentiment.toFixed(1)}
          icon={ArrowTrendingUpIcon}
          color="orange"
        />
      </div>

      {sortedPosts.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
              <CardTitle>Top Performing Posts</CardTitle>
              <div className="flex items-center gap-2">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm"
                >
                  <option value="total_reactions">Sort: Reactions</option>
                  <option value="likes">Sort: Likes</option>
                  <option value="dislikes">Sort: Dislikes</option>
                  <option value="sentiment_score">Sort: Sentiment</option>
                </select>
                <button
                  onClick={() => setSortOrder((prev) => (prev === 'desc' ? 'asc' : 'desc'))}
                  className="px-3 py-2 text-sm rounded-md border border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {sortOrder === 'desc' ? 'High to Low' : 'Low to High'}
                </button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sortedPosts.map((post, index) => (
                <button
                  key={post.id}
                  onClick={() => navigate(`/blog/${encryptBlogId(post.id)}`)}
                  className="w-full text-left p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                        <h4 className="font-medium text-gray-900 dark:text-white truncate">
                          {post.title}
                        </h4>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        {post.persona && `${post.persona} | `}
                        {new Date(post.created_at).toLocaleDateString()}
                      </p>

                      <div className="mt-3 space-y-2">
                        <MetricBar
                          label="Likes"
                          value={post.likes || 0}
                          max={maxReactions}
                          color="bg-green-500"
                        />
                        <MetricBar
                          label="Dislikes"
                          value={post.dislikes || 0}
                          max={maxReactions}
                          color="bg-red-500"
                        />
                      </div>
                    </div>

                    <div className="text-right shrink-0">
                      <div
                        className={`text-lg font-semibold ${
                          post.sentiment_score >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}
                      >
                        {post.sentiment_score > 0 ? '+' : ''}
                        {post.sentiment_score}
                      </div>
                      <div className="text-xs text-gray-500">sentiment</div>
                      <div className="mt-2 text-sm font-medium text-gray-800 dark:text-gray-200">
                        {post.total_reactions || 0} reactions
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {loadError && (
        <Card>
          <CardContent>
            <p className="text-sm text-red-600 dark:text-red-400">
              {loadError}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default AnalyticsPage;

function MetricBar({ label, value, max, color }) {
  const width = Math.min(100, (value / max) * 100);

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs w-14 text-gray-600 dark:text-gray-400">{label}</span>
      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-600 rounded">
        <div className={`h-2 rounded ${color}`} style={{ width: `${width}%` }} />
      </div>
      <span className="text-xs w-8 text-right text-gray-700 dark:text-gray-300">{value}</span>
    </div>
  );
}

function StatCard({ title, value, icon: Icon, color }) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    red: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
    orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400',
  };

  return (
    <Card>
      <CardContent>
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 truncate">{title}</p>
            <p className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mt-1 break-words leading-tight">
              {value}
            </p>
          </div>
          <div className={`p-2 sm:p-3 rounded-lg shrink-0 ${colors[color]}`}>
            <Icon className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
