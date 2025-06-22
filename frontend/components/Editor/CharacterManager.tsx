import { useState } from 'react';
import { Project, Character } from '@/types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Plus, User, Sparkles } from 'lucide-react';
import { useCreateCharacter, useTrainCharacterLora } from '@/hooks/useCharacters';

export function CharacterManager({ project }: { project: Project | null }) {
  const [showForm, setShowForm] = useState(false);
  const [newCharacter, setNewCharacter] = useState({
    name: '',
    description: '',
    visualDescription: '',
  });

  const createCharacter = useCreateCharacter();
  const trainLora = useTrainCharacterLora();

  const handleCreate = async () => {
    if (project?.id) {
      await createCharacter.mutateAsync({
        projectId: project.id,
        ...newCharacter,
      });
      setShowForm(false);
      setNewCharacter({ name: '', description: '', visualDescription: '' });
    }
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold">Personnages</h3>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setShowForm(!showForm)}
        >
          <Plus className="mr-1 h-4 w-4" />
          Nouveau
        </Button>
      </div>

      {showForm && (
        <Card className="p-4 space-y-3">
          <Input
            placeholder="Nom du personnage"
            value={newCharacter.name}
            onChange={(e) => setNewCharacter({ ...newCharacter, name: e.target.value })}
          />
          <Textarea
            placeholder="Description (personnalité, rôle...)"
            value={newCharacter.description}
            onChange={(e) => setNewCharacter({ ...newCharacter, description: e.target.value })}
            rows={3}
          />
          <Textarea
            placeholder="Description visuelle (apparence, vêtements...)"
            value={newCharacter.visualDescription}
            onChange={(e) => setNewCharacter({ ...newCharacter, visualDescription: e.target.value })}
            rows={3}
          />
          <div className="flex gap-2">
            <Button onClick={handleCreate} size="sm">
              Créer
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setShowForm(false)}
            >
              Annuler
            </Button>
          </div>
        </Card>
      )}

      <div className="space-y-2">
        {project?.characters?.map((character) => (
          <Card key={character.id} className="p-3">
            <div className="flex items-start gap-3">
              <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center">
                <User className="h-6 w-6 text-gray-500" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium">{character.name}</h4>
                <p className="text-sm text-gray-600">{character.description}</p>
                <div className="mt-2 flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={character.loraStatus === 'training'}
                    onClick={() => trainLora.mutate(character.id)}
                  >
                    <Sparkles className="mr-1 h-3 w-3" />
                    {character.loraStatus === 'completed' ? 'Réentraîner' : 'Entraîner IA'}
                  </Button>
                  <span className="text-xs text-gray-500 self-center">
                    {character.loraStatus === 'completed' && '✓ Prêt'}
                    {character.loraStatus === 'training' && '⏳ En cours...'}
                  </span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
