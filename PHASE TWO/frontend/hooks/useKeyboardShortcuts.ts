/**
 * Keyboard shortcuts hook for improved UX (T222).
 *
 * Supported shortcuts:
 * - Space: Toggle task completion (when focused on task)
 * - Escape: Close modals/forms
 * - Ctrl+K / Cmd+K: Focus search
 * - N: Create new task
 */

import { useEffect, useCallback } from "react";

interface KeyboardShortcutsConfig {
  onEscape?: () => void;
  onSpace?: () => void;
  onSearch?: () => void;
  onNewTask?: () => void;
  enabled?: boolean;
}

export function useKeyboardShortcuts({
  onEscape,
  onSpace,
  onSearch,
  onNewTask,
  enabled = true,
}: KeyboardShortcutsConfig) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      // Ignore if user is typing in an input, textarea, or contenteditable element
      const target = event.target as HTMLElement;
      const isTyping =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable;

      // Escape key - close modals/forms (works even when typing)
      if (event.key === "Escape" && onEscape) {
        event.preventDefault();
        onEscape();
        return;
      }

      // Don't handle other shortcuts when typing
      if (isTyping) return;

      // Space key - toggle task completion
      if (event.key === " " && onSpace) {
        event.preventDefault();
        onSpace();
        return;
      }

      // Ctrl+K / Cmd+K - focus search
      if ((event.ctrlKey || event.metaKey) && event.key === "k" && onSearch) {
        event.preventDefault();
        onSearch();
        return;
      }

      // N key - create new task
      if (event.key === "n" && onNewTask) {
        event.preventDefault();
        onNewTask();
        return;
      }
    },
    [enabled, onEscape, onSpace, onSearch, onNewTask]
  );

  useEffect(() => {
    if (!enabled) return;

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [enabled, handleKeyDown]);
}

/**
 * Hook for modal/dialog keyboard shortcuts.
 * Automatically handles Escape key to close.
 */
export function useModalShortcuts(onClose: () => void, enabled = true) {
  useKeyboardShortcuts({
    onEscape: onClose,
    enabled,
  });
}

/**
 * Hook for task item keyboard shortcuts.
 * Handles Space to toggle completion.
 */
export function useTaskItemShortcuts(
  onToggle: () => void,
  enabled = true
) {
  useKeyboardShortcuts({
    onSpace: onToggle,
    enabled,
  });
}
