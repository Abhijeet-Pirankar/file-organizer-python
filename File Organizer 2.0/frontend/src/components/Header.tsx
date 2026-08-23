import React from 'react';
import { FolderKanban } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between glass-panel rounded-2xl p-6 relative overflow-hidden">
      {/* Subtle background gradient inside header */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-[80px] -translate-y-1/2 translate-x-1/3 pointer-events-none"></div>
      
      <div className="flex items-center gap-5 relative z-10">
        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-400/30 flex items-center justify-center shadow-[inset_0_1px_1px_rgba(255,255,255,0.2),0_4px_20px_rgba(6,182,212,0.15)] relative group">
          <div className="absolute inset-0 bg-cyan-400/20 rounded-2xl blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <FolderKanban className="w-7 h-7 text-cyan-400 relative z-10" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-md">
              Advanced File Organizer
            </h1>
            <span className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-200 border border-cyan-500/30 uppercase tracking-widest shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]">
              v2.0
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1 font-medium tracking-wide">
            Smart & Safe File Management
          </p>
        </div>
      </div>
      
      <div className="mt-4 sm:mt-0 flex items-center gap-2.5 px-4 py-2 rounded-xl border border-emerald-500/30 bg-emerald-500/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] relative z-10 backdrop-blur-md">
        <div className="relative flex h-2.5 w-2.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
        </div>
        <span className="text-[11px] font-bold text-emerald-400 tracking-[0.15em]">SYSTEM READY</span>
      </div>
    </div>
  );
};
