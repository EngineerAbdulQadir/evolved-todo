"use client";

import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useMemo, useRef } from "react";
import toast from "react-hot-toast";
import { TaskList } from "@/components/tasks/TaskList";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskFilters } from "@/components/tasks/TaskFilters";
import { SortDropdown, type SortOption } from "@/components/tasks/SortDropdown";
import { DashboardSkeleton } from "@/components/common/LoadingSkeleton";
import { Loader3D } from "@/components/common/Loader3D";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { ChatInterface } from "@/components/chat/ChatInterface";

// DISABLED: Multi-tenant imports
// import { OrganizationList } from "@/components/organizations/OrganizationList";
// import { CreateOrganizationDialog } from "@/components/organizations/CreateOrganizationDialog";
// import { InviteMemberDialog } from "@/components/invitations/InviteMemberDialog";
// import { listOrganizations, deleteOrganization, type Organization } from "@/lib/api/organizations";
// import { switchContext } from "@/lib/api/auth";
// import { TeamList } from "@/components/teams/TeamList";
// import { CreateTeamDialog } from "@/components/teams/CreateTeamDialog";
// import { listTeams, deleteTeam, type Team as TeamType } from "@/lib/api/teams";
// import { getOrganization } from "@/lib/api/organizations";
// import { ProjectList } from "@/components/projects/ProjectList";
// import { CreateProjectDialog } from "@/components/projects/CreateProjectDialog";
// import { useTeams } from "@/hooks/useTeams";
// import { useProjects } from "@/hooks/useProjects";

import type { Task, Priority } from "@/types/task";
import {
  Terminal,
  Plus,
  LayoutDashboard,
  LogOut,
  AlertTriangle,
  Activity,
  Search,
  X,
  Briefcase,
  PanelRightOpen,
  PanelRightClose,
  ChevronRight,
  Database,
  Lock,
  CheckSquare,
  Menu,
  ChevronLeft,
  Building2
} from "lucide-react";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Float, MeshDistortMaterial, MeshWobbleMaterial, Stars } from "@react-three/drei";
import * as THREE from "three";
import { 
  Shield,
  Users,
  Layers
} from "lucide-react";

// --- SUB-COMPONENT: SHARP STAT CARD ---
const StatCard = ({ label, value, subtext, icon: Icon, alert = false }: any) => (
  <div className={`relative p-6 border group transition-colors ${alert ? 'bg-red-950/10 border-red-900/50' : 'bg-[#050505] border-white/10 hover:border-white/20'}`}>
    {/* Decorative Corners */}
    <div className={`absolute top-0 left-0 w-2 h-2 border-t border-l ${alert ? 'border-red-500' : 'border-white/40'}`}></div>
    <div className={`absolute top-0 right-0 w-2 h-2 border-t border-r ${alert ? 'border-red-500' : 'border-white/40'}`}></div>
    <div className={`absolute bottom-0 left-0 w-2 h-2 border-b border-l ${alert ? 'border-red-500' : 'border-white/40'}`}></div>
    <div className={`absolute bottom-0 right-0 w-2 h-2 border-b border-r ${alert ? 'border-red-500' : 'border-white/40'}`}></div>

    <div className="flex justify-between items-start mb-4">
      <h3 className={`text-[10px] font-bold uppercase tracking-widest ${alert ? 'text-red-400' : 'text-neutral-500'}`}>{label}</h3>
      <Icon className={`w-4 h-4 ${alert ? 'text-red-500' : 'text-neutral-600'}`} />
    </div>
    <div className={`text-3xl font-mono font-bold ${alert ? 'text-red-500' : 'text-white'}`}>
      {value}
    </div>
    <div className={`mt-2 text-[9px] font-mono uppercase tracking-wide ${alert ? 'text-red-400/70' : 'text-neutral-600'}`}>
      {subtext}
    </div>
  </div>
);

// DISABLED: Multi-tenant BlueprintStats
// const BlueprintStats = () => (
//   <div className="flex flex-row items-center justify-center gap-x-24 py-14 px-4 border-y border-white/5 animate-in fade-in duration-1000 overflow-x-auto no-scrollbar">
//     {/* Projects */}
//     <div className="flex flex-col items-center group shrink-0">
//       <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-[0.4em] mb-3 transition-colors group-hover:text-neutral-300">System // Total Projects</div>
//       <div className="flex items-center gap-3">
//         <span className="text-6xl font-mono font-bold text-white tracking-tighter tabular-nums">00</span>
//         <div className="border-b border-white/20 pb-1 mt-3">
//           <span className="text-[9px] text-neutral-600 font-mono uppercase tracking-widest">Units</span>
//         </div>
//       </div>
//     </div>
//
//     {/* Team */}
//     <div className="flex flex-col items-center group shrink-0">
//       <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-[0.4em] mb-3 transition-colors group-hover:text-neutral-300">Network // Team Members</div>
//       <div className="flex items-center gap-3">
//         <span className="text-6xl font-mono font-bold text-white tracking-tighter tabular-nums">00</span>
//         <div className="border-b border-white/20 pb-1 mt-3">
//           <span className="text-[9px] text-neutral-600 font-mono uppercase tracking-widest">Active</span>
//         </div>
//       </div>
//     </div>
//
//     {/* Workers */}
//     <div className="flex flex-col items-center group shrink-0">
//       <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-[0.4em] mb-3 transition-colors group-hover:text-neutral-300">Assets // Total Workers</div>
//       <div className="flex items-center gap-3">
//         <span className="text-6xl font-mono font-bold text-white tracking-tighter tabular-nums">00</span>
//         <div className="border-b border-white/20 pb-1 mt-3">
//           <span className="text-[9px] text-neutral-600 font-mono uppercase tracking-widest">Assigned</span>
//         </div>
//       </div>
//     </div>
//   </div>
// );

