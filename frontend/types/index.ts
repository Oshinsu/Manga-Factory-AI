export interface Project {
  id: string;
  title: string;
  synopsis: string;
  style: MangaStyle;
  status: ProjectStatus;
  chapters: Chapter[];
  characters: Character[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Chapter {
  id: string;
  number: number;
  title: string;
  synopsis: string;
  pages: Page[];
}

export interface Page {
  id: string;
  pageNumber: number;
  layout: PageLayout;
  panels: Panel[];
  fullPageImage?: string;
}

export interface Panel {
  id: string;
  panelNumber: number;
  description: string;
  dialogue: Dialogue[];
  imageUrl?: string;
  bounds?: Rectangle;
  soundEffects?: SoundEffect[];
}

export interface Character {
  id: string;
  name: string;
  description: string;
  visualDescription: string;
  referenceImages: string[];
  loraPath?: string;
  loraStatus: 'pending' | 'training' | 'completed' | 'failed';
}

export interface Dialogue {
  character: string;
  text: string;
  emotion?: string;
}

export interface SoundEffect {
  text: string;
  style: 'impact' | 'whisper' | 'echo';
  position?: Point;
}

export type MangaStyle = 'shonen' | 'shojo' | 'seinen' | 'josei' | 'kodomo';
export type ProjectStatus = 'draft' | 'generating' | 'completed' | 'error';

export interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Point {
  x: number;
  y: number;
}

export interface PageLayout {
  type: 'standard' | 'dynamic' | 'splash';
  columns: number;
  rows: number;
  panels: PanelLayout[];
}

export interface PanelLayout {
  gridArea: string;
  aspectRatio?: number;
}
