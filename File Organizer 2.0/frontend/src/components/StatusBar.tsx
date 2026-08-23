import React from 'react';

interface Props {
  status: string;
  progress: number; // 0 to 100
}

export const StatusBar: React.FC<Props> = ({ status, progress }) => {
  const isActive = progress > 0 && progress < 100;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-[#0a0f1e]/80 backdrop-blur-md border-t border-white/5 shadow-[0_-4px_20px_rgba(0,0,0,0.4)]">
      {/* Glowing Progress Line */}
      <div className="h-[2px] w-full bg-slate-900 relative overflow-hidden">
        <div
          className="absolute top-0 left-0 h-full transition-all duration-300 ease-out bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"
          style={{ width: `${progress}%` }}
        >
        </div>
      </div>

      {/* Status Text */}
      <div className="px-6 py-2.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="relative flex h-2 w-2">
            {isActive && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>}
            <span className={`relative inline-flex rounded-full h-2 w-2 transition-colors ${isActive ? 'bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]' : 'bg-slate-600'}`}></span>
          </div>
          <span className="text-[11px] text-slate-300 font-bold tracking-widest uppercase drop-shadow-sm">{status}</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-widest">Progress</span>
          <span className="text-[11px] text-cyan-400 font-mono font-bold w-8 text-right drop-shadow-[0_0_2px_rgba(6,182,212,0.5)]">{Math.round(progress)}%</span>
        </div>
      </div>
    </div>
  );
};
