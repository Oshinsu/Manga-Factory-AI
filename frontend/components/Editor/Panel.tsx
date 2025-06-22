import { useDrag } from 'react-dnd';
import { Panel as PanelType, PanelLayout } from '@/types';
import Image from 'next/image';
import { Edit2, Trash2, RefreshCw } from 'lucide-react';

interface PanelProps {
  panel: PanelType;
  layoutInfo?: PanelLayout;
  index: number;
  onEdit?: () => void;
  onDelete?: () => void;
  onRegenerate?: () => void;
}

export function Panel({ panel, layoutInfo, index, onEdit, onDelete, onRegenerate }: PanelProps) {
  const [{ isDragging }, drag] = useDrag({
    type: 'PANEL',
    item: { id: panel.id, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const gridAreaStyle = layoutInfo?.gridArea ? {
    gridArea: layoutInfo.gridArea,
  } : {};

  return (
    <div
      ref={drag}
      className={`
        relative group border-2 border-gray-300 rounded-lg overflow-hidden
        ${isDragging ? 'opacity-50' : ''}
        hover:border-blue-500 transition-all cursor-move
      `}
      style={gridAreaStyle}
    >
      {/* Image de la case */}
      {panel.imageUrl ? (
        <Image
          src={panel.imageUrl}
          alt={`Panel ${panel.panelNumber}`}
          fill
          className="object-cover"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-gray-100">
          <p className="text-gray-500">Panel {panel.panelNumber}</p>
        </div>
      )}

      {/* Overlay avec dialogues */}
      {panel.dialogue?.length > 0 && (
        <div className="absolute inset-x-0 bottom-0 bg-black bg-opacity-60 text-white p-2">
          {panel.dialogue.map((d, i) => (
            <p key={i} className="text-xs">
              <span className="font-bold">{d.character}:</span> {d.text}
            </p>
          ))}
        </div>
      )}

      {/* Actions */}
      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="flex gap-1">
          <button
            onClick={onEdit}
            className="p-1 bg-white rounded shadow hover:bg-gray-100"
          >
            <Edit2 size={16} />
          </button>
          <button
            onClick={onRegenerate}
            className="p-1 bg-white rounded shadow hover:bg-gray-100"
          >
            <RefreshCw size={16} />
          </button>
          <button
            onClick={onDelete}
            className="p-1 bg-white rounded shadow hover:bg-gray-100"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
