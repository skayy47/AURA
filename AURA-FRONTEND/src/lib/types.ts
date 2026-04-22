export interface Meta {
  name: string;
  size_kb: number;
  n_rows: number;
  n_cols: number;
  format: string;
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
  before_rows: number;
  before_cols: number;
  after_rows: number;
  after_cols: number;
  log: Array<{
    step: string;
    detail: string;
    affected_columns?: string[];
  }>;
}

export interface ExploreData {
  n_rows: number;
  n_cols: number;
  numeric_count: number;
  categorical_count: number;
  datetime_count: number;
  missing_total: number;
  column_overview: Array<any>;
}

export interface Message {
  role: 'user' | 'assistant';
  content: string;
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
