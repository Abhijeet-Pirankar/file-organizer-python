import React from 'react';
import { FolderOpen } from 'lucide-react';

interface Props {
  folderPath: string;
  onBrowse: () => void;
  recursive: boolean;
  onRecursiveChange: (val: boolean) => void;
}

export const FolderSelector: React.FC<Props> = ({ folderPath, onBrowse, recursive, onRecursiveChange }) => {
  return (
    <div className="flex flex-col gap-3 w-full p-6">
      <label className="text-[11px] font-bold tracking-widest text-slate-400 uppercase ml-1 drop-shadow-sm flex items-center gap-2">
        Target Folder
        <div className="h-px flex-1 bg-gradient-to-r from-white/10 to-transparent"></div>
      </label>
      
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center w-full">
        <div className="flex-1 flex w-full relative group shadow-sm rounded-xl">
          <div className="flex-1 flex items-center px-4 py-3 min-w-0 overflow-hidden glass-input rounded-l-xl border-r-0 relative z-10 transition-all duration-300">
            <FolderOpen className="w-5 h-5 text-cyan-400 flex-shrink-0 mr-3 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
            <span className={`text-sm tracking-wide truncate ${folderPath ? 'text-slate-200 font-medium' : 'text-slate-500 font-normal'}`}>
              {folderPath || 'Select a folder to organize...'}
            </span>
          </div>
          <button
            onClick={onBrowse}
            className="flex items-center gap-2 px-6 py-3 text-sm font-semibold tracking-wide text-slate-200 hover:text-white rounded-r-xl glass-button transition-all duration-300 z-10"
          >
            Browse
          </button>
        </div>

        <label className="flex items-center gap-3 cursor-pointer group flex-shrink-0 mr-2 sm:ml-2 mt-2 sm:mt-0 p-2 rounded-lg hover:bg-white/5 transition-colors">
          <div className="relative flex items-center justify-center w-5 h-5">
            <input
              type="checkbox"
              checked={recursive}
              onChange={(e) => onRecursiveChange(e.target.checked)}
              className="sr-only"
            />
            <div
              className={`w-5 h-5 rounded-[6px] flex items-center justify-center transition-all duration-300 ${recursive ? 'bg-cyan-500/20 border-cyan-400 shadow-[0_0_12px_rgba(6,182,212,0.4),inset_0_1px_1px_rgba(255,255,255,0.2)]' : 'bg-black/40 border-white/10 group-hover:bg-black/20 group-hover:border-white/20'}`}
              style={{ borderWidth: '1px' }}
            >
              {recursive && (
                <svg className="w-3.5 h-3.5 text-cyan-300 drop-shadow-[0_0_2px_rgba(6,182,212,1)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              )}
            </div>
          </div>
          <span className="text-sm text-slate-400 group-hover:text-slate-200 transition-colors font-medium">Include Subfolders</span>
        </label>
      </div>
    </div>
  );
};
