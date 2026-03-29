import React from 'react';
import { Search } from 'lucide-react';

export const SearchPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <Search className="h-12 w-12 text-primary-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Search Recipes</h1>
        <p className="text-gray-600">Find recipes by name, ingredients, cuisine, or difficulty</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">
          Search interface will be implemented here. This will include filters for cuisine,
          difficulty, cooking time, and more.
        </p>
      </div>
    </div>
  );
};
