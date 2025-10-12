import React from 'react'
import { Link } from 'react-router-dom'
import { useFeaturedRecipes, useRecentRecipes } from '../hooks/useRecipes'
import { RecipeCard } from '../components/RecipeCard'
import { LoadingState } from '../components/LoadingSpinner'
import { ErrorBoundary } from '../components/ErrorBoundary'

export const HomePage: React.FC = () => {
  const { data: featuredRecipes, isLoading: featuredLoading } = useFeaturedRecipes(4)
  const { data: recentRecipes, isLoading: recentLoading } = useRecentRecipes(6)
  return (
    <div className="space-y-12">
      {/* Featured Recipes */}
      {featuredRecipes && featuredRecipes.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Featured Recipes</h2>
            <Link
              to="/recipes?featured=true"
              className="btn btn-outline btn-sm"
            >
              View All Featured
            </Link>
          </div>
          <ErrorBoundary>
            {featuredLoading ? (
              <LoadingState message="Loading featured recipes..." />
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {featuredRecipes.map((recipe) => (
                  <RecipeCard key={recipe.id} recipe={recipe} />
                ))}
              </div>
            )}
          </ErrorBoundary>
        </section>
      )}

      {/* Recent Recipes */}
      {recentRecipes && recentRecipes.length > 0 && (
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recent Recipes</h2>
            <Link
              to="/recipes"
              className="btn btn-outline btn-sm"
            >
              View All Recipes
            </Link>
          </div>
          <ErrorBoundary>
            {recentLoading ? (
              <LoadingState message="Loading recent recipes..." />
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recentRecipes.slice(0, 6).map((recipe) => (
                  <RecipeCard key={recipe.id} recipe={recipe} showFeaturedBadge={false} />
                ))}
              </div>
            )}
          </ErrorBoundary>
        </section>
      )}
    </div>
  )
}
