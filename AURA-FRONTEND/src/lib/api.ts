import { Meta, CleaningConfig, CleanResult, ExploreData, Message } from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function uploadFile(file: File): Promise<{ sessionId: string; meta: Meta; preview: Array<Record<string, any>> }> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_URL}/api/ingest`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

export async function runCleaning(
  sessionId: string,
  config: CleaningConfig
): Promise<CleanResult> {
  const response = await fetch(`${API_URL}/api/clean`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, config }),
  });

  if (!response.ok) {
    throw new Error(`Cleaning failed: ${response.statusText}`);
  }

  return response.json();
}

export async function fetchExplore(sessionId: string): Promise<ExploreData> {
  const response = await fetch(`${API_URL}/api/explore/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Explore failed: ${response.statusText}`);
  }

  return response.json();
}

export async function* streamAsk(
  sessionId: string,
  question: string,
  provider: 'claude' | 'openai'
): AsyncGenerator<string> {
  const response = await fetch(`${API_URL}/api/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      question,
      provider,
    }),
  });

  if (!response.ok) {
    throw new Error(`Ask failed: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error('No response body');

  const decoder = new TextDecoder();
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split('\n').filter(Boolean);

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') break;
        try {
          const parsed = JSON.parse(data);
          yield parsed.chunk || '';
        } catch {
          // Silently ignore parsing errors
        }
      }
    }
  }
}

export function exportUrl(sessionId: string, format: 'csv' | 'xlsx' | 'json' | 'parquet'): string {
  return `${API_URL}/api/export/${sessionId}/${format}`;
}
