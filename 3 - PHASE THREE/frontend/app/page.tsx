"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Terminal,
  Bot,
  CheckSquare,
  Command,
  Hash,
  MoreHorizontal,
  ChevronRight,
  LayoutGrid,
  Cpu,
  CalendarClock,
  MessageSquare,
  Sparkles,
  ListTodo,
  ArrowDownRight,
  Split,
  ShieldAlert,
  BrainCircuit,
  History
} from "lucide-react";

// --- COMPONENTS ---

const SharpButton = ({ text, href, icon: Icon, primary = false }: { text: string, href: string, icon?: any, primary?: boolean }) => (
  <Link 
    href={href} 
    className={`
      group relative inline-flex h-12 items-center justify-center gap-3 px-8 text-xs font-bold uppercase tracking-widest transition-all duration-200 border
      ${primary 
        ? "bg-white text-black border-white hover:bg-neutral-200" 
        : "bg-black text-white border-neutral-700 hover:border-white"
      }
    `}
  >
    {text}
    {Icon && <Icon className="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" />}
  </Link>
);

const SectionLabel = ({ text }: { text: string }) => (
  <div className="flex items-center gap-3 mb-8">
    <div className="h-px w-8 bg-neutral-700"></div>
    <span className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.2em]">{text}</span>
  </div>
);

