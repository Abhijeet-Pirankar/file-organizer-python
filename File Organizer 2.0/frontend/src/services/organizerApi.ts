import { FileInfo, Statistics, CategoryProgress } from '../types';

const API_BASE = 'http://127.0.0.1:8000/api';

export const organizerApi = {
  browseFolder: async (): Promise<string> => {
    try {
      const response = await fetch(`${API_BASE}/browse`);
      if (!response.ok) throw new Error('Failed to browse folder');
      const data = await response.json();
      return data.path || '';
    } catch (e) {
      console.error('Error browsing folder:', e);
      throw e;
    }
  },

  analyzeFolder: async (folder: string, recursive: boolean): Promise<{ files: FileInfo[], stats: Statistics, categories: CategoryProgress[] }> => {
    try {
      const response = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder, recursive })
      });
      if (!response.ok) throw new Error('Failed to analyze folder');
      return await response.json();
    } catch (e) {
      console.error('Error analyzing folder:', e);
      throw e;
    }
  },
  
  organizeFiles: async (folder: string, recursive: boolean = true): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/organize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder, recursive })
      });
      if (!response.ok) throw new Error('Failed to organize files');
      const data = await response.json();
      return data.success;
    } catch (e) {
      console.error('Error organizing files:', e);
      throw e;
    }
  },

  undoOrganize: async (): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/undo`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to undo');
      const data = await response.json();
      return data.success;
    } catch (e) {
      console.error('Error undoing organize:', e);
      throw e;
    }
  },

  watchFolder: async (folder: string): Promise<{status: string}> => {
    try {
      const response = await fetch(`${API_BASE}/watch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder })
      });
      if (!response.ok) throw new Error('Failed to watch folder');
      return await response.json();
    } catch (e) {
      console.error('Error toggling watch:', e);
      throw e;
    }
  }
};
