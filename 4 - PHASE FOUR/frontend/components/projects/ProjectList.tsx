'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { PlusIcon, UsersIcon, CalendarIcon, FolderIcon } from 'lucide-react';
import { Project } from '@/types/project';
import { useProjects } from '@/hooks/useProjects';
import { CreateProjectDialog } from './CreateProjectDialog';

interface ProjectListProps {
  teamId?: string;
  organizationId?: string;
}

export const ProjectList: React.FC<ProjectListProps> = ({ 
  teamId, 
  organizationId 
}) => {
  const {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject
  } = useProjects();
  
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedTeamId, setSelectedTeamId] = useState<string | undefined>(teamId);

  useEffect(() => {
    if (teamId) {
      fetchProjects(teamId);
    }
  }, [teamId, fetchProjects]);

  const handleCreateProject = async (projectData: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => {
    if (!selectedTeamId) {
      throw new Error('Team ID is required to create a project');
    }
    
    await createProject({
      ...projectData,
      team_id: selectedTeamId,
      organization_id: organizationId
    });
    
    setIsCreateDialogOpen(false);
  };

  if (error) {
    return (
      <div className="p-4 text-center">
        <p className="text-destructive">Error loading projects: {error.message}</p>
        <Button onClick={() => fetchProjects(selectedTeamId || '')} className="mt-2">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 border border-dashed border-neutral-800 bg-[#050505]">
          <FolderIcon className="h-10 w-10 text-neutral-700 mb-4" />
          <p className="text-neutral-500 font-mono text-[10px] uppercase tracking-widest text-center">
            No active projects detected.
            <br />
            Deploy new manifest to begin.
          </p>
        </div>
      ) : (
        <div className="grid gap-0 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-t border-l border-white/10">
          {projects.map((project) => (
            <div 
                key={project.id} 
                className="group relative bg-black border-r border-b border-white/10 p-6 transition-all duration-200 hover:bg-[#050505] hover:border-white/40 cursor-default"
            >
              {/* Decorative Corner */}
              <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/0 group-hover:border-white/40 transition-colors"></div>

              <div className="flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white flex items-center gap-2">
                        <FolderIcon className="h-3 w-3 text-neutral-500" />
                        {project.name}
                    </h3>
                    <div className="text-[8px] font-mono text-neutral-600 uppercase tracking-tight mt-1">
                        PRJ_ID // {project.id.substring(0, 13)}
                    </div>
                  </div>
                  <span className="px-1.5 py-0.5 border border-white/10 text-[8px] font-bold text-neutral-400 uppercase tracking-widest">
                    {project.status || 'Active'}
                  </span>
                </div>

                <p className="text-[10px] font-mono text-neutral-500 mb-6 line-clamp-2 leading-relaxed uppercase">
                  {project.description || 'No operational description provided.'}
                </p>

                <div className="mt-auto space-y-3">
                    <div className="flex items-center justify-between text-[9px] font-mono uppercase">
                        <div className="flex items-center gap-1.5 text-neutral-500">
                            <UsersIcon className="h-3 w-3" />
                            <span>{project.members_count || 0} Assets</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-neutral-600">
                            <CalendarIcon className="h-3 w-3" />
                            <span>{new Date(project.created_at).toLocaleDateString()}</span>
                        </div>
                    </div>
                    
                    <div className="pt-3 border-t border-white/5 flex gap-2">
                         <button 
                            className="flex-1 py-1.5 text-[8px] font-bold uppercase tracking-widest border border-white/5 text-neutral-500 hover:text-white hover:border-white/20 transition-all"
                            onClick={() => console.log("Manage Project:", project.id)}
                         >
                            Config
                         </button>
                         <button 
                            className="px-3 py-1.5 text-[8px] font-bold uppercase tracking-widest border border-white/5 text-red-900/40 hover:text-red-500 hover:border-red-900/20 transition-all"
                            onClick={() => deleteProject(project.id)}
                         >
                            Purge
                         </button>
                    </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <CreateProjectDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onCreateProject={handleCreateProject}
        initialTeamId={teamId}
        organizationId={organizationId}
      />
    </div>
  );
};