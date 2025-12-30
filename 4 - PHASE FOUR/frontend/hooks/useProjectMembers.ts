import { useState, useEffect } from 'react';
import { User } from '@/types/user';
import { projectApi } from '@/lib/api/projects';

export const useProjectMembers = () => {
  const [members, setMembers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMembers = async (projectId: string) => {
    setLoading(true);
    setError(null);

    try {
      const projectMembers = await projectApi.getProjectMembers(projectId);
      // The API might return members in a different format, so we might need to transform them
      // For now, we'll assume they match the User interface
      setMembers(projectMembers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch project members');
      console.error('Error fetching project members:', err);
    } finally {
      setLoading(false);
    }
  };

  return {
    members,
    loading,
    error,
    fetchMembers,
  };
};