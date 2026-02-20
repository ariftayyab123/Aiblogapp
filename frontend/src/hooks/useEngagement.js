/**
 * Hook for managing user engagement (likes/dislikes) on blog posts.
 * Handles optimistic updates and server synchronization.
 */
import { useState, useCallback, useEffect } from 'react';
import { engagementApi } from '../services/api';
import { useSession } from '../contexts/SessionContext';

export function useEngagement(blogPostId) {
  const { sessionId } = useSession();

  const [state, setState] = useState({
    likes: 0,
    dislikes: 0,
    userEngagement: null, // 'like', 'dislike', or null
    isSubmitting: false,
    isLoading: true,
  });

  // Fetch initial engagement data
  useEffect(() => {
    const fetchEngagement = async () => {
      if (!blogPostId) return;

      try {
        const response = await engagementApi.getMetrics(blogPostId, sessionId);
        const data = response.data;

        setState({
          likes: data.likes || 0,
          dislikes: data.dislikes || 0,
          userEngagement: data.user_action || null,
          isSubmitting: false,
          isLoading: false,
        });
      } catch (err) {
        console.error('Failed to fetch engagement:', err);
        setState(prev => ({ ...prev, isLoading: false }));
      }
    };

    fetchEngagement();
  }, [blogPostId, sessionId]);

  const fetchEngagement = useCallback(async () => {
    if (!blogPostId) return;

    try {
      const response = await engagementApi.getMetrics(blogPostId, sessionId);
      const data = response.data;

      setState({
        likes: data.likes || 0,
        dislikes: data.dislikes || 0,
        userEngagement: data.user_action || null,
        isSubmitting: false,
        isLoading: false,
      });
    } catch (err) {
      console.error('Failed to fetch engagement:', err);
    }
  }, [blogPostId, sessionId]);

  const toggleEngagement = useCallback(async (action) => {
    if (!blogPostId || state.isSubmitting) return;

    const isRemoving = state.userEngagement === action;

    // Optimistic update
    setState(prev => {
      const newState = { ...prev, isSubmitting: true };

      if (action === 'like') {
        newState.likes = prev.likes + (isRemoving ? -1 : 1);
        if (prev.userEngagement === 'dislike' && !isRemoving) {
          newState.dislikes = prev.dislikes - 1;
        }
      } else if (action === 'dislike') {
        newState.dislikes = prev.dislikes + (isRemoving ? -1 : 1);
        if (prev.userEngagement === 'like' && !isRemoving) {
          newState.likes = prev.likes - 1;
        }
      }

      newState.userEngagement = isRemoving ? null : action;
      return newState;
    });

    try {
      const response = await engagementApi.record({
        blog_id: blogPostId,
        action,
        session_id: sessionId,
      });

      const data = response.data;

      // Sync with server response
      setState({
        likes: data.likes_count,
        dislikes: data.dislikes_count,
        userEngagement: data.was_toggle ? null : action,
        isSubmitting: false,
        isLoading: false,
      });
    } catch (err) {
      // Rollback on error
      await fetchEngagement();
    }
  }, [blogPostId, sessionId, state.userEngagement, state.isSubmitting, fetchEngagement]);

  const like = () => toggleEngagement('like');
  const dislike = () => toggleEngagement('dislike');

  return {
    state,
    like,
    dislike,
    fetchEngagement,
  };
}
