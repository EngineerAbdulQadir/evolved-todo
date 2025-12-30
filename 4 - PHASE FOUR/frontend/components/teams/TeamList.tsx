"use client";

import { Team } from "@/lib/api/teams";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, Calendar, Trash2, UserPlus } from "lucide-react";
import { format } from "date-fns";

/**
 * TeamList Component
 *
 * Displays a list of teams with details and actions.
 *
 * Task: T090 [P] [US2] - TeamList component
 * References:
 * - frontend/lib/api/teams.ts
 * - ADR-001: Multi-Tenant Data Isolation Strategy
 * - ADR-002: RBAC Middleware Architecture
 */

interface TeamListProps {
  teams: Team[];
  onSelect: (team: Team) => void;
  onDelete?: (teamId: string) => void;
  onAddMember?: (teamId: string) => void;
  isLoading?: boolean;
}

export function TeamList({
  teams,
  onSelect,
  onDelete,
  onAddMember,
  isLoading = false,
}: TeamListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-6 bg-gray-200 rounded w-1/3"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3 mt-2"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (teams.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 border border-dashed border-neutral-800 bg-[#050505]">
        <Users className="h-10 w-10 text-neutral-700 mb-4" />
        <p className="text-neutral-500 font-mono text-[10px] uppercase tracking-widest text-center">
          No tactical units detected.
          <br />
          Deploy new unit to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-0 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 border-t border-l border-white/10">
      {teams.map((team) => (
        <div
          key={team.id}
          className={`
            group relative bg-black border-r border-b border-white/10 p-6 transition-all duration-200 cursor-pointer
            hover:bg-[#050505] hover:border-white/40
            ${team.deleted_at ? 'opacity-40 grayscale' : 'opacity-100'}
          `}
          onClick={() => onSelect(team)}
        >
          {/* Decorative Corner */}
          <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/0 group-hover:border-white/40 transition-colors"></div>

          <div className="flex flex-col h-full">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Users className="h-3.5 w-3.5 text-white" />
                  <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-white">
                    {team.name}
                  </h3>
                </div>
                <div className="text-[9px] font-mono text-neutral-600 uppercase tracking-tight">
                  Unit_ID // {team.id.substring(0, 13)}
                </div>
              </div>
              {team.deleted_at && (
                <span className="px-1.5 py-0.5 border border-red-900/50 bg-red-950/20 text-[8px] font-bold text-red-500 uppercase tracking-widest">
                  Offline
                </span>
              )}
            </div>

            {team.description && (
              <p className="text-[10px] font-mono text-neutral-500 mb-6 line-clamp-2 leading-relaxed uppercase">
                {team.description}
              </p>
            )}

            <div className="mt-auto flex items-center justify-between">
              <div className="flex items-center gap-2 text-[9px] font-mono text-neutral-600 uppercase">
                <Calendar className="h-3 w-3" />
                {format(new Date(team.created_at), "dd.MM.yyyy")}
              </div>
              
              <div className="text-[8px] font-bold text-neutral-700 uppercase tracking-widest group-hover:text-white transition-colors">
                Link_Unit {'>'}
              </div>
            </div>

            {!team.deleted_at && (
              <div className="mt-6 pt-4 border-t border-white/5 opacity-0 group-hover:opacity-100 transition-all space-y-2">
                {onAddMember && (
                  <button
                    className="w-full flex items-center justify-center gap-2 py-1.5 text-[9px] font-bold uppercase tracking-widest border border-white/10 text-neutral-400 hover:text-white hover:border-white transition-all"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAddMember(team.id);
                    }}
                  >
                    <UserPlus className="h-3 w-3" />
                    Assign_Member
                  </button>
                )}

                {onDelete && (
                  <button
                    className="w-full flex items-center justify-center gap-2 py-1.5 text-[9px] font-bold uppercase tracking-widest text-red-900/60 hover:text-red-500 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      onDelete(team.id);
                    }}
                  >
                    <Trash2 className="h-3 w-3" />
                    Purge_Unit
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
