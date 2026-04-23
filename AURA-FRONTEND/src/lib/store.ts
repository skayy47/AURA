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

  setClean: (result: CleanResult) => set({ cleanResult: result }),

  setExplore: (data: ExploreData) => set({ exploreData: data }),

  addMessage: (message: Message) =>
    set((state) => ({
      chatHistory: [...state.chatHistory, message],
    })),

  reset: () =>
    set({
      sessionId: null,
      meta: null,
      preview: [],
      ingestWarnings: [],
      cleanResult: null,
      exploreData: null,
      chatHistory: [],
    }),
}));
