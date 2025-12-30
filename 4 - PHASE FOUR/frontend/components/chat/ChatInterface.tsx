'use client';

import { useState, useEffect, useRef } from 'react';
import { useChatKit, ChatKit } from '@openai/chatkit-react';
import { CHATKIT_CONFIG } from '@/lib/chat-config';
// DISABLED: Multi-tenant icons
// import { Building2, Users, Layers, Info } from 'lucide-react';

interface ChatInterfaceProps {
  userId: string;
}

export function ChatInterface({ userId }: ChatInterfaceProps) {
  const [error, setError] = useState<string | null>(null);
  const [isRestoring, setIsRestoring] = useState(true);
  const hasRestoredRef = useRef(false);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);

  // Custom fetch to add JWT authentication
  const authenticatedFetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const token = localStorage.getItem('auth_token');

    const headers = new Headers(init?.headers);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    return fetch(input, {
      ...init,
      headers,
    });
  };

  // Initialize ChatKit with custom backend (Full Proxy Mode)
  // Research confirmed: url + domainKey is correct for ChatKit Python SDK backends
  const {
    control,
    setThreadId,
    sendUserMessage,
    setComposerValue,
    focusComposer,
    fetchUpdates,
    sendCustomAction,
  } = useChatKit({
    api: {
      url: CHATKIT_CONFIG.api.url,
      domainKey: 'localhost', // Placeholder for local dev (no registration needed)
      fetch: authenticatedFetch, // Add JWT to all requests
    },
    theme: {
      colorScheme: 'dark',
      color: {
        grayscale: { hue: 0, tint: 0, shade: 0 },
        accent: { primary: '#ffffff', level: 1 },
      },
      radius: 'sharp',
    },
    composer: {
      placeholder: CHATKIT_CONFIG.ui.placeholder,
    },
    startScreen: {
      greeting: 'Welcome to Evolved Todo AI Assistant! 🤖\n\nI can help you manage your tasks using natural language.',
      prompts: [
        // Task Management
        { label: 'Add Task', prompt: 'Create a task to review Q4 reports with high priority' },
        { label: 'View Tasks', prompt: 'Show me all my active tasks' },
        { label: 'Complete Task', prompt: 'Mark the quarterly report task as complete' },
        { label: 'Search Tasks', prompt: 'Find all tasks with tag "urgent"' },
        { label: 'Update Task', prompt: 'Change the priority of my report task to high' },
        { label: 'Delete Task', prompt: 'Delete the completed meeting notes task' },
      ],
    },
    onError: ({ error }) => {
      setError(error.message || 'ChatKit encountered an error');
    },
  });

  // Restore the most recent conversation when component mounts
  useEffect(() => {
    if (!control || hasRestoredRef.current) return;

    const restoreConversation = async () => {
      try {
        console.log('[ChatInterface] ChatKit mounted, starting fresh conversation');

        // Artificial delay for UI consistency (2 seconds)
        await new Promise(resolve => setTimeout(resolve, 2000));

        hasRestoredRef.current = true;
        setIsRestoring(false);
      } catch (err) {
        console.error('[ChatInterface] Error restoring conversation:', err);
        hasRestoredRef.current = true;
      } finally {
        setIsRestoring(false);
      }
    };

    restoreConversation();
  }, [control, setThreadId, userId]);

  // Save current thread ID to localStorage whenever it changes
  useEffect(() => {
    if (currentThreadId && currentThreadId !== '0') {
      const previousThreadId = localStorage.getItem(`chatkit_last_thread_${userId}`);

      // Log if thread ID changed
      if (previousThreadId !== currentThreadId) {
        console.log('[ChatInterface] Thread ID changed:', {
          previous: previousThreadId,
          current: currentThreadId,
          message: previousThreadId && previousThreadId !== currentThreadId
            ? '⚠️  WARNING: Thread ID changed unexpectedly! Each message might be creating a new conversation.'
            : '✅ Thread ID set successfully'
        });
      }

      localStorage.setItem(`chatkit_last_thread_${userId}`, currentThreadId);
      console.log('[ChatInterface] Saved current thread to localStorage:', currentThreadId);
    }
  }, [currentThreadId, userId]);

  // Debug: Log when thread ID changes
  useEffect(() => {
    console.log('[ChatInterface] Current thread ID:', currentThreadId || 'none');
  }, [currentThreadId]);

  // ChatKit error handling (preserved from original implementation)
  const chatKitError: Error | null = null; // ChatKit errors are handled via onError callback

  if (!control) {
    return (
      <div className="flex flex-col h-full bg-black items-center justify-center">
        <div className="text-white font-mono text-sm">
          {chatKitError ? (
            <>
              <p className="text-red-500 mb-2">ChatKit Error:</p>
              <p className="text-neutral-400">{(chatKitError as Error).message || String(chatKitError)}</p>
            </>
          ) : (
            <p className="text-neutral-500">Initializing ChatKit...</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col overflow-hidden relative" style={{ background: '#000' }}>
      {/* DISABLED: Multi-Tenant Context Bar */}
      {/* {(organizationName || teamName || projectName) && (
        <div className="border-b border-white/10 bg-neutral-900/50 backdrop-blur-sm px-4 py-3 flex-shrink-0">
          <div className="flex items-center gap-4 flex-wrap text-sm">
            <div className="flex items-center gap-2 text-neutral-400">
              <Info className="w-4 h-4" />
              <span className="font-mono text-xs">Current Context:</span>
            </div>
            {organizationName && (
              <div className="flex items-center gap-2 px-3 py-1 bg-black/50 border border-white/10 rounded">
                <Building2 className="w-3 h-3 text-blue-400" />
                <span className="text-white text-xs font-medium">{organizationName}</span>
              </div>
            )}
            {teamName && (
              <div className="flex items-center gap-2 px-3 py-1 bg-black/50 border border-white/10 rounded">
                <Users className="w-3 h-3 text-green-400" />
                <span className="text-white text-xs font-medium">{teamName}</span>
              </div>
            )}
            {projectName && (
              <div className="flex items-center gap-2 px-3 py-1 bg-black/50 border border-white/10 rounded">
                <Layers className="w-3 h-3 text-purple-400" />
                <span className="text-white text-xs font-medium">{projectName}</span>
              </div>
            )}
          </div>
        </div>
      )} */}

      {/* Show loading overlay if restoring */}
      {isRestoring && (
        <div className="absolute inset-0 z-50 flex flex-col h-full bg-black items-center justify-center">
          <div className="text-white font-mono text-sm">
            <p className="text-neutral-500">Loading conversation...</p>
          </div>
        </div>
      )}

      {/* Always render ChatKit but keep it invisible during loading */}
      <div className={`w-full flex-1 ${isRestoring ? 'invisible' : 'visible'}`}>
        <ChatKit
          control={control}
          className="w-full h-full"
        />
      </div>
    </div>
  );
}
