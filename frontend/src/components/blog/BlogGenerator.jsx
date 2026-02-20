/**
 * Blog Generator component - main form for generating blog posts.
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { usePersonas } from '../../hooks/usePersonas';
import { useBlogGeneration, GENERATION_STAGES } from '../../hooks/useBlogGeneration';
import { Card, CardHeader, CardTitle } from '../ui/Card';
import { Textarea } from '../ui/Input';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { encryptBlogId } from '../../utils/blogIdCrypto';

const personaDescriptions = {
  technical: {
    name: 'Technical Writer',
    description: 'Precise, jargon-appropriate, citation-heavy',
    color: 'blue',
  },
  narrative: {
    name: 'Storyteller',
    description: 'Narrative-driven, emotional hooks',
    color: 'purple',
  },
  analyst: {
    name: 'Industry Analyst',
    description: 'Data-focused, trend-aware',
    color: 'green',
  },
  educator: {
    name: 'Educator',
    description: 'Explanatory, structured, beginner-friendly',
    color: 'yellow',
  },
};

export default function BlogGenerator() {
  const navigate = useNavigate();
  const { personas, isLoading: personasLoading } = usePersonas();
  const { state, generateBlog, cancelGeneration, retryLastJob } = useBlogGeneration();

  const [topic, setTopic] = useState('');
  const [selectedPersona, setSelectedPersona] = useState('technical');
  const [speed, setSpeed] = useState('fast');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (topic.trim().length < 5) {
      return;
    }

    const blogPostId = await generateBlog(topic, selectedPersona, speed);

    if (blogPostId) {
      navigate(`/blog/${encryptBlogId(blogPostId)}`);
    }
  };

  const isLoading = state.isGenerating || personasLoading;

  return (
    <div className="max-w-3xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>Generate AI Blog Post</CardTitle>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Enter a topic and choose a writing style to generate your blog post.
          </p>
        </CardHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Topic Input */}
          <Textarea
            label="Blog Topic"
            placeholder="e.g., The future of renewable energy in developing countries..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            rows={4}
            disabled={isLoading}
            error={topic.length > 0 && topic.length < 5 ? 'Topic must be at least 5 characters' : ''}
            required
          />

          {/* Persona Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Writing Style
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(personaDescriptions).map(([slug, desc]) => {
                const persona = personas.find(p => p.slug === slug);
                if (!persona) return null;

                const isSelected = selectedPersona === slug;
                const colorClasses = {
                  blue: 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20',
                  purple: 'border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-900/20',
                  green: 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20',
                  yellow: 'border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20',
                };

                return (
                  <button
                    key={slug}
                    type="button"
                    onClick={() => setSelectedPersona(slug)}
                    disabled={isLoading}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      isSelected
                        ? `border-primary-500 bg-primary-50 dark:bg-primary-900/20 dark:border-primary-500`
                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-1">
                      <span className="font-medium text-gray-900 dark:text-white">
                        {desc.name}
                      </span>
                      {isSelected && (
                        <Badge variant="blue">Selected</Badge>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {desc.description}
                    </p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Generate Button */}
          <div className="relative flex items-center gap-6">
            <select
              value={speed}
              onChange={(e) => setSpeed(e.target.value)}
              disabled={isLoading}
              className="appearance-none px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800"
            >
              <option value="fast">Fast</option>
              <option value="normal">Normal</option>
            </select>
            
            <Button
              type="submit"
              variant="primary"
              size="lg"
              isLoading={isLoading}
              disabled={topic.trim().length < 5 || isLoading}
              className="w-full"
            >
              {isLoading ? (
                <>Generating...</>
              ) : (
                <>
                  <SparklesIcon className="w-5 h-5" />
                  Generate Blog Post
                </>
              )}
            </Button>
            {state.isGenerating && (
              <Button type="button" variant="secondary" onClick={cancelGeneration}>
                Cancel
              </Button>
            )}
            {!state.isGenerating && state.currentStage === 'error' && state.jobId && (
              <Button type="button" variant="secondary" onClick={retryLastJob}>
                Retry
              </Button>
            )}
          </div>

          {/* Progress Indicator */}
          {state.isGenerating && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                <span>{GENERATION_STAGES[state.currentStage]}</span>
                <span>{state.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${state.progress}%` }}
                />
              </div>
            </div>
          )}
        </form>
      </Card>
    </div>
  );
}
