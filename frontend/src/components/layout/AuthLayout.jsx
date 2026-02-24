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
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-primary-700 text-white px-4 py-8 md:px-8 md:py-10">
      <div className="max-w-7xl mx-auto min-h-[calc(100vh-4rem)] grid lg:grid-cols-2 rounded-3xl overflow-hidden border border-white/10 shadow-2xl">
        <section className="p-8 md:p-12 lg:p-14 bg-gradient-to-br from-primary-950/80 to-primary-900/80 flex flex-col justify-between">
          <div>
            <span className="inline-flex items-center rounded-full bg-white/10 px-4 py-2 text-xs tracking-[0.14em] uppercase font-semibold text-primary-100">
              AI Blog Generator
            </span>
            <div className="mt-8 flex items-center gap-3">
              <img
                src="/ai-blog-icon.svg"
                alt="AI Blog Generator logo"
                className="w-12 h-12 md:w-14 md:h-14 rounded-xl shadow-lg"
              />
              <p className="text-xl md:text-2xl font-semibold text-white">AI Blog Generator</p>
            </div>
            <h1 className="mt-6 text-4xl md:text-5xl font-bold leading-tight">{heroTitle}</h1>
            <p className="mt-6 text-primary-100/90 text-lg max-w-xl">{heroDescription}</p>
            <div className="mt-8 inline-flex items-center rounded-full bg-white/10 px-4 py-2 text-sm text-primary-100">
              Guided AI writing with citations and analytics
            </div>
          </div>

          <div className="mt-10 space-y-4 text-primary-100/90">
            {featurePoints.map((point) => (
              <div key={point} className="flex items-center gap-3">
                 <span>{point}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="p-8 md:p-12 lg:p-14 bg-gradient-to-b from-primary-900/80 to-primary-950/90 flex items-center justify-center">
          <div className="w-full max-w-xl rounded-3xl border border-white/10 bg-primary-950/60 backdrop-blur-md shadow-2xl p-7 md:p-9">
            <h2 className="text-3xl font-bold text-center text-white">{formTitle}</h2>
            <p className="mt-3 text-center text-primary-100/80">{formDescription}</p>

            {children}

            {footer && <div className="mt-6 text-sm text-primary-100/80 text-center">{footer}</div>}
          </div>
        </section>
      </div>
    </div>
  );
}
