/**
 * Home Page - editorial masthead with the blog generator as the working column.
 */
import {
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  PencilSquareIcon,
} from '@heroicons/react/24/outline';
import BlogGenerator from '../components/blog/BlogGenerator';

const capabilities = [
  {
    icon: DocumentTextIcon,
    title: 'Sourced by default',
    description:
      'Citations and references are collected alongside the draft, so every claim stays traceable.',
  },
  {
    icon: PencilSquareIcon,
    title: 'Editable drafts',
    description:
      'Nothing publishes itself. Each draft opens in an editor for you to revise, cut, or rewrite.',
  },
  {
    icon: ChatBubbleLeftRightIcon,
    title: 'Reader signals',
    description:
      'Likes, dislikes and engagement rates roll up per post so you can see what actually lands.',
  },
];

export default function HomePage() {
  return (
    <div className="mx-auto max-w-measure">
      {/* Masthead */}
      <header className="border-t-2 border-ink-950 pt-4 dark:border-ink-50">
        <div className="flex items-baseline justify-between gap-4">
          <span className="eyebrow">AI Blog Generator</span>
          <span className="eyebrow hidden sm:inline">Draft · Cite · Measure</span>
        </div>

        <div className="mt-8 grid grid-cols-12 gap-x-4 gap-y-6">
          <h1 className="col-span-12 font-display text-[2.25rem] font-semibold leading-[1.1] tracking-tight text-ink-950 sm:text-5xl lg:col-span-9 dark:text-ink-50">
            Turn a topic into a sourced draft
            <span className="text-accent-500">.</span>
          </h1>
          <p className="col-span-12 max-w-prose text-base leading-relaxed text-ink-700 lg:col-span-9 dark:text-ink-300">
            Choose a writing voice, describe what you want covered, and get back a
            structured draft with its references attached — ready to edit, publish,
            and track.
          </p>
        </div>
      </header>

      {/* Working column */}
      <div className="mt-10">
        <BlogGenerator />
      </div>

      {/* Capabilities */}
      <section className="mt-14" aria-labelledby="capabilities-heading">
        <h2 id="capabilities-heading" className="eyebrow">
          What you get
        </h2>
        <div className="mt-5 grid grid-cols-12 gap-x-4 gap-y-8">
          {capabilities.map(({ icon: Icon, title, description }) => (
            <div key={title} className="col-span-12 sm:col-span-4">
              <div className="rule pt-4">
                <Icon
                  aria-hidden="true"
                  className="h-5 w-5 text-ink-950 dark:text-ink-50"
                  strokeWidth={1.5}
                />
                <h3 className="mt-3 font-display text-base font-semibold text-ink-950 dark:text-ink-50">
                  {title}
                </h3>
                <p className="mt-1.5 text-sm leading-relaxed text-ink-600 dark:text-ink-400">
                  {description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
