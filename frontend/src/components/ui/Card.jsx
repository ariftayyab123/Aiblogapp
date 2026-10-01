/**
 * Card component for content containers.
 *
 * Hairline border, flat surface — the editorial system uses rules rather than
 * shadows to separate content. Pass `interactive` for cards that are clickable.
 */
export function Card({ children, className = '', interactive = false, ...props }) {
  return (
    <div
      className={`card-editorial p-6 ${
        interactive
          ? 'cursor-pointer hover:border-ink-400 dark:hover:border-ink-600'
          : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className = '' }) {
  return (
    <div className={`mb-4 ${className}`}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className = '' }) {
  return (
    <h3 className={`font-display text-xl font-semibold tracking-tight text-ink-950 dark:text-ink-50 ${className}`}>
      {children}
    </h3>
  );
}

export function CardContent({ children, className = '' }) {
  return (
    <div className={className}>
      {children}
    </div>
  );
}
