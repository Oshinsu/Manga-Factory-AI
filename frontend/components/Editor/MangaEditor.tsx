import { useDrop } from 'react-dnd';
import { PanelCanvas } from './PanelCanvas';
import { PageLayout } from './PageLayout';

interface MangaEditorProps {
  project: Project;
  selectedPage: number;
  onPageSelect: (page: number) => void;
}

export function MangaEditor({ project, selectedPage, onPageSelect }: MangaEditorProps) {
  const currentPage = project?.chapters?.[0]?.pages?.[selectedPage];

  const [{ canDrop, isOver }, drop] = useDrop(() => ({
    accept: 'panel',
    drop: (item, monitor) => {
      const delta = monitor.getDifferenceFromInitialOffset();
      // Logique de placement
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
      canDrop: monitor.canDrop(),
    }),
  }));

  return (
    <div className="h-full flex flex-col">
      {/* Barre d'outils */}
      <div className="h-16 bg-gray-800 text-white flex items-center px-4">
        <h2 className="text-xl font-semibold">
          Page {selectedPage + 1} / {project?.chapters?.[0]?.pages?.length || 0}
        </h2>
      </div>

      {/* Zone de travail */}
      <div ref={drop} className="flex-1 relative bg-gray-200 overflow-auto p-8">
        <PageLayout 
          layout={currentPage?.layout}
          panels={currentPage?.panels}
        />
      </div>

      {/* Navigation pages */}
      <div className="h-24 bg-gray-100 border-t overflow-x-auto flex gap-2 p-2">
        {project?.chapters?.[0]?.pages?.map((page, idx) => (
          <div
            key={page.id}
            onClick={() => onPageSelect(idx)}
            className={`
              w-16 h-20 bg-white rounded cursor-pointer transition-all
              ${selectedPage === idx ? 'ring-2 ring-blue-500' : ''}
            `}
          >
            {/* Miniature */}
          </div>
        ))}
      </div>
    </div>
  );
}
