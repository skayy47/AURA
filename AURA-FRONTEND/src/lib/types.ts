export interface Meta {
  file_name: string;
  file_size_kb: number;
  rows: number;
  cols: number;
  format: string;
  missing_count: number;
  columns: string[];
  dtypes: Record<string, string>;
}

export interface CleaningConfig {
  rename_columns: boolean;
  normalize_strings: boolean;
  detect_dates: boolean;
  remove_empty_cols: boolean;
  fill_missing: boolean;
  drop_duplicates: boolean;
}

export interface CleanResult {
  session_id: string;
  rows_before: number;
  rows_after: number;
  cols_before: number;
  cols_after: number;
  log: Array<{
    step: string;
    detail: string;
    affected_columns?: string[];
  }>;
}

export interface ExploreData {
  session_id: string;
  profile: Record<string, any>;
  numeric_cols: string[];
  categorical_cols: string[];
  datetime_cols: string[];
  missing_heatmap: Array<{ column: string; missing: number }>;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  ts?: number;
}

export interface AuraStore {
  sessionId: string | null;
  meta: Meta | null;
  preview: Array<Record<string, any>>;
  cleanResult: CleanResult | null;
  exploreData: ExploreData | null;
  chatHistory: Message[];
  setSession: (sessionId: string) => void;
  setIngest: (meta: Meta, preview: Array<any>) => void;
  setClean: (result: CleanResult) => void;
  setExplore: (data: ExploreData) => void;
  addMessage: (message: Message) => void;
  reset: () => void;
}
