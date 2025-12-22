"use client";

import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { 
  Terminal, 
  ArrowLeft, 
  ArrowRight, 
  User,
  Mail, 
  Lock, 
  Loader2, 
  FileSignature, 
  AlertCircle 
} from "lucide-react";

export default function RegisterPage() {
  const { register, isLoading, error } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  });

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await register(formData);
  };

  return (
    // Main Container: py-24 ensures form doesn't touch edges on vertical resize
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-slate-200 font-sans selection:bg-cyan-500 selection:text-black relative py-24 px-4 sm:px-6 lg:px-8">
      
      {/* --- BACKGROUND GRID SYSTEM --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        <div className="absolute inset-0 bg-[radial-gradient(#334155_1px,transparent_1px)] [background-size:16px_16px] opacity-20"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-cyan-500/5 blur-[120px] rounded-full mix-blend-screen pointer-events-none"></div>
      </div>

      {/* --- TOP LEFT BACK BUTTON --- */}
      <div className="absolute top-6 left-6 z-20">
        <Link
          href="/"
          className="inline-flex items-center text-xs font-mono text-slate-500 hover:text-cyan-400 transition-colors uppercase tracking-widest group border border-transparent hover:border-cyan-900/30 rounded px-3 py-2 hover:bg-cyan-950/30"
        >
          <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
          Abort // Return to System
        </Link>
      </div>

      {/* --- CENTERED CONTENT --- */}
      <div className="relative z-10 w-full max-w-md">
        
        {/* Header / Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-cyan-500 flex items-center justify-center rounded-sm shadow-[0_0_15px_rgba(6,182,212,0.5)]">
              <Terminal className="w-6 h-6 text-black" />
            </div>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            EVOLVED<span className="text-cyan-400">_TODO</span>
          </h1>
          <p className="text-slate-500 font-mono text-xs mt-2 uppercase tracking-widest">
            Create Your Free Account
          </p>
        </div>

        {/* Register Card */}
        <div className="bg-slate-900/50 backdrop-blur-md border border-slate-800 rounded-sm p-8 relative shadow-2xl">
          {/* Decorative Corner Accents */}
          <div className="absolute top-0 left-0 w-3 h-3 border-t border-l border-cyan-500/50"></div>
          <div className="absolute top-0 right-0 w-3 h-3 border-t border-r border-cyan-500/50"></div>
          <div className="absolute bottom-0 left-0 w-3 h-3 border-b border-l border-cyan-500/50"></div>
          <div className="absolute bottom-0 right-0 w-3 h-3 border-b border-r border-cyan-500/50"></div>

          <div className="flex items-center justify-between mb-8 border-b border-slate-800 pb-4">
            <h2 className="text-lg font-bold text-white tracking-tight">GET STARTED</h2>
            <div className="flex items-center gap-2 text-[10px] font-mono text-cyan-500 bg-cyan-950/30 px-2 py-1 rounded border border-cyan-900/30">
              <FileSignature className="w-3 h-3" />
              FREE FOREVER
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-950/20 border border-red-500/30 rounded-sm flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
              <p className="text-sm text-red-400 font-mono">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name Input */}
            <div>
              <label
                htmlFor="name"
                className="block text-[10px] font-mono uppercase tracking-widest text-cyan-500 mb-2"
              >
                Your Name (Optional)
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                </div>
                <input
                  type="text"
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="block w-full pl-10 pr-3 py-3 bg-slate-950 border border-slate-800 rounded-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono text-sm shadow-inner"
                  placeholder="John Doe"
                />
              </div>
            </div>

            {/* Email Input */}
            <div>
              <label
                htmlFor="email"
                className="block text-[10px] font-mono uppercase tracking-widest text-cyan-500 mb-2"
              >
                Email Address *
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                </div>
                <input
                  type="email"
                  id="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="block w-full pl-10 pr-3 py-3 bg-slate-950 border border-slate-800 rounded-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono text-sm shadow-inner"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            {/* Password Input */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label
                  htmlFor="password"
                  className="block text-[10px] font-mono uppercase tracking-widest text-cyan-500"
                >
                  Password *
                </label>
                <span className="text-[10px] text-slate-500 font-mono">Min 8 Characters</span>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-4 w-4 text-slate-500 group-focus-within:text-cyan-400 transition-colors" />
                </div>
                <input
                  type="password"
                  id="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="block w-full pl-10 pr-3 py-3 bg-slate-950 border border-slate-800 rounded-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono text-sm shadow-inner"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-cyan-500 text-slate-950 py-3 px-4 rounded-sm font-bold uppercase tracking-widest text-xs hover:bg-cyan-400 focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_30px_rgba(6,182,212,0.5)] flex items-center justify-center gap-2 mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  CREATING ACCOUNT...
                </>
              ) : (
                <>
                  CREATE ACCOUNT
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-8 text-center border-t border-slate-800 pt-6">
            <p className="text-xs text-slate-500 font-mono">
              ALREADY HAVE AN ACCOUNT?{" "}
              <Link
                href="/login"
                className="text-cyan-400 hover:text-cyan-300 font-bold ml-1 hover:underline decoration-cyan-500/30 underline-offset-4"
              >
                SIGN IN
              </Link>
            </p>
          </div>
        </div>
        
        {/* Footer info */}
        <div className="mt-8 text-center">
            <div className="text-[10px] text-slate-700 font-mono uppercase tracking-widest">
                Evolved Todo - Task Management Evolved
            </div>
        </div>
      </div>
    </div>
  );
}