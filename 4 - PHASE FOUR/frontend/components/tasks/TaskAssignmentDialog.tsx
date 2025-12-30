'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { User } from '@/types/user';
import { Task } from '@/types/task';
import { useProjectMembers } from '@/hooks/useProjectMembers';

interface TaskAssignmentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAssignTask: (taskId: string, userId: string) => Promise<void>;
  taskId: string;
  projectId: string;
  currentAssigneeId?: string;
}

export const TaskAssignmentDialog: React.FC<TaskAssignmentDialogProps> = ({
  open,
  onOpenChange,
  onAssignTask,
  taskId,
  projectId,
  currentAssigneeId,
}) => {
  const [selectedUserId, setSelectedUserId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { members, loading: membersLoading, error: membersError, fetchMembers } = useProjectMembers();

  useEffect(() => {
    if (open && projectId) {
      fetchMembers(projectId);
      if (currentAssigneeId) {
        setSelectedUserId(currentAssigneeId);
      }
    }
  }, [open, projectId, currentAssigneeId, fetchMembers]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onAssignTask(taskId, selectedUserId);
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign task');
    } finally {
      setLoading(false);
    }
  };

  const handleUnassign = async () => {
    setLoading(true);
    setError(null);

    try {
      await onAssignTask(taskId, ''); // Empty string to unassign
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unassign task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Assign Task</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="assignee">Assign to</Label>
            {membersError ? (
              <div className="text-destructive text-sm">
                Error loading members: {membersError}
              </div>
            ) : membersLoading ? (
              <div className="h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm">
                Loading members...
              </div>
            ) : (
              <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a team member" />
                </SelectTrigger>
                <SelectContent>
                  {members.map((member: User) => (
                    <SelectItem key={member.id} value={member.id}>
                      {member.name || member.email}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
          {error && (
            <div className="text-destructive text-sm">
              {error}
            </div>
          )}
          <DialogFooter className="flex gap-2">
            {currentAssigneeId && (
              <Button
                type="button"
                variant="outline"
                onClick={handleUnassign}
                disabled={loading}
              >
                Unassign
              </Button>
            )}
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading || !selectedUserId}>
              {loading ? 'Assigning...' : 'Assign Task'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};