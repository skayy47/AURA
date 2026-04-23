export interface Meta {
  name: string;
  size_kb: number;
  format: string;
  n_rows: number;
  n_cols: number;
  columns: string[];
  dtypes: Record<string, string>;
  missing_total: number;
  missing_by_col: Record<string, number>;
  duplicate_rows: number;
  estimated_date_cols: string[];
  estimated_id_cols: string[];
  estimated_numeric_cols: string[];
  estimated_cat_cols: string[];
  memory_mb: number;
  encoding_detected?: string | null;
  has_header?: boolean;
}

export interface CleaningConfig {
  rename_columns: boolean;
  normalize_strings: boolean;
  detect_dates: boolean;
  remove_empty_cols: boolean;
  fill_missing: boolean;
  drop_duplicates: boolean;
}

export interface CleanLogEntry {
  step: string;
  detail: string;
  affected_columns?: string[];
  rows_changed?: number;
  status?: "ok" | "warn" | "error";
}

export interface CleanResult {
  session_id: string;
  rows_before: number;
  rows_after: number;
  cols_before: number;
  cols_after: number;
  log: CleanLogEntry[];
}

export type ColumnKind = "numeric" | "datetime" | "categorical" | "boolean" | "text" | "id" | "unknown";

export interface HistogramBin {
  bin: string;
  lo: number;
  hi: number;
  count: number;
}

export interface ColumnProfile {
  name: string;
  dtype: string;
  kind: ColumnKind;
  n_missing: number;
  missing_pct: number;
  n_unique: number;
  top_values: Array<{ value: string; count: number }>;
  mean?: number;
  median?: number;
  std?: number;
  min?: number;
  max?: number;
  p25?: number;
  p75?: number;
  skewness?: number;
  kurtosis?: number;
  histogram?: HistogramBin[];
  date_min?: string;
  date_max?: string;
  date_range_days?: number;
  error?: string;
}

export interface CorrelationMatrix {
  columns: string[];
  matrix: {
    index: string[];
    columns: string[];
    data: number[][];
  };
  top_pairs: Array<{ col_a: string; col_b: string; r: number }>;
}

export interface ChartRecommendation {
  type: "timeseries" | "scatter" | "histogram" | "bar_grouped" | "heatmap_corr";
  priority: number;
  rationale: string;
  column?: string;
  columns?: string[];
  x?: string;
  y?: string | string[];
  r?: number;
  points?: Array<Record<string, any>>;
  bars?: Array<{ label: string; value: number }>;
}

export interface DatasetProfile {
  n_rows: number;
  n_cols: number;
  memory_mb: number;
  missing_total: number;
  duplicate_rows: number;
  columns: ColumnProfile[];
  correlation: CorrelationMatrix | null;
  numeric_cols: string[];
  categorical_cols: string[];
  datetime_cols: string[];
  missing_by_col: Array<{ column: string; missing: number; pct: number }>;
}

export interface ExploreData {
  session_id: string;
  profile: DatasetProfile;
  recommendations: ChartRecommendation[];
  // backward-compat
  numeric_cols: string[];
  categorical_cols: string[];
  datetime_cols: string[];
  missing_heatmap: Array<{ column: string; missing: number; pct: number }>;
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
  ingestWarnings: string[];
  cleanResult: CleanResult | null;
  exploreData: ExploreData | null;
  chatHistory: Message[];
  setSession: (sessionId: string) => void;
  setIngest: (meta: Meta, preview: Array<any>, warnings?: string[]) => void;
  setClean: (result: CleanResult) => void;
  setExplore: (data: ExploreData) => void;
  addMessage: (message: Message) => void;
  reset: () => void;
}
