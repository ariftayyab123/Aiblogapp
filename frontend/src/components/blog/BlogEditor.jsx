/**
 * Blog Editor - inline form for editing a blog post's title, topic, and markdown content.
 */
import { useState, useEffect } from 'react';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { Card } from '../ui/Card';
import { Input, Textarea } from '../ui/Input';
import { Button } from '../ui/Button';

export default function BlogEditor({ blogPost, isSaving, onSave, onCancel }) {
  const [title, setTitle] = useState(blogPost?.title || '');
  const [topic, setTopic] = useState(blogPost?.topic_input || '');
  const [content, setContent] = useState(blogPost?.generated_content || '');
  const [errors, setErrors] = useState({});

  useEffect(() => {
    setTitle(blogPost?.title || '');
    setTopic(blogPost?.topic_input || '');
    setContent(blogPost?.generated_content || '');
  }, [blogPost]);

  const validate = () => {
    const next = {};
    if (!title.trim()) next.title = 'Title is required';
    if (!topic.trim()) next.topic = 'Topic is required';
    if (!content.trim()) next.content = 'Content cannot be empty';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validate()) return;
    onSave({
      title: title.trim(),
      topic_input: topic.trim(),
      generated_content: content,
    });
  };

  return (
    <Card className="mx-auto max-w-4xl">
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-xl font-semibold tracking-tight text-ink-950 dark:text-ink-50">
            Edit Blog Post
          </h2>
          <p className="eyebrow">Markdown supported</p>
        </div>

        <Input
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          error={errors.title}
          placeholder="Blog post title"
        />

        <Input
          label="Topic"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          error={errors.topic}
          placeholder="Original topic"
        />

        <Textarea
          label="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          error={errors.content}
          rows={18}
          className="font-mono text-sm leading-relaxed"
          placeholder="Write your blog content in markdown..."
        />

        <div className="flex items-center justify-end gap-3 pt-2">
          <Button type="button" variant="quiet" onClick={onCancel} disabled={isSaving}>
            <XMarkIcon className="h-5 w-5" aria-hidden="true" />
            Cancel
          </Button>
          <Button type="submit" variant="ink" isLoading={isSaving}>
            <CheckIcon className="h-5 w-5" aria-hidden="true" />
            Save Changes
          </Button>
        </div>
      </form>
    </Card>
  );
}