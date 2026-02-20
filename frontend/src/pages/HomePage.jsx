/**
 * Home Page - main landing with blog generator.
 */
import BlogGenerator from '../components/blog/BlogGenerator';

export default function HomePage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
          AI Blog Generator
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Generate authentic, engaging blog posts with AI-powered writing.
          Choose your style, enter a topic, and let AI do the rest.
        </p>
      </div>

      {/* Generator */}
      <BlogGenerator />

      {/* Features */}
      <div className="grid md:grid-cols-3 gap-6 mt-12">
        <div className="text-center p-6">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Authentic Sources</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Citations and references automatically included for credibility.
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Feedback Loop</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Track engagement with likes/dislikes to improve content quality.
          </p>
        </div>

        <div className="text-center p-6">
          <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mx-auto mb-3">
            <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Natural Writing</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Advanced prompt engineering for human-like, engaging content.
          </p>
        </div>
      </div>
    </div>
  );
}
