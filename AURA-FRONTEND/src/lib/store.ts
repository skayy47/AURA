import { create } from 'zustand';
import { Meta, CleaningConfig, CleanResult, ExploreData, Message, AuraStore } from './types';

export const useStore = create<AuraStore>((set) => ({
  sessionId: null,
  meta: null,
  preview: [],
  cleanResult: null,
  exploreData: null,
  chatHistory: [],

  setSession: (sessionId: string) => set({ sessionId }),

  setIngest: (meta: Meta, preview: Array<Record<string, any>>) =>
    set({ meta, preview, cleanResult: null, exploreData: null, chatHistory: [] }),

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
      cleanResult: null,
      exploreData: null,
      chatHistory: [],
    }),
}));
