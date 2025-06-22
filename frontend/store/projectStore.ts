import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Project, Chapter, Page, Panel, Character } from '@/types';

interface ProjectState {
  currentProject: Project | null;
  projects: Project[];
  selectedChapter: number;
  selectedPage: number;
  selectedPanel: Panel | null;
  
  // Actions
  setProject: (project: Project) => void;
  updateProject: (updates: Partial<Project>) => void;
  addCharacter: (character: Character) => void;
  updateCharacter: (id: string, updates: Partial<Character>) => void;
  setSelectedPage: (pageIndex: number) => void;
  setSelectedPanel: (panel: Panel | null) => void;
  updatePanel: (panelId: string, updates: Partial<Panel>) => void;
}

export const useProjectStore = create<ProjectState>()(
  devtools(
    persist(
      (set, get) => ({
        currentProject: null,
        projects: [],
        selectedChapter: 0,
        selectedPage: 0,
        selectedPanel: null,

        setProject: (project) => set({ currentProject: project }),
        
        updateProject: (updates) => set((state) => ({
          currentProject: state.currentProject 
            ? { ...state.currentProject, ...updates }
            : null
        })),
        
        addCharacter: (character) => set((state) => ({
          currentProject: state.currentProject
            ? {
                ...state.currentProject,
                characters: [...state.currentProject.characters, character]
              }
            : null
        })),
        
        updateCharacter: (id, updates) => set((state) => ({
          currentProject: state.currentProject
            ? {
                ...state.currentProject,
                characters: state.currentProject.characters.map(c =>
                  c.id === id ? { ...c, ...updates } : c
                )
              }
            : null
        })),
        
        setSelectedPage: (pageIndex) => set({ selectedPage: pageIndex }),
        
        setSelectedPanel: (panel) => set({ selectedPanel: panel }),
        
        updatePanel: (panelId, updates) => set((state) => {
          if (!state.currentProject) return state;
          
          return {
            currentProject: {
              ...state.currentProject,
              chapters: state.currentProject.chapters.map(chapter => ({
                ...chapter,
                pages: chapter.pages.map(page => ({
                  ...page,
                  panels: page.panels.map(panel =>
                    panel.id === panelId ? { ...panel, ...updates } : panel
                  )
                }))
              }))
            }
          };
        }),
      }),
      {
        name: 'manga-factory-storage',
        partialize: (state) => ({ 
          projects: state.projects,
          currentProject: state.currentProject 
        }),
      }
    )
  )
);
