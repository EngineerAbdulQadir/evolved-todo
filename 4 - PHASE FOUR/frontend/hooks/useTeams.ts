import { useState, useEffect } from 'react';
import { Team } from '@/types/team';
import * as teamApi from '@/lib/api/teams';

export const useTeams = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTeams = async (organizationId: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await teamApi.listTeams(organizationId);
      setTeams(response.teams);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch teams');
      console.error('Error fetching teams:', err);
    } finally {
      setLoading(false);
    }
  };

  const createTeam = async (teamData: Omit<Team, 'id' | 'created_at' | 'updated_at'>) => {
    setLoading(true);
    setError(null);

    try {
      const newTeam = await teamApi.createTeam(teamData);
      setTeams(prev => [...prev, newTeam]);
      return newTeam;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create team');
      console.error('Error creating team:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateTeam = async (teamId: string, teamData: Partial<Team>) => {
    setLoading(true);
    setError(null);

    try {
      const updatedTeam = await teamApi.updateTeam(teamId, teamData);
      setTeams(prev => prev.map(t => t.id === teamId ? updatedTeam : t));
      return updatedTeam;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update team');
      console.error('Error updating team:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteTeam = async (teamId: string) => {
    setLoading(true);
    setError(null);

    try {
      await teamApi.deleteTeam(teamId);
      setTeams(prev => prev.filter(t => t.id !== teamId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete team');
      console.error('Error deleting team:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    teams,
    loading,
    error,
    fetchTeams,
    createTeam,
    updateTeam,
    deleteTeam,
  };
};