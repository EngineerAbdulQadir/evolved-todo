'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage, APIError } from '@/lib/api-client';
import type { Message, ChatRequest } from '@/types/chat';
import { Send, Bot, User, Sparkles, Terminal, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ChatInterfaceProps {
  userId: string;
  initialConversationId?: number;
}

/**
 * Highlight task IDs, priorities, and other special keywords in text.
 * Sharp / Industrial Theme Version.
 */
function highlightTaskDetails(text: string): React.ReactNode {
  const taskIdPattern = /\b(task\s+#?(\d+)|task\s+id:?\s*(\d+))\b/gi;
  const priorityPattern = /\b(high|medium|low)\s+priority\b/gi;
  const statusPattern = /\b(complete|completed|done|pending|deleted|created|updated)\b/gi;

  let parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let matches: Array<{ index: number; text: string; type: string }> = [];

  // Find all matches
  let match;
  const patterns = [
    { pattern: taskIdPattern, type: 'taskId' },
    { pattern: priorityPattern, type: 'priority' },
    { pattern: statusPattern, type: 'status' },
  ];

  patterns.forEach(({ pattern, type }) => {
    while ((match = pattern.exec(text)) !== null) {
      matches.push({
        index: match.index,
        text: match[0],
        type,
      });
    }
  });

  matches.sort((a, b) => a.index - b.index);

  matches.forEach((match, i) => {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    // SHARP THEME STYLES
    const className =
      match.type === 'taskId'
        ? 'font-mono font-bold text-white bg-neutral-900 border border-neutral-700 px-1.5 mx-0.5 rounded-none'
        : match.type === 'priority'
        ? 'font-bold text-white uppercase text-[10px] tracking-wide border border-white/40 px-1 rounded-none bg-black'
        : 'font-mono text-white underline decoration-white/30 underline-offset-4 decoration-1';

    parts.push(
      <span key={`match-${i}`} className={className}>
        {match.text}
      </span>
    );

    lastIndex = match.index + match.text.length;
  });

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? <>{parts}</> : text;
}

export function ChatInterface({ userId, initialConversationId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<number | undefined>(initialConversationId);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation history
  useEffect(() => {
    const loadConversationHistory = async () => {
      if (!initialConversationId) return;

      try {
        setIsLoading(true);
        const history = await import('@/lib/api-client').then(
          ({ getConversationHistory }) => getConversationHistory(userId, initialConversationId)
        );

        const formattedMessages = history.messages.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          created_at: msg.created_at || new Date().toISOString(),
        }));

        setMessages(formattedMessages);
      } catch (err) {
        console.error('Failed to load conversation history:', err);
        setError('Failed to load conversation history. Starting fresh.');
      } finally {
        setIsLoading(false);
      }
    };

    loadConversationHistory();
  }, [userId, initialConversationId]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const request: ChatRequest = {
        message: userMessage.content,
        conversation_id: conversationId,
      };

      const response = await sendChatMessage(userId, request);

      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        created_at: response.created_at,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Check for task operations to trigger UI updates in parent
      const message = response.message.toLowerCase();
      const taskOperations = ['created', 'added', 'updated', 'completed', 'deleted', 'marked'];
      const isTaskOperation = message.includes('task') &&
                              taskOperations.some(op => message.includes(op));

      if (isTaskOperation) {
        window.dispatchEvent(new CustomEvent('ai-task-updated'));
      }
    } catch (err) {
      console.error('Chat error:', err);
      if (err instanceof APIError) {
        setError(err.detail || err.message);
      } else {
        setError('Failed to send message. Please try again.');
      }
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-black border-l border-white/10 relative">
      
      {/* --- CHAT HEADER --- */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-white/10 bg-[#050505]">
        <div className="flex items-center gap-3">
            <div className="w-2 h-2 bg-white animate-pulse"></div>
            <h2 className="text-[10px] font-mono font-bold text-white uppercase tracking-widest">Neural Link</h2>
        </div>
        {conversationId && (
          <span className="text-[10px] text-neutral-600 font-mono border border-neutral-800 px-2 py-0.5 rounded-none bg-black">
            SESSION_ID: {conversationId}
          </span>
        )}
      </div>

      {/* --- MESSAGES AREA --- */}
      <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-black custom-scrollbar">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-neutral-600">
            <div className="w-12 h-12 border border-neutral-800 flex items-center justify-center mb-4">
               <Terminal className="w-6 h-6 text-neutral-500" />
            </div>
            <p className="text-xs font-mono text-white font-bold tracking-widest uppercase mb-1">System Ready</p>
            <p className="text-[10px] font-mono text-neutral-600 uppercase tracking-widest">
              Awaiting Input...
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {/* Avatar - Assistant */}
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-none bg-black border border-white/20 flex items-center justify-center flex-shrink-0 mt-1">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}

            {/* Message Bubble */}
            <div
              className={`max-w-[85%] rounded-none p-4 ${
                message.role === 'user'
                  ? 'bg-white text-black border border-white' // Sharp white block for user
                  : 'bg-black text-neutral-300 border border-white/10' // Black block with border for AI
              }`}
            >
              <div className={`text-sm ${message.role === 'assistant' ? 'font-sans leading-relaxed' : 'font-bold font-mono'}`}>
                {message.role === 'assistant' ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom components for Markdown to match the Sharp aesthetic
                      p: ({ children }) => <p className="mb-2 last:mb-0">{highlightTaskDetails(String(children))}</p>,
                      strong: ({ children }) => <strong className="text-white font-bold uppercase">{children}</strong>,
                      ul: ({ children }) => <ul className="list-square list-inside space-y-1 my-2 border-l border-white/20 pl-4">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 my-2 border-l border-white/20 pl-4 font-mono text-xs">{children}</ol>,
                      li: ({ children }) => <li className="text-neutral-300">{children}</li>,
                      h1: ({ children }) => <h1 className="text-white font-bold text-lg uppercase tracking-widest border-b border-white/20 pb-1 mb-2">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-white font-bold text-sm uppercase tracking-wider mb-2">{children}</h2>,
                      code: ({ children }) => <code className="bg-[#111] border border-white/10 text-white px-1 py-0.5 rounded-none text-xs font-mono">{children}</code>,
                      pre: ({ children }) => <pre className="bg-[#111] border border-white/10 p-3 my-2 overflow-x-auto text-xs font-mono">{children}</pre>,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                ) : (
                  message.content
                )}
              </div>
              
              {/* Timestamp */}
              {message.created_at && (
                <p className={`text-[9px] mt-2 font-mono uppercase tracking-widest ${message.role === 'user' ? 'text-neutral-400 text-right' : 'text-neutral-600'}`}>
                  {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              )}
            </div>

            {/* Avatar - User */}
            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-none bg-white border border-white flex items-center justify-center flex-shrink-0 mt-1">
                <User className="w-4 h-4 text-black" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start gap-4">
            <div className="w-8 h-8 rounded-none bg-black border border-white/20 flex items-center justify-center">
               <Bot className="w-4 h-4 text-neutral-500" />
            </div>
            <div className="bg-black border border-white/10 px-4 py-3 flex items-center gap-1 h-12">
               <span className="w-1.5 h-3 bg-white animate-pulse"></span>
               <span className="text-xs font-mono text-neutral-500 uppercase tracking-widest ml-2">Processing Data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* --- ERROR DISPLAY --- */}
      {error && (
        <div className="px-6 py-3 bg-red-950/20 border-t border-red-900/50">
          <p className="text-xs text-red-500 font-mono flex items-center gap-2 uppercase tracking-wide">
            <AlertCircle className="w-3 h-3" />
            System Error: {error}
          </p>
        </div>
      )}

      {/* --- INPUT AREA --- */}
      <div className="p-0 bg-black border-t border-white/10">
        <form onSubmit={handleSubmit} className="relative flex">
          <div className="w-12 flex items-center justify-center border-r border-white/10 text-neutral-500">
             <span className="font-mono text-lg">{'>'}</span>
          </div>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="ENTER_COMMAND..."
            disabled={isLoading}
            className="flex-1 py-4 px-4 bg-black border-none text-white placeholder-neutral-700 font-mono text-sm focus:ring-0 uppercase tracking-wider"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-6 border-l border-white/10 text-neutral-500 hover:text-white hover:bg-white/5 disabled:opacity-30 disabled:hover:bg-transparent transition-colors uppercase font-mono text-xs font-bold tracking-widest"
          >
            SEND
          </button>
        </form>
      </div>
    </div>
  );
}