/**
 * Engagement Bar component - like/dislike buttons with counts.
 */
import { HandThumbUpIcon, HandThumbDownIcon } from '@heroicons/react/24/outline';
import { HandThumbUpIcon as HandThumbUpSolid, HandThumbDownIcon as HandThumbDownSolid } from '@heroicons/react/24/solid';

export default function EngagementBar({ likes, dislikes, userAction, onLike, onDislike, isLoading }) {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg">
      <div className="text-sm text-gray-600 dark:text-gray-400">
        Was this article helpful?
      </div>

      <div className="flex items-center gap-3">
        {/* Like Button */}
        <button
          onClick={onLike}
          disabled={isLoading}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            userAction === 'like'
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
              : 'bg-white dark:bg-gray-700 text-gray-600 hover:bg-green-50 dark:hover:bg-green-900/20 dark:text-gray-400'
          }`}
        >
          {userAction === 'like' ? (
            <HandThumbUpSolid className="w-5 h-5" />
          ) : (
            <HandThumbUpIcon className="w-5 h-5" />
          )}
          <span className="font-medium">{likes}</span>
        </button>

        {/* Dislike Button */}
        <button
          onClick={onDislike}
          disabled={isLoading}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
            userAction === 'dislike'
              ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
              : 'bg-white dark:bg-gray-700 text-gray-600 hover:bg-red-50 dark:hover:bg-red-900/20 dark:text-gray-400'
          }`}
        >
          {userAction === 'dislike' ? (
            <HandThumbDownSolid className="w-5 h-5" />
          ) : (
            <HandThumbDownIcon className="w-5 h-5" />
          )}
          <span className="font-medium">{dislikes}</span>
        </button>
      </div>
    </div>
  );
}
