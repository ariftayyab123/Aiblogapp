/**
 * Hook for managing blog post generation.
 * Supports asynchronous queue-based generation with polling.
 */
import { useState, useCallback, useRef } from 'react';
import { blogApi } from '../services/api';
import { useSession } from '../contexts/SessionContext';
import { useToast } from '../contexts/ToastContext';

const POLL_INTERVAL_MS = 1000;
const MAX_POLL_ATTEMPTS = 120;

export function useBlogGeneration() {
  const { sessionId } = useSession();
  const { success, error, info } = useToast();
  const cancelRef = useRef(false);

  const [state, setState] = useState({
    isGenerating: false,
    progress: 0,
    currentStage: 'idle', // idle, prompting, generating, completed, error
    error: null,
    blogPostId: null,
    jobId: null,
  });

  const cancelGeneration = useCallback(() => {
    cancelRef.current = true;
    setState((prev) => ({
      ...prev,
      isGenerating: false,
      currentStage: 'idle',
      error: null,
    }));
    info('Generation polling cancelled');
  }, [info]);

  const pollStatus = useCallback(async (jobId, attempts = 0) => {
    if (cancelRef.current) return null;

    if (attempts >= MAX_POLL_ATTEMPTS) {
      setState((prev) => ({
        ...prev,
        isGenerating: false,
        currentStage: 'error',
        error: 'Generation timed out',
      }));
      error('Generation timed out');
      return null;
    }

    try {
      const response = await blogApi.generationStatus(jobId);
      const data = response.data;

      if (data.status === 'completed') {
        setState({
          isGenerating: false,
          progress: 100,
          currentStage: 'completed',
          error: null,
          blogPostId: data.blog_post_id || null,
          jobId,
        });
        success('Blog post generated successfully!');
        return data.blog_post_id || null;
      }

      if (data.status === 'failed') {
        const message = data.error_message || 'Generation failed';
        setState((prev) => ({
          ...prev,
          isGenerating: false,
          currentStage: 'error',
          error: message,
          progress: 100,
        }));
        error(message);
        return null;
      }

      const progress = Number.isFinite(data.progress) ? data.progress : Math.min(95, 10 + attempts);
      setState((prev) => ({
        ...prev,
        progress,
        currentStage: data.status === 'running' ? 'generating' : 'prompting',
        jobId,
      }));

      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
      return pollStatus(jobId, attempts + 1);
    } catch (err) {
      if (attempts >= 5) {
        const message = err.message || 'Failed to check generation status';
        setState((prev) => ({
          ...prev,
          isGenerating: false,
          currentStage: 'error',
          error: message,
        }));
        error(message);
        return null;
      }
      await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS));
      return pollStatus(jobId, attempts + 1);
    }
  }, [error, success]);

  const generateBlog = useCallback(async (topic, personaSlug, speed = 'fast') => {
    cancelRef.current = false;
    setState({
      isGenerating: true,
      progress: 0,
      currentStage: 'prompting',
      error: null,
      blogPostId: null,
      jobId: null,
    });

    try {
      const response = await blogApi.generate({
        topic,
        persona: personaSlug,
        session_id: sessionId,
        speed,
      });

      const result = response.data;

      // Backward compatibility for sync response path.
      if (result.status === 'completed' && result.blog_post_id) {
        setState({
          isGenerating: false,
          progress: 100,
          currentStage: 'completed',
          error: null,
          blogPostId: result.blog_post_id,
          jobId: null,
        });
        success('Blog post generated successfully!');
        return result.blog_post_id;
      }

      if (result.job_id) {
        setState((prev) => ({
          ...prev,
          currentStage: 'generating',
          progress: 15,
          jobId: result.job_id,
        }));
        return pollStatus(result.job_id, 0);
      }

      throw new Error('Unexpected generation response');
    } catch (err) {
      const message = err.message || 'Failed to generate blog post';
      setState({
        isGenerating: false,
        progress: 0,
        currentStage: 'error',
        error: message,
        blogPostId: null,
        jobId: null,
      });
      error(message);
      return null;
    }
  }, [sessionId, pollStatus, success, error]);

  const retryLastJob = useCallback(async () => {
    if (!state.jobId) return null;
    setState((prev) => ({
      ...prev,
      isGenerating: true,
      currentStage: 'generating',
      error: null,
    }));
    return pollStatus(state.jobId, 0);
  }, [state.jobId, pollStatus]);

  const resetState = useCallback(() => {
    cancelRef.current = true;
    setState({
      isGenerating: false,
      progress: 0,
      currentStage: 'idle',
      error: null,
      blogPostId: null,
      jobId: null,
    });
  }, []);

  return {
    state,
    generateBlog,
    cancelGeneration,
    retryLastJob,
    resetState,
  };
}

export const GENERATION_STAGES = {
  idle: '',
  prompting: 'Preparing your prompt...',
  generating: 'AI is writing your blog post...',
  completed: 'Blog post generated!',
  error: 'Generation failed',
};
