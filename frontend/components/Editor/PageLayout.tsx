import { useRef, useEffect } from 'react';
import { Panel } from './Panel';
import { useDrop } from 'react-dnd';
import { PageLayout as PageLayoutType, Panel as PanelType } from '@/types';

interface PageLayoutProps {
  layout: PageLayoutType;
  panels: PanelType[];
  onLayoutChange?: (layout: PageLayoutType) => void;
  onPanelMove?: (panelId: string, newPosition: number) => void;
}

export function PageLayout({ layout, panels, onLayoutChange, onPanelMove }: PageLayoutProps) {
  const canvasRef = useRef<HTMLDivElement>(null);

  const [{ isOver }, drop] = useDrop({
    accept: 'PANEL',
    drop: (item: any, monitor) => {
      const offset = monitor.getSourceClientOffset();
      if (offset && onPanelMove) {
        // Calcul de la nouvelle position
        const rect = canvasRef.current?.getBoundingClientRect();
        if (rect) {
          const x = offset.x - rect.left;
          const y = offset.y - rect.top;
          // Logique pour déterminer la nouvelle position dans la grille
        }
      }
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  });

  useEffect(() => {
    drop(canvasRef);
  }, [drop]);

  const getGridStyle = () => {
    switch (layout?.type) {
      case 'standard':
        return {
          display: 'grid',
          gridTemplateColumns: `repeat(${layout.columns || 2}, 1fr)`,
          gridTemplateRows: `repeat(${layout.rows || 3}, 1fr)`,
          gap: '10px',
        };
      case 'dynamic':
        return {
          display: 'grid',
          gridTemplateAreas: layout.panels
            .map((p, i) => `"panel${i}"`)
            .join(' '),
          gap: '10px',
        };
      default:
        return {};
    }
  };

  return (
    <div 
      ref={canvasRef}
      className="w-full h-full bg-white rounded-lg shadow-inner p-4"
      style={getGridStyle()}
    >
      {panels?.map((panel, index) => (
        <Panel
          key={panel.id}
          panel={panel}
          layoutInfo={layout?.panels?.[index]}
          index={index}
        />
      ))}
      
      {isOver && (
        <div className="absolute inset-0 bg-blue-500 bg-opacity-10 pointer-events-none" />
      )}
    </div>
  );
}
