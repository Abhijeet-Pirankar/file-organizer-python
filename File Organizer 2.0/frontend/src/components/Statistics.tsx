import React from 'react';
import { Statistics as StatsType, CategoryProgress } from '../types';
import { FolderCheck, Copy, AlertTriangle, HelpCircle, HardDrive } from 'lucide-react';
import { CategoryBreakdown } from './CategoryBreakdown';

interface Props {
  stats: StatsType | null;
  categories: CategoryProgress[];
}

interface MiniStatProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: string;
}

const MiniStat: React.FC<MiniStatProps> = ({ icon, label, value, color }) => (
  <div className="flex flex-col gap-2 p-4 rounded-xl glass-card relative overflow-hidden group">
    <div className="absolute top-0 right-0 w-16 h-16 rounded-full blur-[30px] opacity-20 group-hover:opacity-40 transition-opacity duration-500" style={{ backgroundColor: color, transform: 'translate(30%, -30%)' }}></div>
    
    <div className="flex items-center gap-2.5">
      <div className="p-1.5 rounded-lg border shadow-sm relative z-10" style={{ borderColor: `${color}30`, background: `${color}15` }}>
        {icon}
      </div>
      <span className="text-[10px] font-bold tracking-[0.15em] text-slate-400 uppercase relative z-10">{label}</span>
    </div>
    <span className="text-xl font-bold tracking-tight relative z-10 drop-shadow-sm" style={{ color }}>{value}</span>
  </div>
);

export const Statistics: React.FC<Props> = ({ stats, categories }) => {
  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  if (!stats) {
    return (
      <div className="flex flex-col items-center justify-center h-full opacity-50 absolute inset-0 z-10">
        <div className="w-16 h-16 rounded-full bg-cyan-500/10 flex items-center justify-center border border-cyan-500/20 mb-4 shadow-[0_0_15px_rgba(6,182,212,0.1)]">
          <HardDrive className="w-6 h-6 text-cyan-400" />
        </div>
        <p className="text-[13px] font-medium text-slate-400 tracking-wide">Waiting for analysis...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 h-full relative z-10">
      <div className="flex items-center gap-2.5 px-1">
        <div className="p-1.5 rounded-md bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_8px_rgba(6,182,212,0.15)]">
          <HardDrive className="w-4 h-4 text-cyan-400" />
        </div>
        <h2 className="text-sm font-semibold text-slate-200">Statistics Overview</h2>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <MiniStat
          icon={<HardDrive className="w-4 h-4 text-blue-400 drop-shadow-[0_0_3px_rgba(96,165,250,0.8)]" />}
          label="Total Files"
          value={stats.totalFiles}
          color="#60a5fa"
        />
        <MiniStat
          icon={<FolderCheck className="w-4 h-4 text-emerald-400 drop-shadow-[0_0_3px_rgba(52,211,153,0.8)]" />}
          label="Organized"
          value={stats.organized}
          color="#34d399"
        />
        <MiniStat
          icon={<AlertTriangle className="w-4 h-4 text-rose-400 drop-shadow-[0_0_3px_rgba(251,113,133,0.8)]" />}
          label="Errors"
          value={stats.errors}
          color="#fb7185"
        />
        <MiniStat
          icon={<Copy className="w-4 h-4 text-slate-400 drop-shadow-[0_0_3px_rgba(148,163,184,0.8)]" />}
          label="Duplicates"
          value={stats.duplicates}
          color="#94a3b8"
        />
        <MiniStat
          icon={<HelpCircle className="w-4 h-4 text-amber-400 drop-shadow-[0_0_3px_rgba(251,191,36,0.8)]" />}
          label="Others"
          value={stats.others}
          color="#fbbf24"
        />
        <MiniStat
          icon={<HardDrive className="w-4 h-4 text-purple-400 drop-shadow-[0_0_3px_rgba(192,132,252,0.8)]" />}
          label="Total Size"
          value={formatSize(stats.totalSize)}
          color="#c084fc"
        />
      </div>

      <div className="flex-1 mt-2">
        <CategoryBreakdown categories={categories} />
      </div>
    </div>
  );
};
