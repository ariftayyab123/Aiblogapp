/**
 * Engagement Bar component - like/dislike buttons with counts.
 */
import { HandThumbUpIcon, HandThumbDownIcon } from '@heroicons/react/24/outline';
import { HandThumbUpIcon as HandThumbUpSolid, HandThumbDownIcon as HandThumbDownSolid } from '@heroicons/react/24/solid';

const baseButton = 'btn inline-flex items-center gap-2 px-4 py-2 text-sm';
const selected = {
  like: 'border border-emerald-600 bg-emerald-50 text-emerald-800 dark:border-emerald-500 dark:bg-emerald-950/40 dark:text-emerald-300',
  dislike: 'border border-red-600 bg-red-50 text-red-800 dark:border-red-500 dark:bg-red-950/40 dark:text-red-300',
};

export default function EngagementBar({ likes, dislikes, userAction, onLike, onDislike, isLoading }) {
  const totalReactions = (likes || 0) + (dislikes || 0);
  // Counts stay hidden until there are enough of them to mean anything.
  const showCounts = totalReactions >= 5;

  return (
    <div className="card-editorial flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="text-sm font-medium text-ink-900 dark:text-ink-100">Was this article helpful?</p>
        {!showCounts && (
          <p className="mt-1 text-xs text-ink-500 dark:text-ink-400">
            Be among the first to rate this article.
          </p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onLike}
          disabled={isLoading}
          aria-pressed={userAction === 'like'}
          className={`${baseButton} ${userAction === 'like' ? selected.like : 'btn-quiet'}`}
        >
          {userAction === 'like' ? (
            <HandThumbUpSolid className="h-5 w-5" aria-hidden="true" />
          ) : (
            <HandThumbUpIcon className="h-5 w-5" aria-hidden="true" />
          )}
          <span className="font-medium">Helpful</span>
          {showCounts && <span className="font-medium tabular-nums">{likes}</span>}
        </button>

        <button
          type="button"
          onClick={onDislike}
          disabled={isLoading}
          aria-pressed={userAction === 'dislike'}
          className={`${baseButton} ${userAction === 'dislike' ? selected.dislike : 'btn-quiet'}`}
        >
          {userAction === 'dislike' ? (
            <HandThumbDownSolid className="h-5 w-5" aria-hidden="true" />
          ) : (
            <HandThumbDownIcon className="h-5 w-5" aria-hidden="true" />
          )}
          <span className="font-medium">Not helpful</span>
          {showCounts && <span className="font-medium tabular-nums">{dislikes}</span>}
        </button>
      </div>
    </div>
  );
}
