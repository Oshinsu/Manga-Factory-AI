import { useState } from 'react';
import { Page, Panel } from '@/types';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Download, Eye, Maximize2 } from 'lucide-react';

interface PreviewPanelProps {
  page?: Page;
  onPanelEdit: (panelId: string, changes: any) => void;
}

export function PreviewPanel({ page, onPanelEdit }: PreviewPanelProps) {
  const [selectedPanel, setSelectedPanel] = useState<Panel | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [dialogueText, setDialogueText] = useState('');

  const handleDialogueEdit = () => {
    if (selectedPanel) {
      onPanelEdit(selectedPanel.id, {
        dialogue: dialogueText.split('\n').map(line => {
          const [character, ...text] = line.split(':');
          return { character: character.trim(), text: text.join(':').trim() };
        })
      });
      setEditMode(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h3 className="text-lg font-semibold">Aperçu de la page {page?.pageNumber}</h3>
      </div>

      <Tabs defaultValue="page" className="flex-1">
        <TabsList className="w-full">
          <TabsTrigger value="page" className="flex-1">Page complète</TabsTrigger>
          <TabsTrigger value="panels" className="flex-1">Cases</TabsTrigger>
          <TabsTrigger value="dialogue" className="flex-1">Dialogues</TabsTrigger>
        </TabsList>

        <TabsContent value="page" className="p-4">
          <div className="relative aspect-[210/297] bg-gray-100 rounded-lg overflow-hidden">
            {page?.fullPageImage && (
              <img 
                src={page.fullPageImage} 
                alt="Page preview"
                className="w-full h-full object-contain"
              />
            )}
          </div>
          
          <div className="mt-4 flex gap-2">
            <Button variant="outline" size="sm">
              <Eye className="mr-2 h-4 w-4" />
              Plein écran
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Télécharger
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="panels" className="p-4">
          <div className="grid grid-cols-2 gap-4">
            {page?.panels.map((panel) => (
              <div
                key={panel.id}
                onClick={() => setSelectedPanel(panel)}
                className={`
                  cursor-pointer border-2 rounded-lg overflow-hidden
                  ${selectedPanel?.id === panel.id ? 'border-blue-500' : 'border-gray-200'}
                `}
              >
                {panel.imageUrl && (
                  <img 
                    src={panel.imageUrl} 
                    alt={`Panel ${panel.panelNumber}`}
                    className="w-full h-32 object-cover"
                  />
                )}
                <div className="p-2 bg-gray-50">
                  <p className="text-sm font-medium">Case {panel.panelNumber}</p>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="dialogue" className="p-4">
          {selectedPanel ? (
            <div className="space-y-4">
              <h4 className="font-medium">Case {selectedPanel.panelNumber}</h4>
              
              {editMode ? (
                <>
                  <Textarea
                    value={dialogueText}
                    onChange={(e) => setDialogueText(e.target.value)}
                    placeholder="Personnage: Texte du dialogue"
                    rows={6}
                  />
                  <div className="flex gap-2">
                    <Button onClick={handleDialogueEdit}>Sauvegarder</Button>
                    <Button variant="outline" onClick={() => setEditMode(false)}>
                      Annuler
                    </Button>
                  </div>
                </>
              ) : (
                <>
                  <div className="space-y-2">
                    {selectedPanel.dialogue?.map((d, i) => (
                      <div key={i} className="p-2 bg-gray-50 rounded">
                        <span className="font-medium">{d.character}:</span> {d.text}
                      </div>
                    )) || <p className="text-gray-500">Aucun dialogue</p>}
                  </div>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setEditMode(true);
                      setDialogueText(
                        selectedPanel.dialogue
                          ?.map(d => `${d.character}: ${d.text}`)
                          .join('\n') || ''
                      );
                    }}
                  >
                    Modifier les dialogues
                  </Button>
                </>
              )}
            </div>
          ) : (
            <p className="text-gray-500 text-center">Sélectionnez une case</p>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
