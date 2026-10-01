/**
 * Badge component for status indicators.
 *
 * The editorial system marks status with a small dot beside its text label
 * rather than a coloured pill, so colour is never the only signal. Pass
 * `dot={false}` for plain metadata (a persona name, a word count).
 */
const dotStyles = {
  gray: 'bg-ink-400',
  green: 'bg-emerald-500',
  red: 'bg-red-600',
  blue: 'bg-sky-500',
  yellow: 'bg-amber-500',
};

export function Badge({ children, variant = 'gray', dot = true, className = '' }) {
  return (
    <span className={`chip ${className}`}>
      {dot && <span className={`status-dot ${dotStyles[variant] || dotStyles.gray}`} aria-hidden="true" />}
      {children}
    </span>
  );
}
