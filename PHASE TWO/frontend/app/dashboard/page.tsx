"use client";

import { useAuth } from "@/hooks/useAuth";
import { useTasks } from "@/hooks/useTasks";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState, useMemo } from "react";
import toast from "react-hot-toast";
import { TaskList } from "@/components/tasks/TaskList";
import { TaskForm } from "@/components/tasks/TaskForm";
import { TaskFilters } from "@/components/tasks/TaskFilters";
import { SearchBar } from "@/components/tasks/SearchBar";
import { SortDropdown, type SortOption } from "@/components/tasks/SortDropdown";
import { DashboardSkeleton } from "@/components/common/LoadingSkeleton";
import { ConfirmDialog } from "@/components/common/ConfirmDialog";
import type { Task, Priority } from "@/types/task";
import { 
  Terminal, 
  Plus, 
  LayoutDashboard, 
  LogOut, 
  AlertTriangle,
  Activity,
  Search,
  X
} from "lucide-react";

export default function DashboardPage() {
  const { user, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);

  // --- LOGIC: FILTER STATE INITIALIZATION ---
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
  const [searchQuery, setSearchQuery] = useState<string>(() => {
    return searchParams.get("search") || "";
  });
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
    error,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  } = useTasks({ userId: user?.id || null, filters: apiFilters });

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
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-cyan-500 font-mono">
      INITIALIZING SYSTEM...
    </div>
  );
  
  if (!isAuthenticated) return null;

  // --- HANDLERS ---
  const handleCreateTask = async (taskData: any) => {
    try {
      await createTask(taskData);
      setShowForm(false);
      toast.success("Task created successfully!");
    } catch (error) {
      toast.error("Failed to create task");
    }
  };

  const handleEditTask = async (taskData: any) => {
    if (editingTask) {
      try {
        await updateTask(editingTask.id, taskData);
        setEditingTask(null);
        toast.success("Task updated successfully!");
      } catch (error) {
        toast.error("Failed to delete task");
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
        toast.success("Task deleted successfully!");
        setTaskToDelete(null);
      } catch (error) {
        toast.error("Failed to delete task");
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
    setSortOption({ field: "created_at", order: "desc", label: "Newest First" });
  };

  // --- STYLES ---
  const inputStyles = `
    [&_input]:bg-slate-950 
    [&_input]:border-slate-700 
    [&_input]:text-white 
    [&_input]:placeholder-slate-500
    [&_textarea]:bg-slate-950 
    [&_textarea]:border-slate-700 
    [&_textarea]:text-white 
    [&_textarea]:placeholder-slate-500
    [&_select]:bg-slate-950 
    [&_select]:border-slate-700 
    [&_select]:text-white 
    [&_option]:bg-slate-950 
    [&_option]:text-white
    [&_label]:text-cyan-500 
    [&_label]:font-mono 
    [&_label]:text-xs 
    [&_label]:uppercase 
    [&_label]:tracking-widest
  `;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500 selection:text-black flex">
      
      {/* --- BACKGROUND GRID --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-50"></div>
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-900/10 blur-[120px] rounded-full mix-blend-screen"></div>
      </div>

      {/* --- SIDEBAR --- */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-slate-900/80 backdrop-blur-xl border-r border-slate-800 z-30 hidden md:flex flex-col">
        {/* Sidebar Header */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
          <div className="w-8 h-8 bg-cyan-500 flex items-center justify-center rounded-sm shadow-[0_0_10px_rgba(6,182,212,0.5)]">
            <Terminal className="w-5 h-5 text-black" />
          </div>
          <span className="font-mono font-bold text-sm tracking-tighter text-white">
            EVOLVED<span className="text-cyan-400">_OS</span>
          </span>
        </div>

        {/* Navigation */}
        <div className="flex-1 py-8 px-4 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-sm">
            <LayoutDashboard className="w-4 h-4" />
            <span className="text-xs font-mono font-bold tracking-widest uppercase">Dashboard</span>
          </button>
        </div>

        {/* User Footer */}
        <div className="p-4 border-t border-slate-800">
          <div className="flex items-center gap-3 px-2 mb-4">
             <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-cyan-500">
                {user?.email?.charAt(0).toUpperCase()}
             </div>
             <div className="flex-1 min-w-0">
                <div className="text-xs font-bold text-white truncate">{user?.name || "Operator"}</div>
                <div className="text-[10px] text-slate-500 truncate font-mono">{user?.email}</div>
             </div>
          </div>
          <button 
            onClick={() => logout()}
            className="w-full flex items-center justify-center gap-2 py-2 text-xs font-mono text-red-400 hover:text-red-300 hover:bg-red-950/30 border border-transparent hover:border-red-900/50 rounded-sm transition-all"
          >
            <LogOut className="w-3 h-3" /> DISCONNECT
          </button>
        </div>
      </aside>

      {/* --- MAIN CONTENT AREA --- */}
      <main className="flex-1 md:ml-64 relative z-10 min-h-screen flex flex-col">
        
        {/* --- TOP BAR HUD --- */}
        <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 sticky top-0 z-20 px-6 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono">
               <span className="text-slate-500">SYSTEM</span>
               <span className="text-slate-700">/</span>
               <span className="text-cyan-400 font-bold uppercase tracking-widest">Dashboard</span>
            </div>
            
            {/* Mobile Menu Toggle */}
            <div className="md:hidden text-cyan-400">
                <Terminal className="w-5 h-5" />
            </div>
        </header>

        <div className="p-6 md:p-8 space-y-8 max-w-7xl mx-auto w-full">
            
            {/* --- TELEMETRY / STATS --- */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Stats Card 1: User */}
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-sm relative overflow-hidden group">
                   <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                      <Terminal className="w-12 h-12 text-cyan-500" />
                   </div>
                   <h2 className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Operator</h2>
                   <div className="text-xl font-bold text-white truncate">
                      {user?.name || user?.email}
                   </div>
                   <div className="flex items-center gap-2 mt-4 text-[10px] text-green-500 font-mono">
                      <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></div>
                      ONLINE
                   </div>
                </div>

                {/* Stats Card 2: Total Load */}
                <div className="bg-slate-900/50 border border-slate-800 p-6 rounded-sm relative group">
                   <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                      <Activity className="w-12 h-12 text-slate-500" />
                   </div>
                   <h2 className="text-xs font-mono text-slate-500 uppercase tracking-widest mb-1">Active Load</h2>
                   <div className="text-3xl font-bold text-white font-mono">
                      {tasks.filter(t => !t.is_complete).length}
                   </div>
                   <div className="mt-2 text-[10px] text-slate-600 font-mono">PENDING EXECUTION</div>
                </div>

                {/* Stats Card 3: Critical (Overdue) */}
                <div className={`bg-slate-900/50 border p-6 rounded-sm relative group transition-colors ${overdueCount > 0 ? 'border-red-900/50 bg-red-950/10' : 'border-slate-800'}`}>
                   <div className="absolute top-0 right-0 p-3 opacity-20 group-hover:opacity-40 transition-opacity">
                      <AlertTriangle className={`w-12 h-12 ${overdueCount > 0 ? 'text-red-500' : 'text-slate-500'}`} />
                   </div>
                   <h2 className={`text-xs font-mono uppercase tracking-widest mb-1 ${overdueCount > 0 ? 'text-red-400' : 'text-slate-500'}`}>Critical Warnings</h2>
                   <div className={`text-3xl font-bold font-mono ${overdueCount > 0 ? 'text-red-500' : 'text-white'}`}>
                      {overdueCount}
                   </div>
                   <div className={`mt-2 text-[10px] font-mono ${overdueCount > 0 ? 'text-red-400' : 'text-slate-600'}`}>
                      {overdueCount > 0 ? "IMMEDIATE ACTION REQUIRED" : "SYSTEM NOMINAL"}
                   </div>
                </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="bg-red-950/20 border border-red-500/30 text-red-400 px-4 py-3 rounded-sm font-mono text-sm flex items-center gap-3">
                <AlertTriangle className="w-4 h-4" /> {error}
              </div>
            )}

            {/* --- CONTROL PANEL (Search & Filter) --- */}
            {/* Added Z-Index 30 here to float above the Create button area */}
            {!tasksLoading && (
              <div className="bg-slate-900/80 border border-slate-800 rounded-sm p-4 backdrop-blur-sm shadow-xl relative z-30">
                 <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center">
                    <div className="w-full md:w-1/3">
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400" />
                            </div>
                            <div className="[&_input]:bg-slate-950 [&_input]:border-slate-700 [&_input]:text-white [&_input]:pl-10 [&_input]:placeholder-slate-500 [&_input]:focus:border-cyan-500 [&_input]:rounded-sm">
                                <SearchBar value={searchQuery} onChange={setSearchQuery} />
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto items-end md:items-center">
                        <div className="[&_select]:bg-slate-950 [&_select]:border-slate-700 [&_select]:text-white [&_select]:rounded-sm [&_button]:text-slate-400 [&_option]:bg-slate-950 [&_option]:text-white">
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
                        <div className="[&_button]:bg-slate-950 [&_button]:border-slate-700 [&_button]:text-slate-300">
                             <SortDropdown value={sortOption} onChange={setSortOption} />
                        </div>
                    </div>
                 </div>
              </div>
            )}

            {/* --- ACTION AREA (Add Task / Form) --- */}
            {/* Added Z-Index 10 here to stay below the Filters */}
            <div className="relative z-10">
                {editingTask ? (
                    <div className="bg-slate-900 border border-cyan-500/30 rounded-sm p-6 shadow-[0_0_30px_rgba(6,182,212,0.1)]">
                        <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
                            <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                                <Terminal className="w-5 h-5 text-cyan-400" /> EDIT_PROTOCOL
                            </h3>
                            <button onClick={handleCancelEdit} className="text-slate-500 hover:text-white"><X className="w-5 h-5"/></button>
                        </div>
                        <div className={inputStyles}>
                            <TaskForm
                                mode="edit"
                                initialTask={editingTask}
                                onSubmit={handleEditTask}
                                onCancel={handleCancelEdit}
                            />
                        </div>
                    </div>
                ) : showForm ? (
                    <div className="bg-slate-900 border border-cyan-500/30 rounded-sm p-6 shadow-[0_0_30px_rgba(6,182,212,0.1)] animate-in fade-in slide-in-from-top-4">
                         <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
                            <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                                <Plus className="w-5 h-5 text-cyan-400" /> INITIALIZE_TASK
                            </h3>
                            <button onClick={() => setShowForm(false)} className="text-slate-500 hover:text-white"><X className="w-5 h-5"/></button>
                        </div>
                        <div className={inputStyles}>
                            <TaskForm
                                onSubmit={handleCreateTask}
                                onCancel={() => setShowForm(false)}
                            />
                        </div>
                    </div>
                ) : (
                    <button
                        onClick={() => setShowForm(true)}
                        className="w-full group relative overflow-hidden rounded-sm bg-cyan-500/10 border border-cyan-500/30 p-6 text-center transition-all hover:bg-cyan-500/20 hover:border-cyan-400 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]"
                    >
                        <div className="flex flex-col items-center gap-2 text-cyan-400 group-hover:text-cyan-300">
                            <Plus className="w-8 h-8" />
                            <span className="font-mono text-sm font-bold tracking-widest uppercase">Create New Entry</span>
                        </div>
                    </button>
                )}
            </div>

            {/* --- TASK LIST RENDERER --- */}
            {tasksLoading ? (
                <div className="opacity-50 grayscale">
                    <DashboardSkeleton />
                </div>
            ) : tasks.length === 0 ? (
                // Check if any filters or sorting are active
                (statusFilter !== "all" ||
                 priorityFilter !== "all" ||
                 selectedTags.length > 0 ||
                 searchQuery ||
                 sortOption.field !== "created_at" ||
                 sortOption.order !== "desc") ? (
                    // Filters/sorting active but no results
                    <div className="text-center py-20 border border-dashed border-slate-800 rounded-sm">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-900 mb-4">
                            <Search className="w-8 h-8 text-slate-600" />
                        </div>
                        <p className="text-slate-400 font-mono text-sm mb-2">NO TASKS FOUND</p>
                        <p className="text-xs text-slate-600 uppercase tracking-widest mb-4">
                            No tasks match the current filter or sort criteria
                        </p>
                        <button
                            onClick={handleClearFilters}
                            className="text-xs font-bold text-cyan-400 hover:text-cyan-300 uppercase tracking-widest border border-cyan-900/50 px-4 py-2 rounded-sm hover:bg-cyan-950/30 transition-colors"
                        >
                            Reset Filters
                        </button>
                    </div>
                ) : !showForm ? (
                    // No filters and truly empty database
                    <div className="text-center py-20 border border-dashed border-slate-800 rounded-sm">
                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-900 mb-4">
                            <Terminal className="w-8 h-8 text-slate-600" />
                        </div>
                        <p className="text-slate-400 font-mono text-sm mb-2">DATABASE EMPTY</p>
                        <p className="text-xs text-slate-600 uppercase tracking-widest">
                            Initialize a task to begin operations
                        </p>
                    </div>
                ) : null
            ) : tasks.length > 0 ? (
                <div className="space-y-4">
                    {filteredTasks.length !== tasks.length && (
                        <div className="flex items-center gap-2 text-xs font-mono text-slate-500 px-1">
                            <Search className="w-3 h-3" />
                            FILTER_ACTIVE: Showing {filteredTasks.length} / {tasks.length} entries
                        </div>
                    )}

                    {filteredTasks.length === 0 ? (
                        <div className="text-center py-12 bg-slate-900/30 border border-slate-800 rounded-sm">
                            <p className="text-slate-500 font-mono text-sm mb-4">QUERY RETURNED 0 RESULTS</p>
                            <button
                                onClick={handleClearFilters}
                                className="text-xs font-bold text-cyan-400 hover:text-cyan-300 uppercase tracking-widest border border-cyan-900/50 px-4 py-2 rounded-sm hover:bg-cyan-950/30 transition-colors"
                            >
                                Reset Filters
                            </button>
                        </div>
                    ) : (
                        <div className="[&_.task-card]:bg-slate-900/80 [&_.task-card]:border-slate-800 [&_.task-card]:backdrop-blur-sm [&_h3]:text-slate-200 [&_p]:text-slate-400 [&_button]:text-slate-400 [&_.task-checkbox]:border-slate-600 [&_.task-checkbox:checked]:bg-cyan-500 [&_.task-checkbox:checked]:border-cyan-500">
                            <TaskList
                                tasks={filteredTasks}
                                onToggleComplete={toggleComplete}
                                onDelete={handleDeleteTask}
                                onEdit={handleEditClick}
                            />
                        </div>
                    )}
                </div>
            ) : null}

        </div>
      </main>

      {/* Delete Confirmation Dialog */}
      <div className="[&_div[role=dialog]]:bg-slate-950 [&_div[role=dialog]]:border [&_div[role=dialog]]:border-slate-800 [&_h3]:text-white [&_p]:text-slate-400">
          <ConfirmDialog
            isOpen={taskToDelete !== null}
            title="PURGE TASK?"
            message="This action is irreversible. The data will be permanently wiped from the database."
            confirmText="CONFIRM DELETION"
            cancelText="ABORT"
            variant="danger"
            onConfirm={confirmDelete}
            onCancel={cancelDelete}
          />
      </div>
    </div>
  );
}