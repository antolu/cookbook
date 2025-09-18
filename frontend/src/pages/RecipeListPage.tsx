import React from 'react'
import { BookOpen } from 'lucide-react'

export const RecipeListPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <BookOpen className="h-12 w-12 text-primary-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900 mb-2">All Recipes</h1>
        <p className="text-gray-600">
          Browse through our complete collection of recipes
        </p>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-500">
          Recipe list will be implemented here. This will show a paginated grid
          of recipe cards with search and filtering capabilities.
        </p>
      </div>
    </div>
  )
}