import { render, screen, fireEvent } from '@testing-library/react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { MangaEditor } from '@/components/Editor/MangaEditor';

const mockProject = {
  id: '123',
  title: 'Test Manga',
  chapters: [{
    id: '456',
    number: 1,
    pages: [{
      id: '789',
      pageNumber: 1,
      layout: { type: 'standard', columns: 2, rows: 3 },
      panels: []
    }]
  }]
};

describe('MangaEditor', () => {
  it('renders correctly', () => {
    render(
      <DndProvider backend={HTML5Backend}>
        <MangaEditor
          project={mockProject}
          selectedPage={0}
          onPageSelect={jest.fn()}
        />
      </DndProvider>
    );

    expect(screen.getByText('Page 1 / 1')).toBeInTheDocument();
  });

  it('handles page selection', () => {
    const onPageSelect = jest.fn();
    
    render(
      <DndProvider backend={HTML5Backend}>
        <MangaEditor
          project={mockProject}
          selectedPage={0}
          onPageSelect={onPageSelect}
        />
      </DndProvider>
    );

    // Test de sélection de page
    const pageThumb = screen.getByRole('button', { name: /page 1/i });
    fireEvent.click(pageThumb);
    
    expect(onPageSelect).toHaveBeenCalledWith(0);
  });
});
