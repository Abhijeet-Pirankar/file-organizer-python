import { useState } from 'react';
import { Header } from './components/Header';
import { FolderSelector } from './components/FolderSelector';
import { CommandBar } from './components/CommandBar';
import { StatusBar } from './components/StatusBar';
import { FilePreview } from './components/FilePreview';
import { Statistics } from './components/Statistics';
import { organizerApi } from './services/organizerApi';
import { FileInfo, Statistics as StatsType, CategoryProgress } from './types';

function App() {
  const [folderPath, setFolderPath] = useState('');
  const [recursive, setRecursive] = useState(true);
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [stats, setStats] = useState<StatsType | null>(null);
  const [categories, setCategories] = useState<CategoryProgress[]>([]);
  
  const [status, setStatus] = useState('Ready');
  const [progress, setProgress] = useState(0);
  const [isOrganizing, setIsOrganizing] = useState(false);

  const handleBrowse = async () => {
    setStatus('Browsing...');
    try {
      const path = await organizerApi.browseFolder();
      if (path) {
        setFolderPath(path);
        setStatus('Folder selected');
      } else {
        setStatus('Ready');
      }
    } catch (e) {
      setStatus('Error browsing folder');
    }
  };

  const handleAnalyze = async () => {
    if (!folderPath) {
      setStatus('Please select a folder first');
      return;
    }
    
    setStatus('Analyzing folder...');
    setProgress(30);
    try {
      const data = await organizerApi.analyzeFolder(folderPath, recursive);
      setFiles(data.files);
      setStats(data.stats);
      setCategories(data.categories);
      setStatus(`Preview ready — ${data.files.length} files`);
      setProgress(100);
    } catch (e) {
      setStatus('Error analyzing folder');
      setProgress(0);
    }
  };

  const handleOrganize = async () => {
    if (!folderPath || files.length === 0) {
      setStatus('Please analyze a folder first');
      return;
    }
    
    setIsOrganizing(true);
    setStatus('Organizing files...');
    setProgress(10);
    
    try {
      const progressInterval = window.setInterval(() => {
        setProgress(p => Math.min(p + 15, 90));
      }, 300);
      
      const success = await organizerApi.organizeFiles(folderPath, recursive);
      
      window.clearInterval(progressInterval);
      
      if (success) {
        setFiles(prev => prev.map(f => ({ ...f, status: 'Organized' })));
        setStats(prev => prev ? { ...prev, organized: prev.totalFiles, duplicates: 0, others: 0 } : null);
        setStatus('Organization complete');
        setProgress(100);
      } else {
        setStatus('Error organizing files');
        setProgress(0);
      }
    } catch (e) {
      setStatus('Error organizing files');
      setProgress(0);
    } finally {
      setIsOrganizing(false);
    }
  };

  const handleUndo = async () => {
    setStatus('Undoing last operation...');
    setProgress(50);
    try {
      const success = await organizerApi.undoOrganize();
      if (success) {
        setStatus('Undo successful');
        setProgress(100);
        if (folderPath) {
          handleAnalyze();
        }
      } else {
        setStatus('Nothing to undo or error occurred');
        setProgress(0);
      }
    } catch (e) {
      setStatus('Error undoing');
      setProgress(0);
    }
  };

  const handleWatch = async () => {
    if (!folderPath) {
      setStatus('Please select a folder first');
      return;
    }
    
    setStatus('Toggling folder watch...');
    try {
      const res = await organizerApi.watchFolder(folderPath);
      if (res.status === 'started') {
        setStatus('Watching folder for changes...');
      } else {
        setStatus('Stopped watching folder');
      }
    } catch (e) {
      setStatus('Error toggling watch');
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] relative overflow-x-hidden text-slate-200 font-sans">
      <div className="absolute inset-0 noise-bg z-0"></div>
      
      {/* Subtle Premium Glows */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0 opacity-[0.15]">
        <div className="absolute top-[-10%] left-[20%] w-[40%] h-[40%] rounded-full bg-cyan-600/20 blur-[140px] mix-blend-screen"></div>
        <div className="absolute top-[30%] right-[-10%] w-[35%] h-[35%] rounded-full bg-blue-600/20 blur-[130px] mix-blend-screen"></div>
        <div className="absolute bottom-[-15%] left-[30%] w-[45%] h-[45%] rounded-full bg-indigo-500/10 blur-[150px] mix-blend-screen"></div>
      </div>
      
      <div className="relative z-10 w-full max-w-[1440px] mx-auto h-screen flex flex-col p-5 sm:p-6 lg:p-8 gap-5 lg:gap-6">
        
        {/* Layer 1: Header */}
        <div className="shrink-0 animate-fade-in-up" style={{ animationDelay: '0.0s' }}>
          <Header />
        </div>
        
        {/* Layer 2: Folder Selector */}
        <div className="shrink-0 glass-panel rounded-2xl animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <FolderSelector 
            folderPath={folderPath} 
            onBrowse={handleBrowse}
            recursive={recursive}
            onRecursiveChange={setRecursive}
          />
        </div>
        
        {/* Layer 3: Command Bar */}
        <div className="shrink-0 glass-panel rounded-xl animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
          <CommandBar 
            onAnalyze={handleAnalyze}
            onPreview={handleAnalyze}
            onOrganize={handleOrganize}
            onUndo={handleUndo}
            onWatch={handleWatch}
            isOrganizing={isOrganizing}
            hasFolder={!!folderPath}
          />
        </div>
        
        {/* Layer 4: Status / Progress */}
        <div className="shrink-0 animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
          <StatusBar status={status} progress={progress} />
        </div>
        
        {/* Layer 5: Two-column workspace */}
        <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-5 lg:gap-6 animate-fade-in-up" style={{ animationDelay: '0.4s' }}>
          
          {/* File Preview (65-70%) */}
          <div className="flex-[2] glass-panel rounded-2xl flex flex-col min-h-0 relative overflow-hidden">
            <FilePreview files={files} hasAnalyzed={stats !== null} />
          </div>
          
          {/* Statistics & Categories (30-35%) */}
          <div className="flex-[1] glass-panel rounded-2xl flex flex-col min-h-0 overflow-y-auto custom-scrollbar p-6 gap-6 relative">
            <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none rounded-2xl"></div>
            <Statistics stats={stats} categories={categories} />
          </div>
          
        </div>
        
      </div>
    </div>
  );
}

export default App;
