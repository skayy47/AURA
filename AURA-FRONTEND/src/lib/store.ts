import { create } from 'zustand';
import { Meta, CleanResult, ExploreData, Message, AuraStore } from './types';

export const useStore = create<AuraStore>((set) => ({
  sessionId: null,
  meta: null,
  preview: [],
  ingestWarnings: [],
  cleanResult: null,
  exploreData: null,
  chatHistory: [],
  firstRun: true,
  provider: 'gemini',
  temperature: 0.7,

  setSession: (sessionId: string) => set({ sessionId }),

  setIngest: (meta: Meta, preview: Array<Record<string, any>>, warnings: string[] = []) =>
    set({
      meta,
      preview,
      ingestWarnings: warnings,
      cleanResult: null,
      exploreData: null,
      chatHistory: [],
    }),

  setClean: (result: CleanResult) => set((state) => ({
    cleanResult: result,
    meta: state.meta ? { ...state.meta, n_cols: result.cols_after } : state.meta,
  })),

  setExplore: (data: ExploreData) => set({ exploreData: data }),

  addMessage: (message: Message) =>
    set((state) => ({
      chatHistory: [...state.chatHistory, message],
    })),

  setFirstRun: (firstRun: boolean) => set({ firstRun }),
  setProvider: (provider: string) => set({ provider }),
  setTemperature: (temperature: number) => set({ temperature }),

  reset: () =>
    set({
      sessionId: null,
      meta: null,
      preview: [],
      ingestWarnings: [],
      cleanResult: null,
      exploreData: null,
      chatHistory: [],
      firstRun: true,
      provider: 'gemini',
      temperature: 0.7,
    }),
}));
