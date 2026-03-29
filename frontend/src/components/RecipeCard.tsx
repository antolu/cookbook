import React from 'react';
import { Link } from 'react-router-dom';
import { Clock, Users, Star, ChefHat } from 'lucide-react';
import { RecipeListItem } from '../types';
import { formatTime } from '../utils/time';

interface RecipeCardProps {
  recipe: RecipeListItem;
  showFeaturedBadge?: boolean;
}

export const RecipeCard: React.FC<RecipeCardProps> = ({ recipe, showFeaturedBadge = true }) => {
  return (
    <Link to={`/recipes/${recipe.slug}`} className="recipe-card block group">
      <div className="relative">
        {/* Recipe Image */}
        <div className="recipe-card-image-container relative overflow-hidden bg-gray-100">
          {recipe.image_url ? (
            <img
              src={recipe.image_url}
              alt={recipe.name}
              className="recipe-card-image w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
            />
          ) : (
            <div className="recipe-card-image w-full h-48 flex items-center justify-center bg-gray-100">
              <ChefHat className="h-12 w-12 text-gray-400" />
            </div>
          )}

          {/* Featured Badge */}
          {showFeaturedBadge && recipe.is_featured && (
            <div className="absolute top-2 right-2">
              <Star className="h-6 w-6 text-yellow-400 fill-current" />
            </div>
          )}
        </div>

        {/* Recipe Content */}
        <div className="recipe-card-content">
          <h3 className="recipe-card-title group-hover:text-primary-600">{recipe.name}</h3>

          {recipe.description && <p className="recipe-card-description">{recipe.description}</p>}

          {/* Recipe Meta */}
          <div className="recipe-card-meta">
            {/* Servings */}
            {recipe.servings && (
              <div className="flex items-center gap-1">
                <Users className="h-3 w-3" />
                <span>{recipe.servings}</span>
              </div>
            )}

            {/* Total Time */}
            {recipe.total_time && (
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                <span>{formatTime(recipe.total_time)}</span>
              </div>
            )}

            {/* Difficulty */}
            {recipe.difficulty && (
              <span className={`tag tag-difficulty-${recipe.difficulty}`}>{recipe.difficulty}</span>
            )}

            {/* Cuisine */}
            {recipe.cuisine && <span className="tag">{recipe.cuisine}</span>}
          </div>

          {/* Tags */}
          {recipe.tags && recipe.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {recipe.tags.slice(0, 3).map(tag => (
                <span key={tag} className="tag text-xs">
                  {tag}
                </span>
              ))}
              {recipe.tags.length > 3 && (
                <span className="tag text-xs">+{recipe.tags.length - 3} more</span>
              )}
            </div>
          )}
        </div>
      </div>
    </Link>
  );
};
