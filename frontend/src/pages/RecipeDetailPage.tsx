import React from 'react';
import { useParams } from 'react-router-dom';
import { ChefHat } from 'lucide-react';

export const RecipeDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();

  return (
    <div className="space-y-6">
      <div className="text-center">
        <ChefHat className="h-12 w-12 text-primary-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Recipe Detail</h1>
        <p className="text-gray-600">Viewing recipe: {slug}</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">
          Recipe detail view will be implemented here. This will show the full recipe with
          ingredients, instructions, notes, and metadata.
        </p>
      </div>
    </div>
  );
};