const AgentSpecCard = ({ icon: Icon, title, subtitle, children }: { icon: any, title: string, subtitle: string, children: React.ReactNode }) => (
  <div className="bg-black border border-white/10 p-6 flex flex-col h-full hover:border-white/30 transition-colors group">
    <div className="flex justify-between items-start mb-6">
      <div className="w-8 h-8 bg-neutral-900 border border-neutral-800 flex items-center justify-center text-white group-hover:bg-white group-hover:text-black transition-colors">
        <Icon className="w-4 h-4" />
      </div>
      <div className="text-[10px] font-mono text-neutral-600 uppercase tracking-widest">{subtitle}</div>
    </div>
    <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-4">{title}</h3>
    <div className="flex-1">
      {children}
    </div>
  </div>
);

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) return null;
  if (isAuthenticated) return null;

  return (
    <div className="min-h-screen bg-black text-white font-sans selection:bg-white selection:text-black flex flex-col overflow-x-hidden">
      
      {/* --- GRID BACKGROUND --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#222_1px,transparent_1px),linear-gradient(to_bottom,#222_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40"></div>
      </div>

      {/* --- NAVBAR --- */}
      <nav className="fixed top-0 w-full z-50 bg-black/90 backdrop-blur-sm border-b border-white/10">
        <div className="flex h-16 items-center justify-between px-6 max-w-[1400px] mx-auto">
          <div className="flex items-center gap-2">
            <div className="w-5 h-5 bg-white flex items-center justify-center">
              <div className="w-2 h-2 bg-black"></div>
            </div>
            <span className="font-bold text-sm tracking-[0.15em] uppercase">Evolved_Todo</span>
          </div>
          <div className="hidden md:flex items-center gap-10 text-[10px] font-bold uppercase tracking-widest text-neutral-500">
            <a href="#intelligence" className="hover:text-white transition-colors flex items-center gap-1"><Sparkles className="w-3 h-3"/> AI Agent</a>
            <a href="#specifications" className="hover:text-white transition-colors flex items-center gap-1"><Cpu className="w-3 h-3"/> Specifications</a>
            <a href="#system" className="hover:text-white transition-colors">System</a>
            <a href="#protocol" className="hover:text-white transition-colors">Protocol</a>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 hover:text-white">Login</Link>
            <Link href="/register" className="bg-white text-black px-5 py-2 text-[10px] font-bold uppercase tracking-widest hover:bg-neutral-200 transition-colors">
              Initialize
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative z-10 flex-1 flex flex-col pt-16">
        
        {/* --- HERO SECTION --- */}
        <section className="relative border-b border-white/10 bg-black">
          <div className="max-w-[1400px] mx-auto grid lg:grid-cols-12 gap-12 pt-20 pb-24 px-6">
            
            {/* Left: Copy */}
            <div className="lg:col-span-5 flex flex-col justify-center">
              <div className="inline-flex items-center gap-2 border border-white/20 bg-white/5 px-3 py-1 w-fit mb-8">
                <span className="w-1.5 h-1.5 bg-green-500 rounded-none animate-pulse"></span>
                <span className="text-[10px] font-mono text-neutral-300 uppercase tracking-widest">System Online</span>
              </div>
              
              <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-white leading-[0.9] mb-8">
                CAPTURE. <br />
                ORGANIZE. <br />
                <span className="text-neutral-500">EXECUTE.</span>
              </h1>

              <p className="text-neutral-400 text-lg mb-10 font-light leading-relaxed border-l-2 border-white/20 pl-6">
                The next-generation task management system powered by AI.
                Transform chaos into clarity with natural language processing and intelligent automation.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <SharpButton text="Open Dashboard" href="/register" icon={ArrowRight} primary />
                <SharpButton text="View Specifications" href="#specifications" icon={Cpu} />
              </div>
            </div>

            {/* Right: The App Mockup */}
            <div className="lg:col-span-7 relative pt-10">
               <div className="absolute -top-10 -right-10 w-64 h-64 border border-white/5 bg-white/[0.02]"></div>
               <div className="w-full bg-[#050505] border border-white/10 shadow-2xl relative z-10">
                  {/* Window Header */}
                  <div className="h-10 border-b border-white/10 flex items-center justify-between px-4 bg-[#0a0a0a]">
                    <div className="flex gap-4 text-[10px] font-mono text-neutral-500 uppercase tracking-widest">
                       <span className="text-white">Tasks</span>
                       <span>Projects</span>
                    </div>
                    <div className="text-[10px] text-neutral-600 font-mono">v2.4.0</div>
                  </div>
                  
                  <div className="flex h-[400px]">
                     {/* Sidebar */}
                     <div className="w-48 border-r border-white/10 bg-black/50 p-4 hidden md:block">
                        <div className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest mb-4">Workspace</div>
                        <ul className="space-y-1">
                           {['Inbox', 'Today', 'Upcoming', 'High Priority'].map((item, i) => (
                              <li key={i} className={`flex items-center gap-3 px-3 py-2 text-xs font-mono cursor-pointer ${i === 1 ? 'bg-white text-black' : 'text-neutral-400 hover:text-white'}`}>
                                 {i === 1 ? <ArrowDownRight className="w-3 h-3"/> : <span className="w-3 h-3"></span>}
                                 {item}
                              </li>
                           ))}
                        </ul>
                     </div>

                     {/* Main Task List */}
                     <div className="flex-1 bg-black p-6 relative overflow-hidden">
                        <div className="flex justify-between items-end mb-8">
                           <div>
                              <h2 className="text-2xl font-bold uppercase tracking-tight text-white">Today's Focus</h2>
                              <p className="text-[10px] text-neutral-500 font-mono mt-1">OCTOBER 24, 2025 • 4 TASKS</p>
                           </div>
                           <button className="w-8 h-8 border border-white/20 flex items-center justify-center hover:bg-white hover:text-black transition-colors">
                              <MoreHorizontal className="w-4 h-4" />
                           </button>
                        </div>
                        <div className="space-y-px bg-white/10 border border-white/10">
                           {[
                              { title: "Review Q3 Financials", tag: "FINANCE", priority: "HIGH" },
                              { title: "Deploy Production Fix", tag: "DEV", priority: "CRITICAL" },
                              { title: "Team Sync Meeting", tag: "GENERAL", priority: null },
                           ].map((task, i) => (
                              <div key={i} className="group flex items-center justify-between p-4 bg-black hover:bg-neutral-900 transition-colors cursor-pointer border-l-2 border-l-transparent hover:border-l-white">
                                 <div className="flex items-center gap-4">
                                    <div className="w-4 h-4 border border-neutral-600 group-hover:border-white transition-colors"></div>
                                    <span className="text-sm text-neutral-300 font-mono group-hover:text-white">{task.title}</span>
                                 </div>
                                 <div className="flex gap-2">
                                    {task.priority && <span className="text-[9px] bg-white/10 px-1.5 py-0.5 text-white font-mono">{task.priority}</span>}
                                    <span className="text-[9px] text-neutral-600 border border-neutral-800 px-1.5 py-0.5 font-mono">{task.tag}</span>
                                 </div>
                              </div>
                           ))}
                        </div>
                     </div>
                  </div>
               </div>
            </div>
          </div>
        </section>

        {/* --- SCROLLING TICKER --- */}
        <div className="border-b border-white/10 bg-white text-black py-3 overflow-hidden">
           <div className="flex gap-16 whitespace-nowrap font-mono text-xs font-bold uppercase tracking-[0.2em] animate-marquee">
              <span>Natural Language Input</span><span>+</span>
              <span>Intelligent Sorting</span><span>+</span>
              <span>Context Awareness</span><span>+</span>
              <span>Keyboard First</span><span>+</span>
              <span>Zero Latency</span><span>+</span>
              <span>Natural Language Input</span><span>+</span>
              <span>Intelligent Sorting</span><span>+</span>
           </div>
        </div>

        {/* --- SECTION 1: THE INTELLIGENCE LAYER (Visual Demo) --- */}
        <section id="intelligence" className="bg-[#050505] border-b border-white/10 py-32">
           <div className="max-w-[1400px] mx-auto px-6">
              <div className="grid lg:grid-cols-2 gap-20 items-center">
                 
                 {/* Left: Explanation */}
                 <div className="order-2 lg:order-1">
                    <SectionLabel text="The Intelligence Layer" />
                    <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tighter">
                       DO LESS. <br />
                       ACHIEVE MORE.
                    </h2>
                    <p className="text-neutral-400 text-lg leading-relaxed mb-8">
                       Stop filling out endless forms. Our built-in <span className="text-white font-bold">AI Chat Assistant</span> understands your intent. 
                       Just type naturally, and the system parses dates, tags, and priorities instantly.
                    </p>
                    
                    <div className="space-y-6">
                       <div className="flex gap-4 items-start">
                          <div className="mt-1 w-8 h-8 bg-white text-black flex items-center justify-center shrink-0">
                             <MessageSquare className="w-4 h-4" />
                          </div>
                          <div>
                             <h4 className="text-white font-bold text-sm uppercase tracking-wide">Conversational Input</h4>
                             <p className="text-neutral-500 text-xs font-mono mt-1">Chat with your database. "Show me all high priority tasks for next week."</p>
                          </div>
                       </div>
                    </div>
                 </div>

                 {/* Right: The Transformation Visual */}
                 <div className="order-1 lg:order-2 relative group">
                    <div className="relative grid gap-6">
                       <div className="bg-black border border-white/10 p-6 relative">
                          <div className="absolute -left-3 top-6 w-6 h-6 bg-black border border-white/10 flex items-center justify-center text-[10px] text-neutral-500 font-mono">IN</div>
                          <div className="text-[10px] font-mono text-neutral-500 mb-2 uppercase tracking-widest">Natural Language Input</div>
                          <p className="text-lg text-white font-light">
                             "Remind me to <span className="bg-white text-black px-1">email the client</span> about the contract <span className="underline decoration-neutral-600 underline-offset-4">tomorrow at 2pm</span> and tag it <span className="text-neutral-400">#urgent</span>"
                          </p>
                       </div>
                       <div className="flex justify-center -my-3 relative z-10">
                          <div className="bg-black border border-white/10 px-3 py-1 flex items-center gap-2">
                             <Bot className="w-4 h-4 text-white" />
                             <span className="text-[10px] font-mono uppercase tracking-widest">Processing Intent...</span>
                          </div>
                       </div>
                       <div className="bg-white/5 border border-white/10 p-6 relative">
                          <div className="absolute -left-3 top-6 w-6 h-6 bg-white text-black flex items-center justify-center text-[10px] font-mono">OUT</div>
                          <div className="text-[10px] font-mono text-neutral-500 mb-4 uppercase tracking-widest">Structured Task Object</div>
                          <div className="bg-black border border-white/20 p-4 flex items-start gap-4">
                             <div className="mt-1 w-4 h-4 border border-white/50"></div>
                             <div className="flex-1 space-y-2">
                                <div className="text-sm text-white font-bold">Email the client about contract</div>
                                <div className="flex flex-wrap gap-2">
                                   <div className="flex items-center gap-1 bg-neutral-900 border border-neutral-800 px-2 py-1 text-[10px] text-white font-mono uppercase">
                                      <CalendarClock className="w-3 h-3" /> Tomorrow 14:00
                                   </div>
                                   <div className="bg-white text-black px-2 py-1 text-[10px] font-bold font-mono uppercase">
                                      #URGENT
                                   </div>
                                </div>
                             </div>
                          </div>
                       </div>
                    </div>
                 </div>
              </div>
           </div>
        </section>

        {/* --- NEW SECTION: AGENT CAPABILITIES --- */}
        <section id="specifications" className="bg-black border-b border-white/10 py-32 relative">
          <div className="max-w-[1400px] mx-auto px-6">
            <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
              <div>
                <SectionLabel text="Specifications" />
                <h2 className="text-4xl font-bold uppercase text-white tracking-tighter">
                  Smart Task <br/> Management.
                </h2>
              </div>
              <p className="max-w-md text-neutral-500 font-mono text-xs leading-relaxed text-right uppercase tracking-widest hidden md:block">
                AI-Powered • Real-Time Updates • Cloud Synced
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">

              {/* Feature 1: Natural Language */}
              <AgentSpecCard icon={MessageSquare} title="Natural Language" subtitle="AI Chat">
                <p className="text-xs text-neutral-400 font-mono mb-4 leading-relaxed">
                  Just type in plain English. The AI understands your intent and creates structured tasks automatically.
                </p>
                <div className="bg-neutral-950 border border-neutral-900 p-3 space-y-2 opacity-80">
                  <div className="text-[9px] text-neutral-500">"Add buy groceries tomorrow"</div>
                  <div className="flex items-center gap-2 text-white text-[10px]">
                    <CheckSquare className="w-3 h-3" /> Task Created
                  </div>
                </div>
              </AgentSpecCard>

              {/* Feature 2: Smart Priorities */}
              <AgentSpecCard icon={Sparkles} title="Smart Priorities" subtitle="Auto-Sort">
                 <p className="text-xs text-neutral-400 font-mono mb-4 leading-relaxed">
                  Tasks are automatically organized by priority, due date, and tags for maximum productivity.
                </p>
                <div className="space-y-1">
                   <div className="flex items-center gap-2 text-[9px]">
                      <div className="w-2 h-2 bg-red-500"></div>
                      <span className="text-neutral-400">High Priority</span>
                   </div>
                   <div className="flex items-center gap-2 text-[9px]">
                      <div className="w-2 h-2 bg-yellow-500"></div>
                      <span className="text-neutral-400">Medium Priority</span>
                   </div>
                   <div className="flex items-center gap-2 text-[9px]">
                      <div className="w-2 h-2 bg-green-500"></div>
                      <span className="text-neutral-400">Low Priority</span>
                   </div>
                </div>
              </AgentSpecCard>

              {/* Feature 3: Due Date Tracking */}
              <AgentSpecCard icon={CalendarClock} title="Due Date Tracking" subtitle="Deadlines">
                 <p className="text-xs text-neutral-400 font-mono mb-4 leading-relaxed">
                  Never miss a deadline. Get visual indicators for upcoming and overdue tasks.
                </p>
                <div className="space-y-2 font-mono text-[9px]">
                   <div className="flex justify-between text-neutral-400">
                      <span>Due Today</span>
                      <span className="text-yellow-500">3 tasks</span>
                   </div>
                   <div className="flex justify-between text-neutral-400">
                      <span>Overdue</span>
                      <span className="text-red-500">1 task</span>
                   </div>
                </div>
              </AgentSpecCard>

              {/* Feature 4: Tag System */}
              <AgentSpecCard icon={Hash} title="Tag System" subtitle="Organization">
                 <p className="text-xs text-neutral-400 font-mono mb-4 leading-relaxed">
                  Organize tasks with custom tags. Filter and search by tag for quick access to related tasks.
                </p>
                <div className="flex flex-wrap gap-1 mt-4">
                   <div className="text-[9px] bg-neutral-900 border border-neutral-800 px-2 py-1">#work</div>
                   <div className="text-[9px] bg-neutral-900 border border-neutral-800 px-2 py-1">#personal</div>
                   <div className="text-[9px] bg-neutral-900 border border-neutral-800 px-2 py-1">#urgent</div>
                </div>
              </AgentSpecCard>

            </div>
          </div>
        </section>

        {/* --- SYSTEM FEATURES --- */}
        <section id="system" className="bg-black border-b border-white/10 py-32">
           <div className="max-w-[1400px] mx-auto px-6">
              <div className="mb-16">
                 <SectionLabel text="Core Capabilities" />
                 <h2 className="text-3xl font-bold uppercase text-white">System Architecture</h2>
              </div>
              <div className="grid md:grid-cols-3 border-t border-l border-white/10">
                 {[
                    { icon: Terminal, title: "Command Line", desc: "Execute complex workflows without leaving your keyboard." },
                    { icon: LayoutGrid, title: "Smart Views", desc: "Kanban, List, and Calendar views that adapt to your context." },
                    { icon: Hash, title: "Tagging System", desc: "Polymorphic tagging for fluid task organization." },
                    { icon: CheckSquare, title: "Recurring Tasks", desc: "Powerful recurrence rules (cron-style) for daily habits." },
                    { icon: ListTodo, title: "Sub-Tasks", desc: "Break down monumental projects into atomic units of work." },
                    { icon: Sparkles, title: "Focus Mode", desc: "Distraction-free interface that highlights only what matters now." }
                 ].map((feature, i) => (
                    <div key={i} className="group border-r border-b border-white/10 p-10 hover:bg-white/[0.03] transition-colors">
                       <feature.icon className="w-6 h-6 text-neutral-500 mb-6 group-hover:text-white transition-colors" />
                       <h3 className="text-sm font-bold uppercase tracking-widest text-white mb-3">{feature.title}</h3>
                       <p className="text-sm text-neutral-500 font-mono leading-relaxed">{feature.desc}</p>
                    </div>
                 ))}
              </div>
           </div>
        </section>

        {/* --- PROTOCOL (STEPS) --- */}
        <section id="protocol" className="py-32 bg-[#050505]">
           <div className="max-w-[1400px] mx-auto px-6 grid lg:grid-cols-2 gap-16">
              <div>
                 <SectionLabel text="Methodology" />
                 <h2 className="text-4xl font-bold text-white mb-8">
                    THE PROTOCOL <br /> OF EXECUTION.
                 </h2>
                 <p className="text-neutral-500 text-lg mb-8">
                    A tool is only as good as the system behind it. Evolved Todo enforces a strict workflow to ensure nothing is lost and everything is done.
                 </p>
                 <SharpButton text="Start The Protocol" href="/register" primary />
              </div>
              <div className="space-y-0 border border-white/10">
                 {[
                    { step: "01", title: "Capture", desc: "Dump everything into the Inbox. Clear your mind immediately." },
                    { step: "02", title: "Clarify", desc: "The AI helps you define the 'Next Action' for every item." },
                    { step: "03", title: "Execute", desc: "Filter by context and energy level. Do the work." }
                 ].map((item, i) => (
                    <div key={i} className="flex gap-6 p-8 border-b border-white/10 last:border-b-0 bg-black hover:bg-white/[0.02] transition-colors">
                       <span className="text-3xl font-bold text-white/20">{item.step}</span>
                       <div>
                          <h4 className="text-lg font-bold text-white uppercase tracking-widest mb-2">{item.title}</h4>
                          <p className="text-sm text-neutral-500 font-mono">{item.desc}</p>
                       </div>
                    </div>
                 ))}
              </div>
           </div>
        </section>

        {/* --- FINAL CTA --- */}
        <section className="py-32 border-t border-white/10 bg-black text-center px-6">
           <div className="max-w-2xl mx-auto">
              <h2 className="text-5xl md:text-8xl font-bold text-white tracking-tighter mb-8">
                 READY TO <br/> GET ORGANIZED?
              </h2>
              <p className="text-neutral-500 text-lg mb-12 font-mono">
                 JOIN THOUSANDS OF HIGH-PERFORMERS USING EVOLVED TODO
              </p>
              <div className="flex flex-col items-center gap-6">
                 <Link href="/register" className="group relative w-full sm:w-auto h-16 bg-white text-black flex items-center justify-center px-16 text-sm font-bold uppercase tracking-[0.2em] hover:bg-neutral-300 transition-colors">
                    Start Free Today
                 </Link>
                 <p className="text-neutral-600 text-xs font-mono uppercase tracking-widest">
                    No credit card required • Setup in 60 seconds
                 </p>
              </div>
           </div>
        </section>

      </main>

      {/* --- FOOTER --- */}
      <footer className="bg-black py-12 px-6 border-t border-white/10 text-[10px] uppercase tracking-widest font-bold text-neutral-600">
         <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
               <div className="w-3 h-3 bg-neutral-800"></div>
               <span>Evolved Todo Systems © 2025</span>
            </div>
            <div className="flex gap-8">
               <a href="#" className="hover:text-white transition-colors">Privacy</a>
               <a href="#" className="hover:text-white transition-colors">Terms</a>
               <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
         </div>
      </footer>
      
      <style jsx global>{`
        @keyframes marquee { 0% { transform: translateX(0); } 100% { transform: translateX(-50%); } }
        .animate-marquee { animation: marquee 30s linear infinite; }
      `}</style>
    </div>
  );
}