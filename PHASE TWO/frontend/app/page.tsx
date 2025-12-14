"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  CheckSquare,
  Terminal,
  Cpu,
  Database,
  Lock,
  ArrowRight,
  Menu,
  X,
  Code2,
  Activity,
  Zap,
  Globe
} from "lucide-react";

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) return null;
  if (isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500 selection:text-black overflow-x-hidden">
      
      {/* --- BACKGROUND GRID SYSTEM --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        {/* Main Grid */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        {/* Secondary Dotted Grid */}
        <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:16px_16px] opacity-20"></div>
        {/* Blue Atmosphere Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-cyan-500/10 blur-[100px] rounded-full mix-blend-screen pointer-events-none"></div>
      </div>

      {/* --- NAV BAR --- */}
      <nav className="fixed top-0 w-full z-50 border-b border-cyan-900/30 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center h-16 px-6">
          <div className="flex items-center gap-3 group">
            <div className="w-8 h-8 bg-cyan-500 flex items-center justify-center rounded-sm shadow-[0_0_10px_rgba(6,182,212,0.5)] group-hover:shadow-[0_0_20px_rgba(6,182,212,0.8)] transition-all duration-500">
              <Terminal className="w-5 h-5 text-black" />
            </div>
            <span className="font-mono font-bold text-lg tracking-tighter text-white">
              EVOLVED<span className="text-cyan-400">_TODO</span>
            </span>
          </div>

          {/* Desktop Links */}
          <div className="hidden md:flex items-center gap-8 font-mono text-sm">
            <a href="#specs" className="hover:text-cyan-400 transition-colors uppercase tracking-widest text-xs">Specs</a>
            <a href="#protocol" className="hover:text-cyan-400 transition-colors uppercase tracking-widest text-xs">Protocol</a>
            <div className="h-4 w-px bg-slate-800"></div>
            <Link href="/login" className="hover:text-white transition-colors text-slate-400">LOGIN</Link>
            <Link
              href="/register"
              className="bg-slate-100 text-slate-950 px-6 py-2 font-bold hover:bg-cyan-400 hover:text-black transition-all rounded-sm text-xs uppercase tracking-widest shadow-[0_0_10px_rgba(255,255,255,0.1)] hover:shadow-[0_0_15px_rgba(6,182,212,0.6)]"
            >
              Initialize
            </Link>
          </div>

          <button className="md:hidden text-cyan-400" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>

        {/* Mobile Menu Panel */}
        {mobileMenuOpen && (
          <div className="md:hidden absolute top-16 left-0 right-0 bg-slate-950/95 backdrop-blur-xl border-b border-slate-800 shadow-2xl animate-in slide-in-from-top duration-200">
            <div className="flex flex-col p-6 space-y-4 font-mono text-sm">
              <a
                href="#specs"
                onClick={() => setMobileMenuOpen(false)}
                className="hover:text-cyan-400 transition-colors uppercase tracking-widest text-xs py-3 border-b border-slate-800"
              >
                Specs
              </a>
              <a
                href="#protocol"
                onClick={() => setMobileMenuOpen(false)}
                className="hover:text-cyan-400 transition-colors uppercase tracking-widest text-xs py-3 border-b border-slate-800"
              >
                Protocol
              </a>
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="hover:text-white transition-colors text-slate-400 py-3 border-b border-slate-800"
              >
                LOGIN
              </Link>
              <Link
                href="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="bg-cyan-500 text-slate-950 px-6 py-3 font-bold hover:bg-cyan-400 transition-all rounded-sm text-xs uppercase tracking-widest text-center shadow-[0_0_10px_rgba(6,182,212,0.3)]"
              >
                Initialize
              </Link>
            </div>
          </div>
        )}
      </nav>

      <main className="relative z-10 pt-24">
        
        {/* --- HERO SECTION --- */}
        <section className="px-6 border-b border-cyan-900/20 pb-20">
          <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center">
            
            {/* Left Content */}
            <div className="space-y-8">
              {/* Status Badge */}
              <div className="inline-flex items-center gap-3 px-3 py-1 border border-cyan-500/30 bg-cyan-950/30 rounded-full backdrop-blur-sm">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                </span>
                <span className="text-cyan-400 text-xs font-mono uppercase tracking-widest">System Online v1.0</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-white leading-[0.95]">
                MASTER YOUR <br />
                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">TASKS</span> <br />
                EVOLVE.
              </h1>

              <p className="text-lg text-slate-400 max-w-md font-light leading-relaxed">
                The ultimate todo app for serious productivity.
                Recurring tasks, priorities, tags, due dates, and powerful filtering—all in one sleek interface.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Link
                  href="/register"
                  className="group px-8 py-4 bg-cyan-500 text-slate-950 font-bold text-sm uppercase tracking-widest hover:bg-cyan-400 transition-all flex items-center justify-center gap-2 rounded-sm shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_30px_rgba(6,182,212,0.6)]"
                >
                  Get Started Free <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/login"
                  className="px-8 py-4 border border-slate-700 text-slate-300 font-bold text-sm uppercase tracking-widest hover:bg-slate-800 hover:border-cyan-500/50 hover:text-cyan-400 transition-all flex items-center justify-center rounded-sm"
                >
                  Sign In
                </Link>
              </div>

              {/* Technical readout */}
              <div className="grid grid-cols-3 gap-4 border-t border-slate-800 pt-8 mt-8">
                <div>
                  <div className="text-2xl font-mono text-white">Infinite</div>
                  <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Tasks</div>
                </div>
                <div>
                  <div className="text-2xl font-mono text-white">Recurring</div>
                  <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Automation</div>
                </div>
                <div>
                  <div className="text-2xl font-mono text-white">Smart</div>
                  <div className="text-xs text-slate-500 uppercase tracking-widest mt-1">Filters</div>
                </div>
              </div>
            </div>

            {/* Right Visual (Cyber Deck) */}
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg blur opacity-20 group-hover:opacity-40 transition-duration-500"></div>
              <div className="relative bg-slate-950 border border-slate-800 rounded-sm p-2 backdrop-blur-sm">
                <div className="bg-black border border-slate-800 rounded-sm overflow-hidden">
                  {/* Fake Browser Header */}
                  <div className="h-8 bg-slate-900 flex items-center justify-between px-4 border-b border-slate-800">
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 rounded-full bg-slate-600"></div>
                      <div className="w-2 h-2 rounded-full bg-slate-600"></div>
                    </div>
                    <div className="text-[10px] font-mono text-cyan-500/70 bg-cyan-950/30 px-2 py-0.5 rounded-sm border border-cyan-900/30">user@evolved:~/tasks</div>
                  </div>
                  
                  {/* Mock App Interface */}
                  <div className="p-6 font-mono text-sm space-y-4">
                    <div className="flex justify-between text-slate-500 text-xs uppercase mb-6 border-b border-slate-800 pb-2">
                      <span>Task_ID</span>
                      <span>Status</span>
                      <span>Priority</span>
                    </div>
                    
                    {[
                      { id: "TSK-001", text: "Deploy production build", status: "DONE", color: "text-emerald-400" },
                      { id: "TSK-002", text: "Refactor auth middleware", status: "RUNNING", color: "text-cyan-400 animate-pulse" },
                      { id: "TSK-003", text: "Update documentation", status: "PENDING", color: "text-slate-500" },
                    ].map((task, i) => (
                      <div key={i} className="flex items-center justify-between border-b border-dashed border-slate-800 pb-4 last:border-0 hover:bg-slate-900/50 transition-colors cursor-default">
                        <div className="flex items-center gap-4">
                          <span className="text-slate-600 text-xs">{task.id}</span>
                          <span className="text-slate-300">{task.text}</span>
                        </div>
                        <div className="flex items-center gap-6">
                           <span className={`${task.color} text-[10px] tracking-wider font-bold`}>{task.status}</span>
                           <span className="text-[10px] text-slate-600 bg-slate-900 px-1 rounded">HIGH</span>
                        </div>
                      </div>
                    ))}
                    
                    <div className="flex gap-2 text-xs text-cyan-500 pt-2">
                      <span className="animate-pulse">_</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* --- SCROLLING TICKER --- */}
        <div className="border-b border-cyan-900/20 bg-cyan-950/10 py-3 overflow-hidden">
          <div className="flex gap-8 animate-marquee whitespace-nowrap">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="flex items-center gap-8 text-cyan-800/80 font-mono text-xs uppercase tracking-[0.2em]">
                <span>Priorities & Tags</span>
                <span className="text-cyan-400">+</span>
                <span>Recurring Tasks</span>
                <span className="text-cyan-400">+</span>
                <span>Smart Filtering</span>
                <span className="text-cyan-400">+</span>
              </div>
            ))}
          </div>
        </div>

        {/* --- GRID FEATURES --- */}
        <section id="specs" className="max-w-7xl mx-auto px-6 py-24">
          <div className="grid md:grid-cols-3 gap-px bg-slate-800/50 border border-slate-800/50">
            {[
              { icon: <Cpu />, title: "Smart Priorities", desc: "Organize tasks with High, Medium, and Low priorities. Sort and filter to focus on what matters most." },
              { icon: <Database />, title: "Recurring Tasks", desc: "Set tasks to repeat daily, weekly, monthly, or yearly. Perfect for habits and regular check-ins." },
              { icon: <Lock />, title: "Secure & Private", desc: "Your tasks are encrypted and stored securely. Your data belongs to you, always." },
              { icon: <Code2 />, title: "Tags & Search", desc: "Tag your tasks for easy organization. Search and filter instantly to find exactly what you need." },
              { icon: <Activity />, title: "Due Dates", desc: "Never miss a deadline. Set due dates and times, with visual indicators for overdue tasks." },
              { icon: <Globe />, title: "Advanced Filters", desc: "Filter by status, priority, tags, or due dates. Combine filters to create custom task views." }
            ].map((feature, i) => (
              <div key={i} className="bg-slate-950 p-8 hover:bg-slate-900 transition-all duration-300 group border border-transparent hover:border-cyan-900/30 relative">
                <div className="w-10 h-10 bg-slate-900 rounded-sm flex items-center justify-center text-slate-500 mb-6 group-hover:text-cyan-400 group-hover:bg-cyan-950/30 transition-colors group-hover:shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                  {cloneIcon(feature.icon)}
                </div>
                <h3 className="text-xl font-bold text-white mb-4 group-hover:text-cyan-100">{feature.title}</h3>
                <p className="text-slate-400 leading-relaxed text-sm">
                  {feature.desc}
                </p>
                <div className="absolute top-4 right-4 text-[10px] text-slate-700 font-mono opacity-0 group-hover:opacity-100 transition-opacity">
                  SYS_0{i+1}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* --- PROTOCOL / TABS SECTION --- */}
        <section id="protocol" className="border-t border-slate-800 bg-slate-900/20 py-24">
          <div className="max-w-4xl mx-auto px-6">
            <h2 className="text-3xl font-bold text-white mb-12 text-center tracking-tight">HOW IT WORKS</h2>

            <div className="flex flex-col md:flex-row gap-8">
              {/* Tab List */}
              <div className="flex md:flex-col gap-2 md:w-1/3 overflow-x-auto pb-4 md:pb-0">
                {['Create', 'Organize', 'Complete'].map((tab, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveTab(i)}
                    className={`px-6 py-4 text-left font-mono text-xs uppercase tracking-widest border transition-all duration-300 ${
                      activeTab === i 
                      ? 'bg-cyan-500 text-slate-950 border-cyan-500 font-bold shadow-[0_0_15px_rgba(6,182,212,0.4)]' 
                      : 'bg-black text-slate-500 border-slate-800 hover:text-cyan-400 hover:border-cyan-900/50'
                    }`}
                  >
                    0{i+1} // {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="md:w-2/3 bg-black border border-slate-800 p-8 relative min-h-[300px] shadow-2xl">
                {/* Decorative corners */}
                <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan-500/50"></div>
                <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-500/50"></div>
                <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-500/50"></div>
                <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-500/50"></div>

                {activeTab === 0 && (
                  <div className="animate-in fade-in slide-in-from-left-4 duration-300">
                    <h3 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                      <Zap className="w-5 h-5 text-cyan-400" /> Create Tasks Instantly
                    </h3>
                    <p className="text-slate-400 mb-6 leading-relaxed">
                      Add new tasks with a single click. Set titles, descriptions, priorities, tags, due dates, and even make them recurring—all in one intuitive form.
                    </p>
                    <ul className="space-y-4 font-mono text-sm text-slate-500">
                      <li className="flex items-center gap-3 p-2 border border-slate-800/50 rounded bg-slate-900/30">
                        <CheckSquare className="w-4 h-4 text-cyan-400" /> Quick add with <span className="text-cyan-300">keyboard shortcuts</span>
                      </li>
                      <li className="flex items-center gap-3 p-2 border border-slate-800/50 rounded bg-slate-900/30">
                        <CheckSquare className="w-4 h-4 text-cyan-400" /> Set <span className="text-cyan-300">priority levels</span> instantly
                      </li>
                    </ul>
                  </div>
                )}
                {activeTab === 1 && (
                  <div className="animate-in fade-in slide-in-from-left-4 duration-300">
                    <h3 className="text-2xl font-bold text-white mb-4">Organize with Power</h3>
                    <p className="text-slate-400 mb-6">
                      Sort by priority, due date, or completion status. Filter by tags or search terms. Combine multiple filters to create custom views that match your workflow.
                    </p>
                    <div className="relative pt-4">
                      <div className="flex justify-between text-xs font-mono text-cyan-400 mb-2">
                        <span>PRODUCTIVITY</span>
                        <span>MAXIMIZED</span>
                      </div>
                      <div className="h-2 w-full bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                         <div className="h-full bg-cyan-500 w-2/3 shadow-[0_0_10px_rgba(6,182,212,0.8)]"></div>
                      </div>
                    </div>
                  </div>
                )}
                {activeTab === 2 && (
                  <div className="animate-in fade-in slide-in-from-left-4 duration-300">
                    <h3 className="text-2xl font-bold text-white mb-4">Track Completion</h3>
                    <p className="text-slate-400 mb-6">
                      Mark tasks complete with a single click. Recurring tasks automatically generate their next instance. View your completed tasks for a sense of accomplishment.
                    </p>
                    <div className="grid grid-cols-4 gap-2 opacity-50">
                       {[...Array(12)].map((_,i) => (
                         <div key={i} className={`h-8 border border-slate-800 ${i < 8 ? 'bg-cyan-950/30' : 'bg-slate-900'}`}></div>
                       ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* --- BIG CTA --- */}
        <section className="py-32 px-6 text-center relative overflow-hidden">
           {/* Glow Effect */}
           <div className="absolute inset-0 bg-cyan-600/5 z-0"></div>
           <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyan-500/10 blur-[100px] rounded-full"></div>
           
           <div className="relative z-10 max-w-3xl mx-auto">
             <h2 className="text-5xl md:text-8xl font-bold text-white tracking-tighter mb-8">
               READY TO <br /><span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-slate-600">GET THINGS DONE?</span>
             </h2>
             <Link
               href="/register"
               className="inline-block bg-cyan-500 text-black text-lg font-bold px-12 py-5 rounded-sm hover:bg-white hover:scale-105 transition-all uppercase tracking-widest shadow-[0_0_40px_rgba(6,182,212,0.4)] hover:shadow-[0_0_60px_rgba(255,255,255,0.4)]"
             >
               Start for Free
             </Link>
           </div>
        </section>
      </main>

      <footer className="border-t border-slate-800 bg-slate-950 py-12 px-6 font-mono text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-slate-800 border border-slate-700"></div>
            <span>EVOLVED TODO © 2025 - Your Tasks, Evolved.</span>
          </div>
          <div className="flex gap-8 uppercase tracking-widest text-slate-600">
            <a href="#" className="hover:text-cyan-400 transition-colors">About</a>
            <a href="#" className="hover:text-cyan-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-cyan-400 transition-colors">GitHub</a>
          </div>
        </div>
      </footer>
      
      {/* Global CSS for marquee */}
      <style jsx global>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .animate-marquee {
          animation: marquee 30s linear infinite;
        }
      `}</style>
    </div>
  );
}

// Helper for icon cloning
function cloneIcon(icon: any) {
    return <icon.type {...icon.props} className="w-6 h-6" />;
}