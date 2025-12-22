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
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import { ChatInterface } from "@/components/chat/ChatInterface";
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
  MessageSquare,
  PanelRightOpen,
  PanelRightClose,
  ChevronRight,
  Database,
  Lock
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

export default function DashboardPage() {
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
  } = useTasks({ userId: user?.id || null, filters: apiFilters });

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
    tasks.forEach((task) => task.tags.forEach((tag) => tagSet.add(tag)));
    return Array.from(tagSet).sort();
  }, [tasks]);

  const filteredTasks = useMemo(() => {
    if (selectedTags.length <= 1) return tasks;
    return tasks.filter((task) => selectedTags.every((tag) => task.tags.includes(tag)));
  }, [tasks, selectedTags]);

  const overdueCount = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return tasks.filter((task) => {
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
      {tasksLoading ? (
          <div className="opacity-50 grayscale">
              <DashboardSkeleton />
          </div>
      ) : tasks.length === 0 ? (
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
                  />
              )}
          </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-white selection:text-black flex overflow-hidden">

      {/* --- BACKGROUND GRID --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#222_1px,transparent_1px),linear-gradient(to_bottom,#222_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-30"></div>
      </div>

      {/* --- SIDEBAR --- */}
      <aside className="hidden lg:flex flex-col w-64 bg-black border-r border-white/10 z-30">
        <div className="h-16 flex items-center px-6 border-b border-white/10 bg-[#050505]">
           <div className="w-4 h-4 bg-white flex items-center justify-center mr-3">
              <div className="w-1.5 h-1.5 bg-black"></div>
           </div>
           <span className="font-bold text-xs uppercase tracking-[0.2em] text-white">Evolved</span>
        </div>

        <div className="flex-1 py-6 px-0 space-y-1">
          <button
            onClick={() => setShowChatPanel(false)}
            className={`w-full flex items-center gap-3 px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${!showChatPanel ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Tasks
          </button>
          <button
            onClick={() => setShowChatPanel(true)}
            className={`w-full flex items-center gap-3 px-6 py-3 text-[10px] font-bold uppercase tracking-widest transition-all border-l-2 ${showChatPanel ? 'bg-white/5 border-white text-white' : 'border-transparent text-neutral-500 hover:text-white hover:bg-white/[0.02]'}`}
          >
            <MessageSquare className="w-4 h-4" />
            AI Chat
          </button>
        </div>

        <div className="p-6 border-t border-white/10">
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
        </div>
      </aside>

      {/* --- MAIN CONTENT --- */}
      <main className="flex-1 flex flex-col relative z-10 min-w-0">
        
        {/* --- HEADER HUD --- */}
        <header className="h-16 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6 md:px-8">
           <div className="flex items-center gap-2 text-[10px] font-mono text-neutral-500 uppercase tracking-widest">
              <span>System</span>
              <ChevronRight className="w-3 h-3" />
              <span className="text-white font-bold">{showChatPanel ? 'AI Chat' : 'Dashboard'}</span>
           </div>
           
           <div className="lg:hidden text-white">
               <Terminal className="w-5 h-5" />
           </div>
        </header>

        {showChatPanel ? (
          // === CHAT MODE ===
          <div className="flex-1 flex overflow-hidden relative">
             
             {/* Chat Area - Shrinks when drawer opens */}
             <div className="flex-1 flex flex-col relative bg-black min-w-0 transition-all duration-300 ease-in-out">
                <div className="px-6 py-3 border-b border-white/10 bg-[#050505] flex justify-between items-center">
                   <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-green-500 animate-pulse"></div>
                      <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-green-500">AI Online</span>
                   </div>
                   {!showTaskDrawer && (
                       <button onClick={() => setShowTaskDrawer(true)} className="flex items-center gap-2 text-[10px] font-bold uppercase bg-neutral-900 border border-neutral-800 px-3 py-1.5 hover:border-white transition-colors">
                          <PanelRightOpen className="w-3 h-3" /> View Tasks
                       </button>
                   )}
                </div>

                <div className="flex-1 relative z-10 overflow-hidden">
                    {user?.id && <ChatInterface userId={user.id} />}
                </div>
             </div>

             {/* Preview Drawer - READ ONLY MODE */}
             <div 
                className={`
                    fixed inset-y-0 right-0 z-50 bg-[#050505] border-l border-white/10 transition-all duration-300 ease-in-out
                    lg:static lg:z-0
                    ${showTaskDrawer 
                        ? 'translate-x-0 w-full lg:w-[450px]' 
                        : 'translate-x-full lg:translate-x-0 lg:w-0 lg:border-l-0 overflow-hidden'
                    }
                `}
             >
                 <div className="w-full lg:w-[450px] h-full flex flex-col">
                    <div className="h-12 border-b border-white/10 flex items-center justify-between px-4 bg-black">
                       <div className="flex items-center gap-2">
                          <Lock className="w-3 h-3 text-neutral-500" />
                          <span className="text-[10px] font-bold uppercase tracking-widest text-neutral-500">Read Only</span>
                       </div>
                       <button onClick={() => setShowTaskDrawer(false)} className="text-neutral-500 hover:text-white"><PanelRightClose className="w-4 h-4"/></button>
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 bg-black">
                       {/* PASSING READONLY=TRUE HERE */}
                       <TaskListRenderer readOnly={true} />
                    </div>
                 </div>
             </div>

          </div>
        ) : (
          // === DASHBOARD MODE ===
          <div className="flex-1 overflow-y-auto bg-black p-6 md:p-8">
             <div className="max-w-[1600px] mx-auto space-y-8">
                
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                   <StatCard
                      label="User"
                      value={user?.name?.split(' ')[0] || "User"}
                      subtext="Status: Active"
                      icon={Terminal}
                   />
                   <StatCard
                      label="Active Tasks"
                      value={tasks.filter(t => !t.is_complete).length}
                      subtext="Not Completed"
                      icon={Activity}
                   />
                   <StatCard
                      label="Overdue Tasks"
                      value={overdueCount}
                      subtext={overdueCount > 0 ? "Need Attention" : "All on Track"}
                      icon={AlertTriangle}
                      alert={overdueCount > 0}
                   />
                </div>

                {/* === UPDATED COMMAND BAR (Fixed Fitting) === */}
                {!tasksLoading && (
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
                )}

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
                                 due_date: editingTask.due_date || undefined
                               }}
                               onSubmit={handleEditTask}
                               onCancel={handleCancelEdit}
                            />
                         </div>
                      </div>
                   ) : showForm ? (
                      <div className="border border-white/10 bg-[#050505] p-6 animate-in fade-in slide-in-from-top-2">
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