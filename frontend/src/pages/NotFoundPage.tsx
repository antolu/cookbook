import React from 'react'
import { Link } from 'react-router-dom'
import { Home, AlertTriangle } from 'lucide-react'

export const NotFoundPage: React.FC = () => {
  return (
    <div className="text-center space-y-6">
      <div className="flex justify-center">
        <AlertTriangle className="h-16 w-16 text-gray-400" />
      </div>

      <div>
        <h1 className="text-6xl font-bold text-gray-900 mb-2">404</h1>
        <h2 className="text-2xl font-semibold text-gray-700 mb-4">
          Recipe Not Found
        </h2>
        <p className="text-gray-600 mb-8 max-w-md mx-auto">
          Sorry, we couldn't find the recipe you're looking for.
          It might have been moved or deleted.
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          to="/"
          className="btn btn-primary flex items-center gap-2"
        >
          <Home className="h-4 w-4" />
          Back to Home
        </Link>
        <Link
          to="/recipes"
          className="btn btn-outline"
        >
          Browse Recipes
        </Link>
      </div>
    </div>
  )
}