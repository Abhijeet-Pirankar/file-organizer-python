import React, { useState, useMemo } from 'react';
import { FileInfo } from '../types';
import { FolderSearch, Search, Image, FileText, Video, Music, Archive, LayoutGrid, File, CheckCircle2, AlertCircle } from 'lucide-react';

interface Props {
  files: FileInfo[];
  hasAnalyzed: boolean;
}

export const FilePreview: React.FC<Props> = ({ files, hasAnalyzed }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');

  const categories = useMemo(() => {
    const cats = new Set(files.map(f => f.category));
    return ['All', ...Array.from(cats).sort()];
  }, [files]);

  const filteredFiles = useMemo(() => {
    return files.filter(f => {
      const matchesSearch = f.filename.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = categoryFilter === 'All' || f.category === categoryFilter;
      return matchesSearch && matchesCategory;
    });
  }, [files, searchTerm, categoryFilter]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Images':   return <Image    className="w-4 h-4" style={{ color: '#c084fc' }} />;
      case 'PDFs':     return <FileText className="w-4 h-4" style={{ color: '#fb7185' }} />;
      case 'Videos':   return <Video    className="w-4 h-4" style={{ color: '#60a5fa' }} />;
      case 'Docs':     return <FileText className="w-4 h-4" style={{ color: '#7dd3fc' }} />;
      case 'Music':    return <Music    className="w-4 h-4" style={{ color: '#f472b6' }} />;
      case 'Archives': return <Archive  className="w-4 h-4" style={{ color: '#fbbf24' }} />;
      case 'Programs': return <LayoutGrid className="w-4 h-4" style={{ color: '#22d3ee' }} />;
      default:         return <File     className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <div className="h-full flex flex-col overflow-hidden bg-transparent">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-white/5 bg-black/20">
        <div className="flex items-center gap-3">
          <FolderSearch className="w-5 h-5 text-cyan-400 drop-shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
          <h2 className="text-sm font-semibold text-slate-200">File Preview</h2>
          <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-white/5 text-slate-400 border border-white/10 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)]">
            {files.length} files
          </span>
        </div>
        <div className="flex gap-3">
          <div className="relative group">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-cyan-400 transition-colors" />
            <input
              type="text"
              placeholder="Search files..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 text-xs font-medium text-slate-200 rounded-lg placeholder-slate-500 focus:outline-none w-56 transition-all glass-input"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-4 py-2 text-xs font-medium text-slate-300 rounded-lg focus:outline-none cursor-pointer min-w-[140px] transition-all glass-input hover:bg-white/5"
            style={{ appearance: 'none', backgroundImage: 'url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%2394a3b8%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E")', backgroundRepeat: 'no-repeat', backgroundPosition: 'right 12px top 50%', backgroundSize: '10px auto' }}
          >
            {categories.map(c => (
              <option key={c} value={c} style={{ background: '#0f172a' }}>{c === 'All' ? 'All Categories' : c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto relative custom-scrollbar">
        {!hasAnalyzed ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-b from-transparent to-black/20">
            <div className="w-24 h-24 rounded-3xl flex items-center justify-center relative bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 mb-6 shadow-[inset_0_1px_1px_rgba(255,255,255,0.1),0_8px_32px_rgba(0,0,0,0.2)] group hover:scale-105 transition-transform duration-500">
              <div className="absolute inset-0 bg-cyan-400/20 rounded-3xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <FolderSearch className="w-10 h-10 text-cyan-400 drop-shadow-md relative z-10" strokeWidth={1.5} />
            </div>
            <h3 className="text-xl font-bold text-slate-200 mb-3 tracking-wide">No files analyzed</h3>
            <p className="text-sm text-slate-400 text-center max-w-[280px] leading-relaxed">
              Select a target folder above and click <strong className="text-cyan-400 font-semibold">Analyze</strong> to preview its contents.
            </p>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 z-10 bg-[#0a0f1e]/90 backdrop-blur-md border-b border-white/5 shadow-sm">
              <tr>
                {['File Name', 'Size', 'Category', 'Status'].map((h, i) => (
                  <th
                    key={h}
                    className={`py-4 px-6 text-xs font-bold tracking-wider text-slate-400 uppercase ${i === 3 ? 'text-right' : ''}`}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredFiles.map((file, i) => {
                return (
                  <tr
                    key={i}
                    className="group transition-colors duration-200 border-b border-white/[0.03] last:border-0 hover:bg-white/[0.04]"
                  >
                    <td className="py-3.5 px-6">
                      <div className="flex items-center gap-4">
                        <div className="p-2 rounded-lg bg-black/20 border border-white/5 group-hover:bg-black/40 transition-colors shadow-sm">
                          {getCategoryIcon(file.category)}
                        </div>
                        <span className="text-sm text-slate-300 truncate max-w-[200px] lg:max-w-[300px] xl:max-w-[400px] font-medium group-hover:text-white transition-colors" title={file.filename}>
                          {file.filename}
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 px-6 text-sm text-slate-400 whitespace-nowrap font-medium">
                      {formatSize(file.size)}
                    </td>
                    <td className="py-3.5 px-6 text-sm text-slate-300">
                      <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-black/20 border border-white/5">
                        {file.category}
                      </span>
                    </td>
                    <td className="py-3.5 px-6 text-right">
                      {file.status === 'Ready' && (
                        <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wider text-slate-400 bg-slate-800/50 px-2 py-1 rounded border border-slate-700">
                          READY
                        </span>
                      )}
                      {file.status === 'Organized' && (
                        <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded border border-emerald-500/20 shadow-[0_0_8px_rgba(52,211,153,0.15)]">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          ORGANIZED
                        </span>
                      )}
                      {file.status === 'Error' && (
                        <span className="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-wider text-rose-400 bg-rose-500/10 px-2 py-1 rounded border border-rose-500/20">
                          <AlertCircle className="w-3.5 h-3.5" />
                          ERROR
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}

        {hasAnalyzed && filteredFiles.length === 0 && files.length > 0 && (
          <div className="py-24 flex flex-col items-center text-center animate-fade-in-up">
            <div className="p-4 rounded-2xl bg-black/20 border border-white/5 mb-4">
              <Search className="w-8 h-8 text-slate-500" />
            </div>
            <p className="text-sm font-medium text-slate-400">No files match your search criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};
