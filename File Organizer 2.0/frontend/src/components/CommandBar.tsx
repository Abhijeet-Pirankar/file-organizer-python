import React from 'react';
import { Search, Eye, Zap, Undo2, Activity, Settings, Radio } from 'lucide-react';

interface Props {
  onAnalyze: () => void;
  onPreview: () => void;
  onOrganize: () => void;
  onUndo?: () => void;
  onWatch?: () => void;
  isOrganizing?: boolean;
  hasFolder?: boolean;
}

export const CommandBar: React.FC<Props> = ({ onAnalyze, onPreview, onOrganize, onUndo, onWatch, isOrganizing, hasFolder }) => {
  const btnStyle = "flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm text-slate-300 glass-button disabled:opacity-40 disabled:cursor-not-allowed group";
  
  return (
    <div className="flex items-center gap-3 w-full p-4 overflow-x-auto custom-scrollbar relative">
      <div className="flex items-center gap-3 relative z-10">
        <button className={btnStyle} onClick={onAnalyze} disabled={!hasFolder || isOrganizing}>
          <Search className="w-4 h-4 text-cyan-400 group-hover:text-cyan-300 transition-colors drop-shadow-[0_0_4px_rgba(6,182,212,0.3)]" />
          Analyze
        </button>

        <button className={btnStyle} onClick={onPreview} disabled={!hasFolder || isOrganizing}>
          <Eye className="w-4 h-4 text-blue-400 group-hover:text-blue-300 transition-colors drop-shadow-[0_0_4px_rgba(59,130,246,0.3)]" />
          Preview
        </button>

        <div className="w-px h-6 bg-white/10 mx-1"></div>

        <button
          onClick={onOrganize}
          disabled={!hasFolder || isOrganizing}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-bold text-sm glass-button-primary disabled:opacity-50 disabled:cursor-not-allowed ${isOrganizing ? 'animate-pulse-glow' : ''}`}
        >
          <Zap className={`w-4 h-4 ${isOrganizing ? 'text-white' : 'text-cyan-100'} drop-shadow-[0_0_4px_rgba(255,255,255,0.8)]`} />
          {isOrganizing ? 'Organizing...' : 'Organize'}
        </button>

        <div className="w-px h-6 bg-white/10 mx-1"></div>

        <button className={btnStyle} onClick={onUndo} disabled={isOrganizing}>
          <Undo2 className="w-4 h-4 text-purple-400 group-hover:text-purple-300 transition-colors" />
          Undo
        </button>

        <button className={btnStyle} onClick={onWatch} disabled={!hasFolder || isOrganizing}>
          <Radio className="w-4 h-4 text-fuchsia-400 group-hover:text-fuchsia-300 transition-colors" />
          Watch
        </button>
      </div>

      <div className="flex-1"></div>

      <div className="flex items-center gap-3 relative z-10">
        <button className={btnStyle}>
          <Activity className="w-4 h-4 text-emerald-400 group-hover:text-emerald-300 transition-colors" />
          Activity
        </button>

        <button className={btnStyle}>
          <Settings className="w-4 h-4 text-slate-400 group-hover:text-slate-300 transition-colors" />
          Settings
        </button>
      </div>
    </div>
  );
};
