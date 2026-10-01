/**
 * Button component with variants.
 */
import { forwardRef } from 'react';

const buttonStyles = {
  ink: 'btn-ink',
  accent: 'btn-accent',
  quiet: 'btn-quiet',
  danger: 'btn-danger',
  'danger-quiet': 'btn-danger-quiet',
};

const buttonSizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button = forwardRef(
  (
    {
      variant = 'ink',
      size = 'md',
      isLoading = false,
      disabled,
      children,
      className = '',
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={`btn inline-flex items-center justify-center gap-2 ${
          buttonStyles[variant] || buttonStyles.ink
        } ${buttonSizes[size]} ${isLoading ? 'cursor-wait' : ''} ${className}`}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="spinner h-4 w-4" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            {children}
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
