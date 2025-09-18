import React from 'react'
import { Link } from 'react-router-dom'
import { ChefHat, Clock, Users, Star } from 'lucide-react'
import { useFeaturedRecipes, useRecentRecipes } from '../hooks/useRecipes'
import { RecipeCard } from '../components/RecipeCard'
import { LoadingState } from '../components/LoadingSpinner'
import { ErrorBoundary } from '../components/ErrorBoundary'

export const HomePage: React.FC = () => {
  const { data: featuredRecipes, isLoading: featuredLoading } = useFeaturedRecipes(4)
  const { data: recentRecipes, isLoading: recentLoading } = useRecentRecipes(6)
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12">
        <div className="flex justify-center mb-6">
          <ChefHat className="h-16 w-16 text-primary-600" />
        </div>
        <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
          Welcome to Cookbook
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Organize, discover, and share your favorite recipes in a beautiful,
          modern interface. From quick weeknight dinners to elaborate weekend
          projects.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/recipes"
            className="btn btn-primary btn-lg"
          >
            Browse Recipes
          </Link>
          <Link
            to="/search"
            className="btn btn-outline btn-lg"
          >
            Search Recipes
          </Link>
        </div>
      </section>

      {/* Features Section */}
      <section className="grid md:grid-cols-3 gap-8">
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Clock className="h-12 w-12 text-primary-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Time Tracking
          </h3>
          <p className="text-gray-600">
            Keep track of prep time, cook time, and difficulty levels to plan
            your meals perfectly.
          </p>
        </div>

        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Users className="h-12 w-12 text-primary-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Serving Sizes
          </h3>
          <p className="text-gray-600">
            Easily scale recipes up or down based on how many people you're
            cooking for.
          </p>
        </div>

        <div className="text-center">
          <div className="flex justify-center mb-4">
            <Star className="h-12 w-12 text-primary-600" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Featured Recipes
          </h3>
          <p className="text-gray-600">
            Discover curated recipes and seasonal favorites handpicked for you.
          </p>
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div>
            <div className="text-3xl font-bold text-primary-600 mb-1">150+</div>
            <div className="text-sm text-gray-600">Recipes</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600 mb-1">25+</div>
            <div className="text-sm text-gray-600">Cuisines</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600 mb-1">10+</div>
            <div className="text-sm text-gray-600">Categories</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-primary-600 mb-1">500+</div>
            <div className="text-sm text-gray-600">Tips & Notes</div>
          </div>
        </div>
      </section>

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

      {/* CTA Section */}
      <section className="bg-primary-50 rounded-lg p-8 text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Ready to start cooking?
        </h2>
        <p className="text-lg text-gray-600 mb-6 max-w-2xl mx-auto">
          Explore our collection of carefully curated recipes, from beginner-friendly
          meals to gourmet masterpieces.
        </p>
        <Link
          to="/recipes"
          className="btn btn-primary btn-lg"
        >
          Explore Recipes
        </Link>
      </section>
    </div>
  )
}