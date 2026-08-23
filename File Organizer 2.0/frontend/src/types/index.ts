export interface FileInfo {
  filename: string;
  size: number; // in bytes
  category: string;
  status: 'Ready' | 'Organized' | 'Error';
  path?: string;
}

export interface Statistics {
  totalFiles: number;
  organized: number;
  duplicates: number;
  errors: number;
  others: number;
  totalSize: number; // in bytes
}

export interface CategoryProgress {
  name: string;
  count: number;
  percentage: number;
}
