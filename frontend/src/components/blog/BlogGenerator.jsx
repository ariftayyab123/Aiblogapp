/**
 * Blog Generator component - main form for generating blog posts.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronDownIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { usePersonas } from '../../hooks/usePersonas';
import { useBlogGeneration, GENERATION_STAGES } from '../../hooks/useBlogGeneration';
import { Button } from '../ui/Button';

const personaDescriptions = {
  technical: {
    name: 'Technical Writer',
    description: 'Precise, jargon-appropriate, citation-heavy',
  },
  narrative: {
    name: 'Storyteller',
    description: 'Narrative-driven, emotional hooks',
  },
  analyst: {
    name: 'Industry Analyst',
    description: 'Data-focused, trend-aware',
  },
  educator: {
    name: 'Educator',
    description: 'Explanatory, structured, beginner-friendly',
  },
};

/** Numbered section label — the Swiss grid device used throughout the form. */
function FieldLabel({ index, children, htmlFor }) {
  return (
    <label htmlFor={htmlFor} className="flex items-baseline gap-3">
      <span className="font-display text-sm text-accent-600 dark:text-accent-400">{index}</span>
      <span className="eyebrow">{children}</span>
    </label>
  );
}

export default function BlogGenerator() {
  const navigate = useNavigate();
  const { personas, isLoading: personasLoading } = usePersonas();
  const { state, generateBlog, cancelGeneration, retryLastJob } = useBlogGeneration();
  const personaList = Array.isArray(personas) ? personas : [];

  const [topic, setTopic] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('technical');
  const [speed, setSpeed] = useState('fast');
  const lengthHint =
    speed === 'normal'
      ? 'Detailed mode usually takes longer (higher quality, longer output).'
      : 'Brief mode is faster and returns a concise, quick-read version.';

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (topic.trim().length < 5) {
      return;
    }

    const blogPostId = await generateBlog(topic, selectedPersona, speed);

    if (blogPostId) {
      const { encryptBlogId } = await import('../../utils/blogIdCrypto');
      navigate(`/blog/${encryptBlogId(blogPostId)}`);
    }
  };

  const isLoading = state.isGenerating || personasLoading;
  const topicError = topic.length > 0 && topic.length < 5;

  return (
    <section className="card-editorial p-6 md:p-8">
      <header className="border-b border-ink-200 pb-5 dark:border-ink-800">
        <h2 className="font-display text-2xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
          Draft a new post
        </h2>
        <p className="mt-1.5 text-sm text-ink-600 dark:text-ink-400">
          Written by Claude from your topic and chosen style. Every draft is
          machine-generated and yours to edit before publishing.
        </p>
      </header>

      <form onSubmit={handleSubmit} className="mt-7 space-y-8">
        {/* 01 — Topic */}
        <div className="space-y-3">
          <FieldLabel index="01" htmlFor="blog-topic">
            Topic
          </FieldLabel>
          <textarea
            id="blog-topic"
            rows={5}
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={isLoading}
            required
            aria-invalid={topicError || undefined}
            aria-describedby={topicError ? 'blog-topic-error' : undefined}
            placeholder="e.g., The future of renewable energy in developing countries..."
            className={`input-editorial resize-y leading-relaxed disabled:opacity-60 ${
              topicError ? 'border-red-500 focus:border-red-500 dark:border-red-500' : ''
            }`}
          />
          {topicError && (
            <p id="blog-topic-error" className="text-sm text-red-600 dark:text-red-400">
              Topic must be at least 5 characters
            </p>
          )}
        </div>

        {/* 02 — Writing style */}
        <fieldset className="space-y-3" disabled={isLoading}>
          <legend className="sr-only">Writing style</legend>
          <FieldLabel index="02">Writing style</FieldLabel>
          <div className="grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-ink-200 bg-ink-200 sm:grid-cols-2 dark:border-ink-800 dark:bg-ink-800">
            {Object.entries(personaDescriptions).map(([slug, desc]) => {
              const persona = personaList.find((p) => p.slug === slug);
              if (!persona) return null;

              const isSelected = selectedPersona === slug;

              return (
                <button
                  key={slug}
                  type="button"
                  onClick={() => setSelectedPersona(slug)}
                  disabled={isLoading}
                  aria-pressed={isSelected}
                  className={`relative cursor-pointer p-4 text-left transition-colors duration-200 disabled:cursor-not-allowed disabled:opacity-60 ${
                    isSelected
                      ? 'bg-ink-900 text-white dark:bg-ink-50 dark:text-ink-950'
                      : 'bg-white text-ink-950 hover:bg-ink-100 dark:bg-ink-900 dark:text-ink-50 dark:hover:bg-ink-800'
                  }`}
                >
                  {isSelected && (
                    <span
                      aria-hidden="true"
                      className="absolute right-0 top-0 h-full w-1 bg-accent-500"
                    />
                  )}
                  <span className="block font-medium">{desc.name}</span>
                  <span
                    className={`mt-1 block text-sm ${
                      isSelected
                        ? 'text-ink-300 dark:text-ink-600'
                        : 'text-ink-600 dark:text-ink-400'
                    }`}
                  >
                    {desc.description}
                  </span>
                </button>
              );
            })}
          </div>
        </fieldset>

        {/* 03 — Length + submit */}
        <div className="space-y-3">
          <FieldLabel index="03" htmlFor="blog-length">
            Length
          </FieldLabel>
          <div className="flex flex-col gap-4 md:flex-row md:items-start">
            <div className="md:w-56">
              <div className="relative">
                <select
                  id="blog-length"
                  value={speed}
                  onChange={(e) => setSpeed(e.target.value)}
                  disabled={isLoading}
                  className="input-editorial cursor-pointer appearance-none pr-10 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  <option value="fast">Brief (quick read)</option>
                  <option value="normal">Detailed (in-depth)</option>
                </select>
                <ChevronDownIcon
                  aria-hidden="true"
                  className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-500"
                />
              </div>
              <p className="mt-2 text-xs leading-relaxed text-ink-600 dark:text-ink-400">
                {lengthHint}
              </p>
            </div>

            <div className="flex flex-1 flex-col gap-3 sm:flex-row">
              <Button
                type="submit"
                variant="ink"
                size="lg"
                isLoading={isLoading}
                disabled={topic.trim().length < 5 || isLoading}
                className="flex flex-1 items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>Generating...</>
                ) : (
                  <>
                    <SparklesIcon aria-hidden="true" className="h-5 w-5" />
                    Generate draft
                  </>
                )}
              </Button>
              {state.isGenerating && (
                <Button type="button" variant="quiet" size="lg" onClick={cancelGeneration}>
                  Cancel
                </Button>
              )}
              {!state.isGenerating && state.currentStage === 'error' && state.jobId && (
                <Button type="button" variant="quiet" size="lg" onClick={retryLastJob}>
                  Retry
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Staged progress — never a bare spinner. */}
        {state.isGenerating && (
          <div
            role="status"
            aria-live="polite"
            className="border-t border-ink-200 pt-5 dark:border-ink-800"
          >
            <div className="mb-2 flex items-baseline justify-between">
              <span className="text-sm font-medium text-ink-950 dark:text-ink-50">
                {GENERATION_STAGES[state.currentStage]}
              </span>
              <span className="font-display text-sm text-ink-600 dark:text-ink-400">
                {state.progress}%
              </span>
            </div>
            <div className="h-1 w-full overflow-hidden bg-ink-200 dark:bg-ink-800">
              <div
                className="h-1 bg-accent-500 transition-[width] duration-300 ease-out"
                style={{ width: `${state.progress}%` }}
              />
            </div>
          </div>
        )}
      </form>
    </section>
  );
}
