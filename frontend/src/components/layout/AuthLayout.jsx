/**
 * Auth layout - editorial title page: statement column + form column.
 */
export default function AuthLayout({
  heroTitle,
  heroDescription,
  featurePoints = [],
  formTitle,
  formDescription,
  footer,
  children,
}) {
  return (
    <div className="min-h-screen bg-paper px-4 py-10 md:px-8 md:py-14 lg:flex lg:items-center dark:bg-ink-950">
      <div className="mx-auto grid w-full max-w-6xl gap-x-12 gap-y-14 lg:grid-cols-12">
        {/* Statement column */}
        <section className="lg:col-span-6 xl:col-span-5">
          <div className="border-t-2 border-ink-950 pt-4 dark:border-ink-50">
            <span className="eyebrow">AI Blog Generator</span>
          </div>

          <div className="mt-8 flex items-center gap-3">
            <img
              src="/ai-blog-icon.svg"
              alt=""
              aria-hidden="true"
              className="h-11 w-11 rounded-lg ring-1 ring-ink-900/10 dark:ring-ink-50/10"
            />
            <span className="font-display text-xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
              Blog Generator
            </span>
          </div>

          <h1 className="mt-8 font-display text-[2rem] font-semibold leading-[1.12] tracking-tight text-ink-950 sm:text-[2.75rem] dark:text-ink-50">
            {heroTitle}
            <span className="text-accent-500">.</span>
          </h1>

          <p className="mt-5 max-w-prose leading-relaxed text-ink-700 dark:text-ink-300">
            {heroDescription}
          </p>

          {featurePoints.length > 0 && (
            <ul className="mt-10">
              {featurePoints.map((point, index) => (
                <li key={point} className="rule flex gap-4 py-4">
                  <span className="font-display text-sm text-accent-600 dark:text-accent-400">
                    {String(index + 1).padStart(2, '0')}
                  </span>
                  <span className="text-sm leading-relaxed text-ink-700 dark:text-ink-300">
                    {point}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Form column */}
        <section className="lg:col-span-6 lg:border-l lg:border-ink-200 lg:pl-12 xl:col-span-6 xl:col-start-7 dark:lg:border-ink-800">
          <div className="mx-auto w-full max-w-md lg:pt-4">
            <h2 className="font-display text-2xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
              {formTitle}
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-ink-600 dark:text-ink-400">
              {formDescription}
            </p>

            {children}

            {footer && (
              <div className="mt-7 border-t border-ink-200 pt-5 text-sm text-ink-600 dark:border-ink-800 dark:text-ink-400">
                {footer}
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
