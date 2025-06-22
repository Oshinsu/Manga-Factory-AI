'use client';

import { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { useWebSocket } from '@/hooks/useWebSocket';
import { MangaEditor } from '@/components/Editor/MangaEditor';
import { PreviewPanel } from '@/components/Preview/PreviewPanel';
import { ControlPanel } from '@/components/Editor/ControlPanel';

export default function EditorPage() {
  const [project, setProject] = useState(null);
  const [selectedPage, setSelectedPage] = useState(0);
  const { status, sendMessage } = useWebSocket(project?.id);

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="flex h-screen bg-gray-100">
        {/* Panneau de contrôle */}
        <div className="w-80 bg-white shadow-lg">
          <ControlPanel 
            project={project}
            onGenerateStart={() => sendMessage({ type: 'start_generation' })}
          />
        </div>

        {/* Éditeur principal */}
        <div className="flex-1 overflow-hidden">
          <MangaEditor
            project={project}
            selectedPage={selectedPage}
            onPageSelect={setSelectedPage}
          />
        </div>

        {/* Panneau de prévisualisation */}
        <div className="w-96 bg-white shadow-lg">
          <PreviewPanel
            page={project?.chapters?.[0]?.pages?.[selectedPage]}
            onPanelEdit={(panelId, changes) => {
              sendMessage({ 
                type: 'edit_panel', 
                panelId, 
                changes 
              });
            }}
          />
        </div>
      </div>
    </DndProvider>
  );
}
