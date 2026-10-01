/**
 * Input component with label support.
 */
import { forwardRef, useId } from 'react';

const errorRing = 'border-red-600 focus:border-red-600 dark:border-red-500 dark:focus:border-red-500';

export const Input = forwardRef(
  ({ label, error, className = '', id, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={inputId} className="field-label">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          className={`input-editorial ${error ? errorRing : ''} ${className}`}
          {...props}
        />
        {error && (
          <p id={errorId} className="mt-1.5 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export const Textarea = forwardRef(
  ({ label, error, className = '', rows = 4, id, ...props }, ref) => {
    const generatedId = useId();
    const textareaId = id || generatedId;
    const errorId = `${textareaId}-error`;

    return (
      <div className="w-full">
        {label && (
          <label htmlFor={textareaId} className="field-label">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={textareaId}
          rows={rows}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? errorId : undefined}
          className={`input-editorial ${error ? errorRing : ''} ${className}`}
          {...props}
        />
        {error && (
          <p id={errorId} className="mt-1.5 text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = 'Textarea';
