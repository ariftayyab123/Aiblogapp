/**
 * Hook for fetching and managing blog posts.
 */
import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { blogApi } from '../services/api';
import { useToast } from '../contexts/ToastContext';

export function useBlogPosts(filters = {}) {
  const { error } = useToast();
  const lastErrorRef = useRef(null);
  const [state, setState] = useState({
    posts: [],
    isLoading: true,
    error: null,
  });

  // Avoid infinite re-fetch loops from object identity changes.
  const filterKey = useMemo(() => JSON.stringify(filters || {}), [filters]);
  const normalizedFilters = useMemo(() => JSON.parse(filterKey), [filterKey]);

  const fetchPosts = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await blogApi.list(normalizedFilters);
      lastErrorRef.current = null;
      setState({
        posts: response.data.results || response.data,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState({
        posts: [],
        isLoading: false,
        error: err.message,
      });
      if (lastErrorRef.current !== err.message) {
        error('Failed to load blog posts');
        lastErrorRef.current = err.message;
      }
    }
  }, [normalizedFilters, error]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const deletePost = useCallback(async (postId) => {
    try {
      await blogApi.delete(postId);
      setState(prev => ({
        ...prev,
        posts: prev.posts.filter(p => p.id !== postId),
      }));
      return true;
    } catch (err) {
      error('Failed to delete blog post');
      return false;
    }
  }, [error]);

  return {
    ...state,
    fetchPosts,
    deletePost,
  };
}

/**
 * Hook for editing a single blog post.
 */
export function useEditBlogPost() {
  const { success, error } = useToast();
  const [isSaving, setIsSaving] = useState(false);

  const savePost = useCallback(async (postId, data) => {
    setIsSaving(true);
    try {
      const response = await blogApi.update(postId, data);
      success('Blog post updated');
      return response.data;
    } catch (err) {
      error(err?.message || 'Failed to update blog post');
      return null;
    } finally {
      setIsSaving(false);
    }
  }, [success, error]);

  return { isSaving, savePost };
}

/**
 * Hook for fetching a single blog post.
 */
export function useBlogPost(postId) {
  const { error } = useToast();
  const lastErrorRef = useRef(null);
  const [state, setState] = useState({
    post: null,
    isLoading: true,
    error: null,
  });

  const fetchPost = useCallback(async () => {
    if (!postId || Number.isNaN(postId)) {
      setState({
        post: null,
        isLoading: false,
        error: 'Invalid blog post id',
      });
      return;
    }

    setState(prev => ({ ...prev, isLoading: true }));

    try {
      const response = await blogApi.get(postId);
      lastErrorRef.current = null;
      setState({
        post: response.data,
        isLoading: false,
        error: null,
      });
    } catch (err) {
      setState({
        post: null,
        isLoading: false,
        error: err.message,
      });
      if (lastErrorRef.current !== err.message) {
        error('Failed to load blog post');
        lastErrorRef.current = err.message;
      }
    }
  }, [postId, error]);

  useEffect(() => {
    fetchPost();
  }, [fetchPost]);

  return {
    ...state,
    fetchPost,
    updatePost: (updates) => setState(prev => ({ ...prev, post: { ...(prev.post || {}), ...updates } })),
  };
}
