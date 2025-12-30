'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Project } from '@/types/project';
import { useProjects } from '@/hooks/useProjects';

import { Project } from '@/types/project';
import { useTeams } from '@/hooks/useTeams';
import { useAuth } from '@/hooks/useAuth';

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateProject: (projectData: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => Promise<void>;
  initialTeamId?: string;
  organizationId?: string;
}

export const CreateProjectDialog: React.FC<CreateProjectDialogProps> = ({
  open,
  onOpenChange,
  onCreateProject,
  initialTeamId,
  organizationId,
}) => {
  const { user } = useAuth();
  const { teams } = useTeams();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('active');
  const [teamId, setTeamId] = useState(initialTeamId || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync initialTeamId if it changes
  React.useEffect(() => {
    if (initialTeamId) setTeamId(initialTeamId);
  }, [initialTeamId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!teamId) {
        setError("Team selection required.");
        return;
    }
    setLoading(true);
    setError(null);

    try {
      await onCreateProject({
        name,
        description,
        status,
        team_id: teamId,
        organization_id: organizationId || '',
      });
      setName('');
      setDescription('');
      setStatus('active');
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md rounded-none border-white/20 bg-black text-white font-mono">
        <DialogHeader className="border-b border-white/10 pb-4">
          <DialogTitle className="text-xs font-bold uppercase tracking-[0.2em]">Project_Initialization</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6 py-6">
          
          <div className="space-y-2">
            <Label htmlFor="team" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Target_Unit (Team)</Label>
            <select
              id="team"
              value={teamId}
              onChange={(e) => setTeamId(e.target.value)}
              className="w-full rounded-none border border-neutral-800 bg-[#050505] text-xs font-mono p-3 focus:border-white focus:ring-0 text-white appearance-none"
              required
            >
              <option value="" disabled className="text-neutral-700">-- SELECT OPERATIONAL UNIT --</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id} className="bg-black text-white">
                  {team.name.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="name" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Project_Identity</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. ALPHA_STRIKE_PRO"
              className="rounded-none border-neutral-800 bg-[#050505] text-xs font-mono focus:border-white focus:ring-0 placeholder:text-neutral-700"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400">Objective_Parameters</Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Primary mission objectives and scope..."
              className="rounded-none border-neutral-800 bg-[#050505] text-xs font-mono focus:border-white focus:ring-0 placeholder:text-neutral-700 min-h-[80px]"
            />
          </div>
          
          {error && (
            <div className="p-3 bg-red-950/20 border border-red-900/50 rounded-none">
                <p className="text-[10px] font-mono text-red-500 uppercase">{error}</p>
            </div>
          )}

          <DialogFooter className="border-t border-white/10 pt-4">
            <Button 
                type="button" 
                variant="outline" 
                onClick={() => onOpenChange(false)}
                className="rounded-none border-neutral-800 text-neutral-500 hover:text-white text-[10px] font-bold uppercase tracking-widest"
            >
              Abort
            </Button>
            <Button 
                type="submit" 
                disabled={loading}
                className="rounded-none bg-white text-black hover:bg-neutral-200 text-[10px] font-bold uppercase tracking-widest px-6"
            >
              {loading ? 'Initializing...' : 'Deploy Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};