// --- SUB-COMPONENT: ACTIVE PROJECTS PANEL ---
const ActiveProjectsPanel = () => (
  <div className="relative bg-[#050505] border border-white/10 p-6 transition-colors hover:border-white/20 flex flex-col h-full group">
    {/* Decorative Corners */}
    <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
    <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
    <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
    <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>

    <div className="flex justify-between items-start mb-6">
      <div>
        <h2 className="text-xl font-mono font-bold text-white tracking-tight">Active Projects</h2>
        <p className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest mt-1">LATEST DEVELOPMENTS</p>
      </div>
      <div className="px-2 py-0.5 border border-green-900/50 bg-green-950/20 text-[8px] font-bold text-green-500 rounded-none uppercase tracking-widest">
        Online
      </div>
    </div>

    <div className="flex-1 flex items-center justify-center border border-dashed border-white/5 rounded-none opacity-20 my-4 min-h-[120px]">
      <p className="text-[10px] font-mono uppercase tracking-widest text-white">No active units</p>
    </div>

    <div className="mt-auto pt-4 border-t border-white/5 flex justify-center">
      <button className="text-[10px] font-bold text-neutral-500 hover:text-white flex items-center gap-2 transition-colors uppercase tracking-widest">
        View All Projects <ChevronRight className="w-3 h-3" />
      </button>
    </div>
  </div>
);

// --- SUB-COMPONENT: SYSTEM LOGS PANEL ---
const SystemLogsPanel = () => (
  <div className="relative bg-[#050505] border border-white/10 p-6 transition-colors hover:border-white/20 flex flex-col h-full group">
    {/* Decorative Corners */}
    <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
    <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
    <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
    <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>

    <div className="flex justify-between items-start mb-6">
      <div>
        <h2 className="text-xl font-mono font-bold text-white tracking-tight">System Logs</h2>
        <p className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest mt-1">LIVE EVENT STREAM</p>
      </div>
      <div className="px-2 py-0.5 border border-green-900/50 bg-green-950/20 text-[8px] font-bold text-green-500 rounded-none uppercase tracking-widest">
        Online
      </div>
    </div>

    <div className="flex-1 flex items-center justify-center border border-dashed border-white/5 rounded-none opacity-20 my-4 min-h-[120px]">
      <p className="text-[10px] font-mono uppercase tracking-widest text-white">No active logs</p>
    </div>

    <div className="mt-auto pt-4 border-t border-white/5 flex justify-end">
      <button className="text-[10px] font-bold text-neutral-500 hover:text-white flex items-center gap-2 transition-colors uppercase tracking-widest">
        Full Audit Log <ChevronRight className="w-3 h-3" />
      </button>
    </div>
  </div>
);

