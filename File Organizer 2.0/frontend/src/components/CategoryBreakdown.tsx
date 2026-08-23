import React from 'react';
import { CategoryProgress } from '../types';
import { Image, FileText, Video, File, Music, Archive, LayoutGrid } from 'lucide-react';

interface Props {
  categories: CategoryProgress[];
}

const categoryStyles: Record<string, { icon: (cls: string) => React.ReactNode; bar: string; color: string }> = {
  Images:   { icon: (c) => <Image    className={c} style={{ color: '#c084fc' }} />, bar: 'linear-gradient(90deg, #9333ea, #d8b4fe)', color: '#c084fc' },
  PDFs:     { icon: (c) => <FileText className={c} style={{ color: '#fb7185' }} />, bar: 'linear-gradient(90deg, #e11d48, #fda4af)', color: '#fb7185' },
  Videos:   { icon: (c) => <Video    className={c} style={{ color: '#60a5fa' }} />, bar: 'linear-gradient(90deg, #2563eb, #93c5fd)', color: '#60a5fa' },
  Docs:     { icon: (c) => <FileText className={c} style={{ color: '#7dd3fc' }} />, bar: 'linear-gradient(90deg, #0284c7, #bae6fd)', color: '#7dd3fc' },
  Music:    { icon: (c) => <Music    className={c} style={{ color: '#f472b6' }} />, bar: 'linear-gradient(90deg, #db2777, #fbcfe8)', color: '#f472b6' },
  Archives: { icon: (c) => <Archive  className={c} style={{ color: '#fbbf24' }} />, bar: 'linear-gradient(90deg, #d97706, #fde68a)', color: '#fbbf24' },
  Programs: { icon: (c) => <LayoutGrid className={c} style={{ color: '#22d3ee' }} />, bar: 'linear-gradient(90deg, #0891b2, #a5f3fc)', color: '#22d3ee' },
};

export const CategoryBreakdown: React.FC<Props> = ({ categories }) => {
  return (
    <div className="w-full">
      <h2 className="text-[10px] font-bold tracking-[0.2em] text-slate-500 uppercase mb-5 pl-1 drop-shadow-sm">Category Breakdown</h2>

      {categories.length === 0 ? (
        <div className="text-center text-xs text-slate-500 py-8 font-medium">
          No categories to display.
        </div>
      ) : (
        <div className="space-y-5">
          {categories.map((cat, i) => {
            const style = categoryStyles[cat.name];
            return (
              <div key={i} className="group px-1">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <div className="p-1.5 rounded-lg bg-black/30 border border-white/5 transition-all duration-300 group-hover:bg-black/50 shadow-sm">
                      {style ? style.icon('w-3.5 h-3.5 drop-shadow-sm') : <File className="w-3.5 h-3.5 text-slate-500" />}
                    </div>
                    <span className="text-xs text-slate-300 font-semibold tracking-wide group-hover:text-white transition-colors">{cat.name}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] text-slate-500 font-mono font-medium">{cat.count} files</span>
                    <span
                      className="text-[11px] font-bold w-9 text-right"
                      style={{ color: style ? style.color : '#94a3b8' }}
                    >
                      {cat.percentage.toFixed(0)}%
                    </span>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="h-1 w-full rounded-full overflow-hidden bg-black/50 border border-white/[0.02] shadow-[inset_0_1px_2px_rgba(0,0,0,0.5)]">
                  <div
                    className="h-full rounded-full transition-all duration-1000 ease-out relative"
                    style={{
                      width: `${cat.percentage}%`,
                      background: style ? style.bar : 'rgba(255,255,255,0.2)',
                    }}
                  >
                    {style && (
                      <div className="absolute inset-0 bg-white/20 w-full h-full blur-[2px]"></div>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
