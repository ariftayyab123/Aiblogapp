/**
 * Analytics Page - displays overall statistics.
 *
 * 1400px frame, dense metric band, hairline rows per the analytics spec.
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
  ChevronDownIcon,
  ArrowPathIcon,
  BarsArrowDownIcon,
  BarsArrowUpIcon,
} from '@heroicons/react/24/outline';
import { encryptBlogId } from '../utils/blogIdCrypto';

const SORT_OPTIONS = [
  { value: 'recent', label: 'Recent' },
  { value: 'helpful', label: 'Helpful' },
  { value: 'needs_improvement', label: 'Needs improvement' },
  { value: 'helpfulness_score', label: 'Helpfulness score' },
];

function AnalyticsPage() {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [sortOrder, setSortOrder] = useState('desc');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [refreshNonce, setRefreshNonce] = useState(0);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const sortParamMap = {
          recent: 'sentiment',
          helpful: 'likes',
          needs_improvement: 'dislikes',
          helpfulness_score: 'sentiment',
        };

        const response = await analyticsApi.get({
          sort: sortParamMap[sortBy] || 'sentiment',
          order: sortOrder,
          limit: 20,
          from: fromDate || undefined,
          to: toDate || undefined,
          refresh: refreshNonce || undefined,
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
  }, [sortBy, sortOrder, fromDate, toDate, refreshNonce]);

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
    const sortKeyMap = {
      recent: 'created_at',
      helpful: 'likes',
      needs_improvement: 'dislikes',
      helpfulness_score: 'sentiment_score',
    };

    const sortKey = sortKeyMap[sortBy] || 'created_at';

    posts.sort((a, b) => {
      if (sortKey === 'created_at') {
        const left = new Date(a.created_at || 0).getTime() || 0;
        const right = new Date(b.created_at || 0).getTime() || 0;
        return sortOrder === 'asc' ? left - right : right - left;
      }

      const left = Number(a[sortKey] ?? 0);
      const right = Number(b[sortKey] ?? 0);
      return sortOrder === 'asc' ? left - right : right - left;
    });
    return posts;
  }, [stats.top_posts, sortBy, sortOrder]);

  const maxReactions = useMemo(() => {
    if (!sortedPosts.length) return 1;
    return Math.max(...sortedPosts.map((post) => post.total_reactions || 0), 1);
  }, [sortedPosts]);

  return (
    <div className="mx-auto max-w-wide space-y-8">
      <header>
        <p className="eyebrow">Reporting</p>
        <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
          Analytics Dashboard
        </h1>
      </header>

      {/* Metric band */}
      {isLoading ? (
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-5" aria-busy="true" aria-label="Loading analytics">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="card-editorial space-y-3 p-5">
              <div className="skeleton h-3 w-20" />
              <div className="skeleton h-8 w-16" />
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4 xl:grid-cols-5">
          <StatCard title="Total posts" value={stats.total_posts} icon={DocumentTextIcon} />
          <StatCard title="Total helpful" value={stats.total_likes} icon={HeartIcon} />
          <StatCard title="Needs improvement" value={stats.total_dislikes} icon={HandThumbDownIcon} />
          <StatCard title="Feedback rate" value={stats.reaction_rate} icon={UserGroupIcon} />
          <StatCard
            title="Helpfulness score"
            value={avgSentiment.toFixed(1)}
            icon={ArrowTrendingUpIcon}
          />
        </div>
      )}

      {/* Controls */}
      <section className="card-editorial p-5" aria-label="Filters">
        <div className="grid gap-4 md:grid-cols-12 md:items-end">
          <div className="md:col-span-3">
            <label htmlFor="analytics-sort" className="field-label">Sort by</label>
            <div className="relative">
              <select
                id="analytics-sort"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="select-editorial"
              >
                {SORT_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
              <ChevronDownIcon
                className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500"
                aria-hidden="true"
              />
            </div>
          </div>

          <div className="md:col-span-3">
            <label htmlFor="analytics-from" className="field-label">From</label>
            <input
              id="analytics-from"
              type="date"
              value={fromDate}
              max={toDate || undefined}
              onChange={(e) => setFromDate(e.target.value)}
              className="input-editorial py-2.5 text-sm"
            />
          </div>

          <div className="md:col-span-3">
            <label htmlFor="analytics-to" className="field-label">To</label>
            <input
              id="analytics-to"
              type="date"
              value={toDate}
              min={fromDate || undefined}
              onChange={(e) => setToDate(e.target.value)}
              className="input-editorial py-2.5 text-sm"
            />
          </div>

          <div className="flex items-center gap-2 md:col-span-3 md:justify-end">
            <button
              type="button"
              onClick={() => setSortOrder((prev) => (prev === 'desc' ? 'asc' : 'desc'))}
              title={sortOrder === 'desc' ? 'Currently high to low' : 'Currently low to high'}
              className="btn btn-quiet inline-flex items-center gap-1.5 px-3 py-2.5 text-sm"
            >
              {sortOrder === 'desc' ? (
                <BarsArrowDownIcon className="h-4 w-4" aria-hidden="true" />
              ) : (
                <BarsArrowUpIcon className="h-4 w-4" aria-hidden="true" />
              )}
              {sortOrder === 'desc' ? 'High to low' : 'Low to high'}
            </button>
            <button
              type="button"
              onClick={() => setRefreshNonce(Date.now())}
              title="Bypass the cached report and refetch"
              className="btn btn-quiet inline-flex items-center gap-1.5 px-3 py-2.5 text-sm"
            >
              <ArrowPathIcon className="h-4 w-4" aria-hidden="true" />
              Refresh
            </button>
          </div>
        </div>
      </section>

      {loadError && (
        <div className="card-editorial border-l-2 border-l-red-600 p-5">
          <p className="text-sm font-medium text-red-700 dark:text-red-400">{loadError}</p>
        </div>
      )}

      {/* Top performing posts */}
      {!isLoading && (
        <section aria-labelledby="top-posts-heading" className="space-y-4">
          <div className="flex items-baseline justify-between gap-3">
            <h2
              id="top-posts-heading"
              className="font-display text-xl font-semibold tracking-tight text-ink-950 dark:text-ink-50"
            >
              Top Performing Posts
            </h2>
            <span className="eyebrow">{sortedPosts.length} shown</span>
          </div>

          {sortedPosts.length === 0 ? (
            <div className="card-editorial p-8 text-center text-ink-600 dark:text-ink-400">
              No feedback recorded in this range yet.
            </div>
          ) : (
            <ul className="border-b border-ink-200 dark:border-ink-800">
              {sortedPosts.map((post, index) => (
                <li key={post.id}>
                  <button
                    type="button"
                    onClick={() => navigate(`/blog/${encryptBlogId(post.id)}`)}
                    className="row-editorial"
                  >
                    <div className="grid gap-4 md:grid-cols-12 md:items-start">
                      <div className="min-w-0 md:col-span-9">
                        <div className="flex items-center gap-2">
                          <span className="eyebrow tabular-nums">#{index + 1}</span>
                          <h3 className="truncate font-medium text-ink-950 dark:text-ink-50">
                            {post.title}
                          </h3>
                        </div>
                        <p className="mt-1 text-sm text-ink-600 dark:text-ink-400">
                          {post.persona && `${post.persona} · `}
                          {new Date(post.created_at).toLocaleDateString()}
                        </p>

                        <div className="mt-3 max-w-md space-y-2">
                          <MetricBar
                            label="Helpful"
                            value={post.likes || 0}
                            max={maxReactions}
                            color="bg-emerald-500"
                          />
                          <MetricBar
                            label="Needs imp."
                            value={post.dislikes || 0}
                            max={maxReactions}
                            color="bg-red-500"
                          />
                        </div>
                      </div>

                      <div className="shrink-0 md:col-span-3 md:text-right">
                        <div
                          className={`metric text-2xl tabular-nums ${
                            post.sentiment_score >= 0
                              ? 'text-emerald-700 dark:text-emerald-400'
                              : 'text-red-700 dark:text-red-400'
                          }`}
                        >
                          {post.sentiment_score > 0 ? '+' : ''}
                          {post.sentiment_score}
                        </div>
                        <div className="eyebrow mt-1">Score</div>
                        <div className="mt-2 text-sm text-ink-700 dark:text-ink-300">
                          {post.total_reactions || 0} feedback responses
                        </div>
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}

export default AnalyticsPage;

function MetricBar({ label, value, max, color }) {
  const width = Math.min(100, (value / max) * 100);

  return (
    <div className="flex items-center gap-2" title={`${label}: ${value} of ${max}`}>
      <span className="w-16 shrink-0 text-xs text-ink-600 dark:text-ink-400">{label}</span>
      <div className="h-1.5 flex-1 rounded bg-ink-200 dark:bg-ink-800">
        <div
          className={`h-1.5 rounded transition-[width] duration-300 ${color}`}
          style={{ width: `${width}%` }}
        />
      </div>
      <span className="w-8 shrink-0 text-right text-xs tabular-nums text-ink-700 dark:text-ink-300">
        {value}
      </span>
    </div>
  );
}

function StatCard({ title, value, icon: Icon }) {
  return (
    <div className="card-editorial p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="eyebrow truncate" title={title}>{title}</p>
          <p className="metric mt-2 break-words tabular-nums">{value}</p>
        </div>
        <Icon className="h-5 w-5 shrink-0 text-ink-400 dark:text-ink-500" aria-hidden="true" />
      </div>
    </div>
  );
}
