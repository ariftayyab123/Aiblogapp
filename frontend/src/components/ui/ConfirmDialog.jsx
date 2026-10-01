/**
 * ConfirmDialog - lightweight, accessible confirmation modal.
 * Used for destructive actions like deleting a blog post.
 */
import { useEffect } from 'react';
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmText = 'Delete',
  cancelText = 'Cancel',
  danger = true,
  isConfirming = false,
  onConfirm,
  onCancel,
}) {
  // Escape closes the dialog, except while the action is in flight.
  useEffect(() => {
    if (!open || isConfirming) return undefined;

    const onKeyDown = (event) => {
      if (event.key === 'Escape') onCancel?.();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [open, isConfirming, onCancel]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-overlay flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-label={title}
    >
      <div className="scrim" onClick={isConfirming ? undefined : onCancel} />
      <div className="card-editorial relative w-full max-w-md p-6 shadow-e-xl">
        <button
          type="button"
          onClick={onCancel}
          disabled={isConfirming}
          aria-label="Close"
          className="icon-btn absolute right-3 top-3 h-9 w-9"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>

        <div className="flex items-start gap-4">
          <div
            className={`flex-shrink-0 rounded-full border p-2 ${
              danger
                ? 'border-red-200 text-red-600 dark:border-red-900 dark:text-red-400'
                : 'border-ink-200 text-ink-800 dark:border-ink-700 dark:text-ink-200'
            }`}
          >
            <ExclamationTriangleIcon className="h-6 w-6" aria-hidden="true" />
          </div>
          <div className="min-w-0 pr-8">
            <h3 className="font-display text-lg font-semibold tracking-tight text-ink-950 dark:text-ink-50">
              {title}
            </h3>
            {message && (
              <p className="mt-1.5 text-sm text-ink-600 dark:text-ink-400">{message}</p>
            )}
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={isConfirming}
            className="btn btn-quiet"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isConfirming}
            className={`btn ${danger ? 'btn-danger' : 'btn-ink'}`}
          >
            {isConfirming ? `${confirmText}...` : confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
