"use client";

import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";
import { FormEvent, useState } from "react";
import { 
  Terminal, 
  ArrowLeft, 
  ArrowRight, 
  Mail, 
  Lock, 
  Loader2, 
  ShieldCheck, 
  AlertTriangle,
  Cpu
} from "lucide-react";

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    await login(formData);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-black text-white font-sans selection:bg-white selection:text-black relative py-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
      
      {/* --- BACKGROUND GRID SYSTEM (Matches Landing Page) --- */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#222_1px,transparent_1px),linear-gradient(to_bottom,#222_1px,transparent_1px)] bg-[size:4rem_4rem] opacity-40"></div>
        {/* Subtle radial falloff */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(0,0,0,0.8)_100%)]"></div>
      </div>

      {/* --- TOP LEFT BACK BUTTON --- */}
      <div className="absolute top-8 left-8 z-20">
        <Link
          href="/"
          className="group flex items-center gap-2 text-[10px] font-bold uppercase tracking-widest text-neutral-500 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
          <span>Back to Home</span>
        </Link>
      </div>

      {/* --- CENTERED CONTENT --- */}
      <div className="relative z-10 w-full max-w-md">
        
        {/* Logo / Header */}
        <div className="text-center mb-10">
           <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-5 h-5 bg-white flex items-center justify-center">
              <div className="w-2 h-2 bg-black"></div>
            </div>
            <span className="font-bold text-sm tracking-[0.15em] uppercase">Evolved_Todo</span>
          </div>
        </div>

        {/* Login Container */}
        <div className="bg-[#050505] border border-white/10 p-1 relative">
          
          {/* Internal Border (Double Border Effect) */}
          <div className="border border-white/5 p-8 sm:p-10">

            {/* Status Bar */}
            <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/10">
              <h2 className="text-sm font-bold text-white uppercase tracking-widest">Sign In</h2>
              <div className="flex items-center gap-2 text-[9px] font-mono text-neutral-500 uppercase">
                <div className="w-1.5 h-1.5 bg-green-500 animate-pulse"></div>
                System Ready
              </div>
            </div>

            {error && (
              <div className="mb-6 bg-red-950/20 border border-red-900/50 p-3 flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="text-[10px] font-bold text-red-500 uppercase tracking-wide">Access Denied</p>
                  <p className="text-xs text-red-400 font-mono">{error}</p>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Input */}
              <div className="space-y-2">
                <label
                  htmlFor="email"
                  className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-neutral-500"
                >
                  <span>Email Address</span>
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-4 w-4 text-neutral-600 group-focus-within:text-white transition-colors" />
                  </div>
                  <input
                    type="email"
                    id="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="block w-full pl-10 pr-3 py-3 bg-black border border-white/10 text-white placeholder-neutral-700 focus:outline-none focus:border-white focus:ring-0 transition-colors font-mono text-sm rounded-none"
                    placeholder="your@email.com"
                    autoFocus
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="space-y-2">
                <label
                  htmlFor="password"
                  className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-neutral-500"
                >
                  <span>Password</span>
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-4 w-4 text-neutral-600 group-focus-within:text-white transition-colors" />
                  </div>
                  <input
                    type="password"
                    id="password"
                    required
                    value={formData.password}
                    onChange={(e) =>
                      setFormData({ ...formData, password: e.target.value })
                    }
                    className="block w-full pl-10 pr-3 py-3 bg-black border border-white/10 text-white placeholder-neutral-700 focus:outline-none focus:border-white focus:ring-0 transition-colors font-mono text-sm rounded-none"
                    placeholder="••••••••••••"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-white text-black h-12 flex items-center justify-center gap-3 text-xs font-bold uppercase tracking-widest hover:bg-neutral-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2 rounded-none"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    Authenticating...
                  </>
                ) : (
                  <>
                    Sign In
                    <ArrowRight className="w-3 h-3" />
                  </>
                )}
              </button>
            </form>

            {/* Footer Links */}
            <div className="mt-8 pt-6 border-t border-white/10 flex justify-between items-center text-[10px] uppercase tracking-widest">
               <Link href="/register" className="text-neutral-500 hover:text-white transition-colors flex items-center gap-2 group">
                  <span className="w-1 h-1 bg-neutral-700 group-hover:bg-white transition-colors"></span>
                  Create Account
               </Link>
               <Link href="/forgot-password" className="text-neutral-500 hover:text-white transition-colors">
                  Forgot Password?
               </Link>
            </div>

          </div>
        </div>

        {/* Security Badge */}
        <div className="mt-8 flex justify-center">
            <div className="flex items-center gap-2 text-[9px] text-neutral-700 font-mono uppercase tracking-widest border border-neutral-900 px-3 py-1 bg-black">
                <ShieldCheck className="w-3 h-3" /> 256-Bit Encrypted Connection
            </div>
        </div>
        
      </div>
    </div>
  );
}