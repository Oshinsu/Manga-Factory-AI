import { useState } from 'react';
import { Project, MangaStyle } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Play, Settings, Users, FileText, Download } from 'lucide-react';
import { CharacterManager } from './CharacterManager';
import { GenerationSettings } from './GenerationSettings';
import { ExportOptions } from './ExportOptions';

interface ControlPanelProps {
  project: Project | null;
  onGenerateStart: () => void;
  onProjectUpdate?: (updates: Partial<Project>) => void;
}

export function ControlPanel({ project, onGenerateStart, onProjectUpdate }: ControlPanelProps) {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerate = () => {
    setIsGenerating(true);
    onGenerateStart();
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-xl font-bold">Manga Factory</h2>
      </div>

      <Tabs defaultValue="project" className="flex-1">
        <TabsList className="w-full">
          <TabsTrigger value="project" className="flex-1">
            <FileText className="mr-1 h-4 w-4" />
            Projet
          </TabsTrigger>
          <TabsTrigger value="characters" className="flex-1">
            <Users className="mr-1 h-4 w-4" />
            Personnages
          </TabsTrigger>
          <TabsTrigger value="settings" className="flex-1">
            <Settings className="mr-1 h-4 w-4" />
            Paramètres
          </TabsTrigger>
          <TabsTrigger value="export" className="flex-1">
            <Download className="mr-1 h-4 w-4" />
            Export
          </TabsTrigger>
        </TabsList>

        <TabsContent value="project" className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Titre du manga</label>
            <Input
              value={project?.title || ''}
              onChange={(e) => onProjectUpdate?.({ title: e.target.value })}
              placeholder="Mon super manga"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Synopsis</label>
            <Textarea
              value={project?.synopsis || ''}
              onChange={(e) => onProjectUpdate?.({ synopsis: e.target.value })}
              placeholder="Un lycéen timide découvre qu'il peut parler aux animaux..."
              rows={4}
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Style</label>
            <Select
              value={project?.style || 'shonen'}
              onValueChange={(value) => onProjectUpdate?.({ style: value as MangaStyle })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="shonen">Shōnen</SelectItem>
                <SelectItem value="shojo">Shōjo</SelectItem>
                <SelectItem value="seinen">Seinen</SelectItem>
                <SelectItem value="josei">Josei</SelectItem>
                <SelectItem value="kodomo">Kodomo</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Button 
            onClick={handleGenerate}
            disabled={!project?.synopsis || isGenerating}
            className="w-full"
          >
            <Play className="mr-2 h-4 w-4" />
            {isGenerating ? 'Génération en cours...' : 'Lancer la génération'}
          </Button>
        </TabsContent>

        <TabsContent value="characters">
          <CharacterManager project={project} />
        </TabsContent>

        <TabsContent value="settings">
          <GenerationSettings project={project} />
        </TabsContent>

        <TabsContent value="export">
          <ExportOptions project={project} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
