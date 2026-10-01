/**
 * Toast notification component.
 */
import { useEffect, useState } from 'react';
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon, InformationCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const icons = {
  success: CheckCircleIcon,
  error: ExclamationCircleIcon,
  info: InformationCircleIcon,
  warning: ExclamationTriangleIcon,
};

/* Hairline surface for every toast; type is carried by the left edge and the
   icon colour, never by a tinted background. */
const edges = {
  success: 'border-l-emerald-500',
  error: 'border-l-red-600',
  info: 'border-l-ink-900 dark:border-l-ink-100',
  warning: 'border-l-amber-500',
};

const iconColors = {
  success: 'text-emerald-600 dark:text-emerald-400',
  error: 'text-red-600 dark:text-red-400',
  info: 'text-ink-700 dark:text-ink-300',
  warning: 'text-amber-600 dark:text-amber-500',
};

export default function Toast({ message, type = 'info', onClose }) {
  const [isExiting, setIsExiting] = useState(false);
  const Icon = icons[type] || InformationCircleIcon;

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsExiting(true);
    }, 4500);

    return () => clearTimeout(timer);
  }, []);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(onClose, 300);
  };

  return (
    <div
      role="status"
      className={`card-editorial flex max-w-md items-center gap-3 border-l-2 px-4 py-3 shadow-e-lg transition-all duration-300 ${
        edges[type] || edges.info
      } ${isExiting ? 'opacity-0 translate-x-full' : 'opacity-100 translate-x-0'}`}
    >
      <Icon className={`h-5 w-5 flex-shrink-0 ${iconColors[type] || iconColors.info}`} aria-hidden="true" />
      <p className="flex-1 text-sm font-medium text-ink-900 dark:text-ink-100">{message}</p>
      <button
        type="button"
        onClick={handleClose}
        aria-label="Dismiss notification"
        className="flex-shrink-0 cursor-pointer rounded p-1 text-ink-500 transition-colors duration-200 hover:bg-ink-100 hover:text-ink-950 dark:text-ink-400 dark:hover:bg-ink-800 dark:hover:text-ink-50"
      >
        <XMarkIcon className="h-4 w-4" />
      </button>
    </div>
  );
}