// --- SUB-COMPONENT: 3D BACKGROUND ---
const ThreeDBackground = () => {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none opacity-40">
      <Canvas camera={{ position: [0, 0, 5], fov: 75 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        <Float speed={2} rotationIntensity={1} floatIntensity={1}>
          <mesh position={[2, 1, -2]} rotation={[0.5, 0.5, 0]}>
            <boxGeometry args={[1, 1, 1]} />
            <MeshWobbleMaterial color="#ffffff" speed={1} factor={0.2} wireframe />
          </mesh>
        </Float>
        <Float speed={1.5} rotationIntensity={0.5} floatIntensity={0.5}>
          <mesh position={[-3, -2, -3]} rotation={[1, 0, 0.5]}>
            <octahedronGeometry args={[1, 0]} />
            <MeshDistortMaterial color="#444444" speed={2} distort={0.3} wireframe />
          </mesh>
        </Float>
        <gridHelper args={[20, 20, 0xffffff, 0x222222]} rotation={[Math.PI / 2, 0, 0]} position={[0, 0, -5]} />
      </Canvas>
    </div>
  );
};

export function DashboardContent() {
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);
  
  // Toggle for Chat Mode
  const [showChatPanel, setShowChatPanel] = useState(false);
  // Toggle for the Preview Drawer
  const [showTaskDrawer, setShowTaskDrawer] = useState(false);
  // Sidebar collapse state
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  // Current view: 'overview' or 'tasks' (chat is handled via showChatPanel)
  const [currentView, setCurrentView] = useState<'overview' | 'tasks'>('overview');

  // --- TRANSITION LOADING ---
  const [viewTransitionLoading, setViewTransitionLoading] = useState(false);
  const prevView = useRef(currentView);
  const prevChat = useRef(showChatPanel);

  useEffect(() => {
    if (viewTransitionLoading) {
      const timer = setTimeout(() => setViewTransitionLoading(false), 2000);
      return () => clearTimeout(timer);
    }
  }, [viewTransitionLoading]);

  // DISABLED: Multi-tenant state
  // const [organizations, setOrganizations] = useState<Organization[]>([]);
  // const [isOrgLoading, setIsOrgLoading] = useState(false);
  // const [orgError, setOrgError] = useState<string | null>(null);
  // const [isCreateOrgDialogOpen, setIsCreateOrgDialogOpen] = useState(false);
  // const [selectedOrg, setSelectedOrg] = useState<Organization | null>(null);
  // const [isInviteOrgDialogOpen, setIsInviteOrgDialogOpen] = useState(false);
  // const [isOrgDropdownOpen, setIsOrgDropdownOpen] = useState(false);
  // const [hasCreatedDefaultOrg, setHasCreatedDefaultOrg] = useState(false);
  // const [teamsForTeams, setTeamsForTeams] = useState<TeamType[]>([]);
  // const [isTeamsLoading, setIsTeamsLoading] = useState(false);
  // const [teamsError, setTeamsError] = useState<string | null>(null);
  // const [isCreateTeamDialogOpen, setIsCreateTeamDialogOpen] = useState(false);
  // const { projects, loading: projectsLoading, fetchProjects, createProject } = useProjects();
  // const { teams: teamsForProjects, loading: projectsTeamsLoading, fetchTeams: fetchProjectsTeams } = useTeams();
  // const [selectedTeamIdForProjects, setSelectedTeamIdForProjects] = useState<string | null>(null);
  // const [isCreateProjectDialogOpen, setIsCreateProjectDialogOpen] = useState(false);

  // DISABLED: Multi-tenant data loading and handlers
  // All organization, team, and project logic has been removed

  const handleViewChange = (newView: 'overview' | 'tasks' | 'chat') => {
    if (
      (newView === 'chat' && showChatPanel) ||
      (newView === 'overview' && !showChatPanel && currentView === 'overview') ||
      (newView === 'tasks' && !showChatPanel && currentView === 'tasks')
    ) return;

    // Set loading state IMMEDIATELY to avoid flicker
    setViewTransitionLoading(true);

    if (newView === 'chat') {
      setShowChatPanel(true);
    } else {
      setShowChatPanel(false);
      setCurrentView(newView as 'overview' | 'tasks');
    }
  };

  // --- LOGIC: FILTER STATE ---
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "completed">(() => {
    const status = searchParams.get("status");
    return (status === "active" || status === "completed") ? status : "all";
  });
  const [priorityFilter, setPriorityFilter] = useState<Priority | "all">(() => {
    const priority = searchParams.get("priority");
    return (priority === "high" || priority === "medium" || priority === "low") ? priority as Priority : "all";
  });
  const [selectedTags, setSelectedTags] = useState<string[]>(() => {
    const tags = searchParams.get("tags");
    return tags ? tags.split(",") : [];
  });
  
  // --- SEARCH LOGIC ---
  const [searchQuery, setSearchQuery] = useState<string>(() => {
    return searchParams.get("search") || "";
  });
  const [inputValue, setInputValue] = useState<string>(searchQuery);

  useEffect(() => {
    setInputValue(searchQuery);
  }, [searchQuery]);

  const [sortOption, setSortOption] = useState<SortOption>(() => {
    const sortBy = searchParams.get("sort_by");
    const sortOrder = searchParams.get("sort_order");
    if (sortBy && sortOrder) {
      return { field: sortBy as any, order: sortOrder as any, label: "" };
    }
    return { field: "created_at", order: "desc", label: "Newest First" };
  });

  // --- LOGIC: API FILTERS ---
  const apiFilters = useMemo(() => {
    const filters: any = {};
    if (statusFilter === "active") filters.completed = false;
    if (statusFilter === "completed") filters.completed = true;
    if (priorityFilter !== "all") filters.priority = priorityFilter;
    if (selectedTags.length > 0) filters.tag = selectedTags[0];
    if (searchQuery) filters.search = searchQuery;
    filters.sort_by = sortOption.field;
    filters.sort_order = sortOption.order;
    return Object.keys(filters).length > 0 ? filters : undefined;
  }, [statusFilter, priorityFilter, selectedTags, searchQuery, sortOption]);

  const {
    tasks,
    isLoading: tasksLoading,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
    refetch: refetchTasks,
  } = useTasks({ userId: user?.id || null, filters: apiFilters });

  const isAnyLoading = viewTransitionLoading || tasksLoading;

  // --- LOGIC: REFETCH TASKS WHEN RETURNING FROM CHAT ---
  const previousChatPanel = useRef(showChatPanel);
  useEffect(() => {
    // If switching from chat to dashboard, refetch tasks
    if (previousChatPanel.current === true && showChatPanel === false) {
      refetchTasks();
    }
    previousChatPanel.current = showChatPanel;
  }, [showChatPanel, refetchTasks]);

  // --- LOGIC: AUTO-PREVIEW ---
  const isFirstRender = useRef(true);
  useEffect(() => {
    if (!tasksLoading) {
      if (isFirstRender.current) {
        isFirstRender.current = false;
      } else if (showChatPanel) {
        setShowTaskDrawer(true);
      }
    }
  }, [tasks, tasksLoading, showChatPanel]);

  // --- LOGIC: DATA PROCESSING ---
  const availableTags = useMemo(() => {
    const tagSet = new Set<string>();
    tasks
      .filter(task => task) // Filter out undefined/null tasks
      .forEach((task) => task.tags.forEach((tag) => tagSet.add(tag)));
    return Array.from(tagSet).sort();
  }, [tasks]);

  const filteredTasks = useMemo(() => {
    const validTasks = tasks.filter(task => task); // Filter out undefined/null tasks
    if (selectedTags.length <= 1) return validTasks;
    return validTasks.filter((task) => selectedTags.every((tag) => task.tags.includes(tag)));
  }, [tasks, selectedTags]);

  const overdueCount = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return tasks
      .filter(task => task) // Filter out undefined/null tasks
      .filter((task) => {
        if (task.is_complete || !task.due_date) return false;
        const dueDate = new Date(task.due_date);
        dueDate.setHours(0, 0, 0, 0);
        return dueDate < today;
      }).length;
  }, [tasks]);

  // --- LOGIC: URL UPDATES ---
  useEffect(() => {
    const params = new URLSearchParams();
    if (statusFilter !== "all") params.set("status", statusFilter);
    if (priorityFilter !== "all") params.set("priority", priorityFilter);
    if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));
    if (searchQuery) params.set("search", searchQuery);
    if (sortOption.field !== "created_at" || sortOption.order !== "desc") {
      params.set("sort_by", sortOption.field);
      params.set("sort_order", sortOption.order);
    }
    const queryString = params.toString();
    const newUrl = queryString ? `?${queryString}` : window.location.pathname;
    if (window.location.search !== `?${queryString}`) {
      window.history.replaceState(null, "", newUrl);
    }
  }, [statusFilter, priorityFilter, selectedTags, searchQuery, sortOption]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push("/login");
  }, [isAuthenticated, authLoading, router]);

  if (authLoading) return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white font-mono text-xs uppercase tracking-widest">
      <Terminal className="w-4 h-4 mr-2 animate-pulse" /> Loading...
    </div>
  );
  
  if (!isAuthenticated) return null;

  // --- HANDLERS ---
  const handleCreateTask = async (taskData: any) => {
    try {
      await createTask(taskData);
      setShowForm(false);
      toast.success("Task created.");
    } catch (error) {
      toast.error("Failed to create task.");
    }
  };

  const handleEditTask = async (taskData: any) => {
    if (editingTask) {
      try {
        await updateTask(editingTask.id, taskData);
        setEditingTask(null);
        toast.success("Task updated.");
      } catch (error) {
        toast.error("Update failed.");
      }
    }
  };

  const handleEditClick = (task: Task) => { setEditingTask(task); setShowForm(false); };
  const handleCancelEdit = () => { setEditingTask(null); };
  const handleDeleteTask = (taskId: number) => { setTaskToDelete(taskId); };
  
  const confirmDelete = async () => {
    if (taskToDelete) {
      try {
        await deleteTask(taskToDelete);
        toast.success("Task deleted.");
        setTaskToDelete(null);
      } catch (error) {
        toast.error("Failed to delete task.");
      }
    }
  };

  const cancelDelete = () => { setTaskToDelete(null); };
  
  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) => prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]);
  };

  const handleClearFilters = () => {
    setStatusFilter("all");
    setPriorityFilter("all");
    setSelectedTags([]);
    setSearchQuery(""); 
    setInputValue("");  
    setSortOption({ field: "created_at", order: "desc", label: "Newest First" });
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSearchQuery(inputValue); 
  };

  const handleClearSearch = () => {
    setInputValue("");
    setSearchQuery("");
  };

  // --- STYLES FOR SHARP THEME ---
  const sharpThemeOverrides = `
    [&_input]:rounded-none [&_input]:border-neutral-800 [&_input]:bg-[#050505] [&_input]:focus:border-white [&_input]:focus:ring-0
    [&_select]:rounded-none [&_select]:border-neutral-800 [&_select]:bg-[#050505] [&_select]:focus:border-white
    [&_textarea]:rounded-none [&_textarea]:border-neutral-800 [&_textarea]:bg-[#050505] [&_textarea]:focus:border-white
    [&_button]:rounded-none 
    [&_.task-card]:rounded-none [&_.task-card]:border-white/10 [&_.task-card]:bg-black [&_.task-card]:hover:border-white/30
    [&_input[type=checkbox]]:rounded-none [&_input[type=checkbox]]:border-neutral-600 [&_input[type=checkbox]]:text-white
    [&_.rounded-lg]:rounded-none [&_.rounded-md]:rounded-none [&_.rounded-xl]:rounded-none
    [&_.shadow-sm]:shadow-none [&_.shadow-md]:shadow-none [&_.shadow-lg]:shadow-none
    [&_div.border]:border-neutral-800 [&_div.border]:bg-black
  `;

  // --- TASK LIST RENDERER (Updated for Read-Only Logic) ---
  const TaskListRenderer = ({ readOnly = false }: { readOnly?: boolean }) => (
    <div className={`
        ${sharpThemeOverrides} 
        ${readOnly ? `
            [&_.task-card]:pointer-events-none 
            [&_button]:hidden 
            [&_input[type=checkbox]]:hidden 
            [&_.task-card]:border-l-4 [&_.task-card]:border-l-neutral-700
            [&_.task-card]:opacity-90
        ` : ''}
    `}>
      {tasks.length === 0 ? (
          (statusFilter !== "all" || priorityFilter !== "all" || selectedTags.length > 0 || searchQuery) ? (
              <div className="flex flex-col items-center justify-center py-20 border border-dashed border-neutral-800 bg-[#050505]">
                  <Search className="w-8 h-8 text-neutral-600 mb-4" />
                  <p className="text-neutral-400 font-mono text-xs uppercase tracking-widest mb-4">No matching records found</p>
                  {!readOnly && (
                      <button
                          onClick={handleClearFilters}
                          className="text-[10px] font-bold text-black bg-white px-4 py-2 uppercase hover:bg-neutral-200 transition-colors"
                      >
                          Reset Filters
                      </button>
                  )}
              </div>
          ) : !showForm ? (
              <div className="flex flex-col items-center justify-center py-20 border border-dashed border-neutral-800 bg-[#050505]">
                  <Database className="w-8 h-8 text-neutral-600 mb-4" />
                  <p className="text-neutral-400 font-mono text-xs uppercase tracking-widest">Database Empty</p>
              </div>
          ) : null
      ) : (
          <div className="space-y-0 border-t border-neutral-800">
              {filteredTasks.length === 0 ? (
                  <div className="py-12 text-center text-neutral-500 font-mono text-xs">NO RESULTS</div>
              ) : (
                  <TaskList
                      tasks={filteredTasks}
                      onToggleComplete={readOnly ? () => {} : toggleComplete}
                      onDelete={readOnly ? () => {} : handleDeleteTask}
                      onEdit={readOnly ? () => {} : handleEditClick}
                      onAssignTask={readOnly ? () => {} : (taskId) => console.log('Assign task:', taskId)} // Placeholder for now
                  />
              )}
          </div>
      )}
    </div>
  );

  // DISABLED: Multi-tenant renderer components removed
  // OrganizationsRenderer, TeamsRenderer, and ProjectsRenderer have been removed

  return (
    <div className="h-screen bg-black text-white font-sans selection:bg-white selection:text-black flex overflow-hidden">

      {/* --- BACKGROUND 3D --- */}
      <ThreeDBackground />

      {/* --- SIDEBAR --- */}
      <aside className={`hidden lg:flex flex-col ${isSidebarCollapsed ? 'w-16' : 'w-64'} bg-black border-r border-white/10 z-30 transition-all duration-300`}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-white/10 bg-[#050505]">
           {!isSidebarCollapsed && (
             <div className="flex items-center">
               <div className="w-4 h-4 bg-white flex items-center justify-center mr-3">
                  <div className="w-1.5 h-1.5 bg-black"></div>
               </div>
               <span className="font-bold text-xs uppercase tracking-[0.2em] text-white">Evolved</span>
             </div>
           )}
           <button
             onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
             className="text-neutral-500 hover:text-white transition-colors ml-auto"
             title={isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
           >
             {isSidebarCollapsed ? <Menu className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
           </button>
        </div>

        <div className="flex-1 py-6 px-0 space-y-1">
          <button
            onClick={() => handleViewChange('overview')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel && currentView === 'overview' ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Overview"
          >
            <LayoutDashboard className="w-4 h-4" />
            {!isSidebarCollapsed && 'Overview'}
          </button>
          <button
            onClick={() => handleViewChange('chat')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${showChatPanel ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Workspace"
          >
            <Briefcase className="w-4 h-4" />
            {!isSidebarCollapsed && 'Workspace'}
          </button>
          <button
            onClick={() => handleViewChange('tasks')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel && currentView === 'tasks' ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Tasks"
          >
            <CheckSquare className="w-4 h-4" />
            {!isSidebarCollapsed && 'Tasks'}
          </button>
          {/* DISABLED: Multi-tenant features temporarily disabled for debugging */}
          {/* <button
            onClick={() => handleViewChange('organizations')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel && currentView === 'organizations' ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Organizations"
          >
            <Building2 className="w-4 h-4" />
            {!isSidebarCollapsed && 'Organizations'}
          </button>
          <button
            onClick={() => handleViewChange('projects')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel && currentView === 'projects' ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Projects"
          >
            <Layers className="w-4 h-4" />
            {!isSidebarCollapsed && 'Projects'}
          </button>
          <button
            onClick={() => handleViewChange('teams')}
            className={`w-full flex items-center ${isSidebarCollapsed ? 'justify-center' : 'gap-3'} px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel && currentView === 'teams' ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
            title="Teams"
          >
            <Users className="w-4 h-4" />
            {!isSidebarCollapsed && 'Teams'}
          </button> */}
        </div>

        <div className={`p-6 border-t border-white/10 ${isSidebarCollapsed ? 'px-2' : ''}`}>
           {!isSidebarCollapsed ? (
             <>
               <div className="mb-4">
                  <div className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest mb-1">User</div>
                  <div className="text-sm font-bold text-white truncate">{user?.name || "Unknown"}</div>
                  <div className="text-[10px] text-neutral-600 font-mono truncate">{user?.email}</div>
               </div>
               <button
                onClick={() => logout()}
                className="w-full flex items-center justify-center gap-2 py-2 text-[10px] font-bold uppercase tracking-widest bg-neutral-900 border border-neutral-800 text-neutral-400 hover:bg-white hover:text-black hover:border-white transition-all"
              >
                <LogOut className="w-3 h-3" /> Sign Out
              </button>
             </>
           ) : (
             <button
              onClick={() => logout()}
              className="w-full flex items-center justify-center py-2 text-neutral-400 hover:text-white transition-all"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
           )}
        </div>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative z-10 min-w-0">
        
        {/* --- HEADER HUD --- */}
        <header className="h-16 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6 md:px-8">
           <div className="flex items-center gap-2 text-[10px] font-mono text-neutral-500 uppercase tracking-widest">
              <span>System</span>
              <ChevronRight className="w-3 h-3" />
                            <span className="text-white font-bold">
                              {showChatPanel ? 'Workspace' :
                               currentView === 'overview' ? 'Overview' :
                               currentView === 'tasks' ? 'Tasks' : 'Dashboard'}
                            </span>
                         </div>

                         {/* DISABLED: Organization Selector */}
                         {/* <div className="flex items-center gap-4">
                            <div className="relative">
                              <button
                                onClick={() => setIsOrgDropdownOpen(!isOrgDropdownOpen)}
                                className="flex items-center gap-2 px-4 py-2 bg-neutral-900 border border-white/10 hover:border-white/30 transition-colors text-sm"
                                disabled={isOrgLoading}
                              >
                                <Building2 className="w-4 h-4 text-neutral-400" />
                                <span className="text-white max-w-[150px] truncate hidden sm:inline">
                                  {selectedOrg?.name || "Select Organization"}
                                </span>
                                <ChevronRight className={`w-4 h-4 text-neutral-400 transition-transform ${isOrgDropdownOpen ? 'rotate-90' : ''}`} />
                              </button>

                              {/* Dropdown *\/}
                              {isOrgDropdownOpen && (
                                <div className="absolute right-0 mt-2 w-64 bg-neutral-900 border border-white/10 shadow-lg max-h-[400px] overflow-y-auto z-[999]">
                                  {isOrgLoading ? (
                                    <div className="p-4 text-center">
                                      <Terminal className="w-4 h-4 text-white animate-pulse mx-auto" />
                                    </div>
                                  ) : organizations.length === 0 ? (
                                    <div className="p-4 text-center text-neutral-500 text-sm">
                                      No organizations found
                                    </div>
                                  ) : (
                                    <>
                                      {organizations.map((org) => (
                                        <button
                                          key={org.id}
                                          onClick={() => handleSelectOrganization(org)}
                                          className={`w-full text-left px-4 py-3 hover:bg-white/5 transition-colors border-b border-white/5 ${
                                            org.id === selectedOrg?.id
                                              ? "bg-white/10"
                                              : ""
                                          }`}
                                        >
                                          <div className="font-medium text-white text-sm">
                                            {org.name}
                                          </div>
                                          <div className="text-xs text-neutral-500 truncate">
                                            {org.slug}
                                          </div>
                                        </button>
                                      ))}
                                      <button
                                        onClick={() => {
                                          setIsOrgDropdownOpen(false);
                                          handleViewChange('organizations');
                                        }}
                                        className="w-full text-left px-4 py-3 text-sm text-neutral-400 hover:text-white hover:bg-white/5 transition-colors border-t border-white/10"
                                      >
                                        + Manage Organizations
                                      </button>
                                    </>
                                  )}
                                </div>
                              )}
                            </div> */}
                         <div className="flex items-center gap-4">

                            <div className="lg:hidden text-white">
                                <Terminal className="w-5 h-5" />
                            </div>
                         </div>
                                 </header>
                         
                                 {/* --- UNIFIED LOADING OVERLAY --- */}
                                 {isAnyLoading && (
                                   <div className="absolute inset-0 top-16 z-50 flex flex-col items-center justify-center bg-black">
                                      <div className="text-white font-mono text-sm">
                                        <p className="text-neutral-500">
                                          {currentView === 'overview' ? 'Loading overview...' :
                                           currentView === 'tasks' ? 'Loading tasks...' :
                                           'Loading...'}
                                        </p>
                                      </div>
                                   </div>
                                 )}
                         
                                 {showChatPanel ? (                        // === CHAT MODE === (Pure ChatKit Only)
                        <div className="flex-1 flex flex-col overflow-hidden bg-black">
                           {user?.id && <ChatInterface userId={user.id} />}
                        </div>
                                                                      ) : currentView === 'tasks' ? (
                                                                        // === TASKS VIEW === (Task List and Management)
                                                                        <div className={`flex-1 ${ isAnyLoading ? 'overflow-hidden' : 'overflow-y-auto' } bg-black p-6 md:p-8 relative`}>
                                                                           <div className={`max-w-[1600px] mx-auto space-y-8 ${isAnyLoading ? 'hidden' : 'block'}`}>                                               {/* === UPDATED COMMAND BAR (Fixed Fitting) === */}
                                 <div className="flex flex-col lg:flex-row gap-6">
                                    
                                    {/* Left: Standalone Search Input */}
                                    <div className="flex-1 flex items-center h-14 bg-[#050505] border border-white/10 focus-within:border-white transition-colors relative group">
                                       <div className="w-12 h-full flex items-center justify-center text-neutral-500 border-r border-white/5">
                                          <span className="font-mono text-lg">{'>'}</span>
                                       </div>
                                       <form onSubmit={handleSearchSubmit} className="flex-1 h-full flex">
                                          <input
                                             type="text"
                                             value={inputValue}
                                             onChange={(e) => setInputValue(e.target.value)}
                                             placeholder="Search tasks..."
                                             className="w-full h-full bg-transparent border-none text-sm font-mono text-white placeholder-neutral-700 focus:ring-0 px-4"
                                          />
                                       </form>
                                       {inputValue && (
                                           <button onClick={handleClearSearch} className="w-12 h-full flex items-center justify-center text-neutral-500 hover:text-white">
                                              <X className="w-4 h-4" />
                                           </button>
                                       )}
                                    </div>
              
                                    {/* Right: Filters & Sort Group (Fixed Height & Alignment) */}
                                    <div className="flex items-center gap-4 h-14">
                                        <div className={sharpThemeOverrides + " flex gap-4 h-full"}>
                                           {/* Filter Dropdown - Direct placement, no wrapper */}
                                           <div className="h-full">
                                              <TaskFilters
                                                statusFilter={statusFilter}
                                                priorityFilter={priorityFilter}
                                                selectedTags={selectedTags}
                                                availableTags={availableTags}
                                                onStatusChange={setStatusFilter}
                                                onPriorityChange={setPriorityFilter}
                                                onTagToggle={handleTagToggle}
                                                onClearFilters={handleClearFilters}
                                              />
                                           </div>
                                           
                                           {/* Sort Dropdown - Direct placement, no wrapper */}
                                           <div className="h-full">
                                              <SortDropdown value={sortOption} onChange={setSortOption} />
                                           </div>
                                        </div>
                                    </div>
                                 </div>
              
                              {/* Task Creation / Edit Area */}
                              <div className="relative z-10">
                                 {editingTask ? (
                                    <div className="border border-white/10 bg-[#050505] p-6">
                                       <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
                                          <h3 className="text-sm font-bold uppercase tracking-widest text-white flex items-center gap-2">
                                             <Terminal className="w-4 h-4" /> Edit Task
                                          </h3>
                                          <button onClick={handleCancelEdit} className="text-neutral-500 hover:text-white"><X className="w-4 h-4"/></button>
                                       </div>
                                       <div className={sharpThemeOverrides}>
                                          <TaskForm
                                             mode="edit"
                                             initialTask={{
                                               ...editingTask,
                                               description: editingTask.description || "",
                                               due_date: editingTask.due_date || undefined,
                                               due_time: editingTask.due_time || undefined,
                                               priority: editingTask.priority || undefined,
                                               recurrence: editingTask.recurrence || undefined,
                                               recurrence_day: editingTask.recurrence_day || undefined
                                             }}
                                             onSubmit={handleEditTask}
                                             onCancel={handleCancelEdit}
                                          />
                                       </div>
                                    </div>
                                 ) : showForm ? (
                                    <div className="border border-white/10 bg-[#050505] p-6">
                                       <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/10">
                                          <h3 className="text-sm font-bold uppercase tracking-widest text-white flex items-center gap-2">
                                             <Plus className="w-4 h-4" /> New Task
                                          </h3>
                                          <button onClick={() => setShowForm(false)} className="text-neutral-500 hover:text-white"><X className="w-4 h-4"/></button>
                                       </div>
                                       <div className={sharpThemeOverrides}>
                                          <TaskForm onSubmit={handleCreateTask} onCancel={() => setShowForm(false)} />
                                       </div>
                                    </div>
                                 ) : (
                                    <button
                                       onClick={() => setShowForm(true)}
                                       className="w-full h-14 border border-white/10 bg-black hover:bg-white hover:text-black hover:border-white transition-all flex items-center justify-center gap-2 text-xs font-bold uppercase tracking-widest text-neutral-400 group"
                                    >
                                       <Plus className="w-4 h-4 group-hover:scale-110 transition-transform" /> New Task
                                    </button>
                                 )}
                              </div>
              
                              {/* Main List */}
                              <div className="min-h-[400px]">
                                 <TaskListRenderer />
                              </div>
              
                           </div>
                        </div>
                              ) : (
          // === OVERVIEW MODE === (Core Stats + Blueprint Hub)
          <div className={`flex-1 ${ isAnyLoading ? 'overflow-hidden' : 'overflow-y-auto' } bg-black p-6 md:p-12 relative`}>
             <div className={`max-w-[1400px] mx-auto space-y-16 animate-in fade-in duration-700 ${isAnyLoading ? 'hidden' : 'block'}`}>
                
                {/* Dashboard Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                   <StatCard
                      label="Logged In As"
                      value={user?.name?.split(' ')[0] || "User"}
                      subtext="Authenticated"
                      icon={Shield}
                   />
                   <StatCard
                      label="Active Tasks"
                      value={tasks.filter(t => t && !t.is_complete).length}
                      subtext="In Progress"
                      icon={Activity}
                   />
                   <StatCard
                      label="Overdue Tasks"
                      value={overdueCount}
                      subtext={overdueCount > 0 ? "Needs Attention" : "All on Track"}
                      icon={AlertTriangle}
                      alert={overdueCount > 0}
                   />
                </div>

                {/* DISABLED: Blueprint Stats */}
                {/* <BlueprintStats /> */}

                {/* DISABLED: Quick Access Navigation Cards */}
                {/* <div className="space-y-6">
                   <div className="flex items-center justify-between">
                      <h2 className="text-xl font-mono font-bold text-white tracking-tight uppercase">Quick Access</h2>
                      <p className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">Navigate System Modules</p>
                   </div>
                   <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <button
                         onClick={() => handleViewChange('tasks')}
                         className="relative p-6 border border-white/10 bg-[#050505] hover:border-white/30 hover:bg-white/5 transition-all group text-left"
                      >
                         <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
                         <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
                         <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
                         <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>
                         <CheckSquare className="w-8 h-8 text-neutral-500 group-hover:text-white transition-colors mb-4" />
                         <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-2">Tasks</h3>
                         <p className="text-[10px] text-neutral-500 uppercase tracking-wider">Manage workloads</p>
                         <div className="mt-4 text-2xl font-mono font-bold text-white">{tasks.filter(t => t && !t.is_complete).length}</div>
                         <div className="text-[9px] text-neutral-600 uppercase tracking-wide">Active</div>
                      </button>

                      <button
                         onClick={() => handleViewChange('organizations')}
                         className="relative p-6 border border-white/10 bg-[#050505] hover:border-white/30 hover:bg-white/5 transition-all group text-left"
                      >
                         <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
                         <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
                         <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
                         <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>
                         <Building2 className="w-8 h-8 text-neutral-500 group-hover:text-white transition-colors mb-4" />
                         <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-2">Organizations</h3>
                         <p className="text-[10px] text-neutral-500 uppercase tracking-wider">Network registry</p>
                         <div className="mt-4 text-2xl font-mono font-bold text-white">{organizations.length}</div>
                         <div className="text-[9px] text-neutral-600 uppercase tracking-wide">Nodes</div>
                      </button>

                      <button
                         onClick={() => handleViewChange('teams')}
                         className="relative p-6 border border-white/10 bg-[#050505] hover:border-white/30 hover:bg-white/5 transition-all group text-left"
                      >
                         <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
                         <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
                         <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
                         <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>
                         <Users className="w-8 h-8 text-neutral-500 group-hover:text-white transition-colors mb-4" />
                         <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-2">Teams</h3>
                         <p className="text-[10px] text-neutral-500 uppercase tracking-wider">Tactical units</p>
                         <div className="mt-4 text-2xl font-mono font-bold text-white">{teamsForTeams.length}</div>
                         <div className="text-[9px] text-neutral-600 uppercase tracking-wide">Units</div>
                      </button>

                      <button
                         onClick={() => handleViewChange('projects')}
                         className="relative p-6 border border-white/10 bg-[#050505] hover:border-white/30 hover:bg-white/5 transition-all group text-left"
                      >
                         <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
                         <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
                         <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
                         <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>
                         <Layers className="w-8 h-8 text-neutral-500 group-hover:text-white transition-colors mb-4" />
                         <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-2">Projects</h3>
                         <p className="text-[10px] text-neutral-500 uppercase tracking-wider">Deployments</p>
                         <div className="mt-4 text-2xl font-mono font-bold text-white">{projects.length}</div>
                         <div className="text-[9px] text-neutral-600 uppercase tracking-wide">Active</div>
                      </button>

                      <button
                         onClick={() => handleViewChange('chat')}
                         className="relative p-6 border border-white/10 bg-[#050505] hover:border-white/30 hover:bg-white/5 transition-all group text-left md:col-span-2 lg:col-span-4"
                      >
                         <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-white/40"></div>
                         <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-white/40"></div>
                         <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-white/40"></div>
                         <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-white/40"></div>
                         <div className="flex items-center gap-4">
                            <Briefcase className="w-8 h-8 text-neutral-500 group-hover:text-white transition-colors" />
                            <div className="flex-1">
                               <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-1">AI Workspace</h3>
                               <p className="text-[10px] text-neutral-500 uppercase tracking-wider">Natural language command interface</p>
                            </div>
                            <ChevronRight className="w-5 h-5 text-neutral-600 group-hover:text-white transition-colors" />
                         </div>
                      </button>
                   </div>
                </div> */}

                {/* DISABLED: Operational Feed (Active Projects & System Logs) */}
                {/* <div className="pb-12">
                   <ActiveProjectsPanel />
                   <SystemLogsPanel />
                </div> */}

             </div>
          </div>
        )}

      </main>

      {/* Delete Confirmation Dialog */}
      <div className="[&_div[role=dialog]]:rounded-none [&_div[role=dialog]]:border [&_div[role=dialog]]:border-white/20 [&_div[role=dialog]]:bg-black [&_h3]:font-mono [&_h3]:uppercase [&_button]:rounded-none">
          <ConfirmDialog
            isOpen={taskToDelete !== null}
            title="Delete Task"
            message="This task will be permanently deleted."
            confirmText="Delete Task"
            cancelText="Cancel"
            variant="danger"
            onConfirm={confirmDelete}
            onCancel={cancelDelete}
          />
      </div>

    </div>
  );
}