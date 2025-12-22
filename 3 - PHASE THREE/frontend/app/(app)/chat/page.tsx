/**
 * Chat page for AI-powered todo management.
 *
 * Task: T021 - Create chat page
 * Spec: specs/003-phase3-ai-chatbot/spec.md
 */

"use client";

import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { ChatInterface } from '@/components/chat/ChatInterface';

export default function ChatPage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-950 text-cyan-500 font-mono">
        INITIALIZING SYSTEM...
      </div>
    );
  }

  // Don't render anything if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          AI Todo Assistant
        </h1>
        <p className="text-gray-600 mt-2">
          Manage your tasks using natural language
        </p>
      </div>

      <ChatInterface userId={user!.id} />

      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Try these commands:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• &quot;Add a task to buy groceries&quot;</li>
          <li>• &quot;Show me my tasks&quot;</li>
          <li>• &quot;Mark task 3 as complete&quot;</li>
          <li>• &quot;Add a high priority task to prepare presentation&quot;</li>
          <li>• &quot;Create a weekly recurring task for team meeting&quot;</li>
        </ul>
      </div>
    </div>
  );
}
