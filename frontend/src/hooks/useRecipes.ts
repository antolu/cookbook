import { useQuery, useMutation, useQueryClient } from 'react-query'
import toast from 'react-hot-toast'
import { recipeApi } from '../services/api'
import {
  Recipe,
  RecipeListItem,
  RecipeCreate,
  RecipeUpdate,
  RecipeSearchParams,
  RecipeSearchResponse,
} from '../types'

// Query keys
export const RECIPE_KEYS = {
  all: ['recipes'] as const,
  lists: () => [...RECIPE_KEYS.all, 'list'] as const,
  list: (params?: any) => [...RECIPE_KEYS.lists(), params] as const,
  details: () => [...RECIPE_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...RECIPE_KEYS.details(), id] as const,
  search: (params: RecipeSearchParams) => [...RECIPE_KEYS.all, 'search', params] as const,
  featured: () => [...RECIPE_KEYS.all, 'featured'] as const,
  recent: () => [...RECIPE_KEYS.all, 'recent'] as const,
  categories: () => [...RECIPE_KEYS.all, 'categories'] as const,
  cuisines: () => [...RECIPE_KEYS.all, 'cuisines'] as const,
  tags: () => [...RECIPE_KEYS.all, 'tags'] as const,
}

// Get all recipes
export function useRecipes(params?: {
  skip?: number
  limit?: number
  featured_only?: boolean
}) {
  return useQuery({
    queryKey: RECIPE_KEYS.list(params),
    queryFn: () => recipeApi.getRecipes(params),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Search recipes
export function useSearchRecipes(params: RecipeSearchParams) {
  return useQuery({
    queryKey: RECIPE_KEYS.search(params),
    queryFn: () => recipeApi.searchRecipes(params),
    enabled: !!(params.q || params.category || params.cuisine || params.difficulty || params.tags?.length),
    staleTime: 2 * 60 * 1000, // 2 minutes for search results
  })
}

// Get featured recipes
export function useFeaturedRecipes(limit?: number) {
  return useQuery({
    queryKey: RECIPE_KEYS.featured(),
    queryFn: () => recipeApi.getFeaturedRecipes(limit),
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get recent recipes
export function useRecentRecipes(limit?: number) {
  return useQuery({
    queryKey: RECIPE_KEYS.recent(),
    queryFn: () => recipeApi.getRecentRecipes(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Get single recipe
export function useRecipe(identifier: string) {
  return useQuery({
    queryKey: RECIPE_KEYS.detail(identifier),
    queryFn: () => recipeApi.getRecipe(identifier),
    enabled: !!identifier,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Get categories
export function useCategories() {
  return useQuery({
    queryKey: RECIPE_KEYS.categories(),
    queryFn: () => recipeApi.getCategories(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Get cuisines
export function useCuisines() {
  return useQuery({
    queryKey: RECIPE_KEYS.cuisines(),
    queryFn: () => recipeApi.getCuisines(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Get tags
export function useTags() {
  return useQuery({
    queryKey: RECIPE_KEYS.tags(),
    queryFn: () => recipeApi.getTags(),
    staleTime: 30 * 60 * 1000, // 30 minutes
  })
}

// Create recipe mutation
export function useCreateRecipe() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (recipe: RecipeCreate) => recipeApi.createRecipe(recipe),
    onSuccess: (newRecipe) => {
      // Invalidate relevant queries
      queryClient.invalidateQueries(RECIPE_KEYS.lists())
      queryClient.invalidateQueries(RECIPE_KEYS.featured())
      queryClient.invalidateQueries(RECIPE_KEYS.recent())

      // Add to detail cache
      queryClient.setQueryData(RECIPE_KEYS.detail(newRecipe.id), newRecipe)
      queryClient.setQueryData(RECIPE_KEYS.detail(newRecipe.slug), newRecipe)

      toast.success(`Recipe "${newRecipe.name}" created successfully!`)
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to create recipe'
      toast.error(message)
    },
  })
}

// Update recipe mutation
export function useUpdateRecipe() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, recipe }: { id: string; recipe: RecipeUpdate }) =>
      recipeApi.updateRecipe(id, recipe),
    onSuccess: (updatedRecipe) => {
      // Update caches
      queryClient.setQueryData(RECIPE_KEYS.detail(updatedRecipe.id), updatedRecipe)
      queryClient.setQueryData(RECIPE_KEYS.detail(updatedRecipe.slug), updatedRecipe)

      // Invalidate lists to reflect changes
      queryClient.invalidateQueries(RECIPE_KEYS.lists())
      queryClient.invalidateQueries(RECIPE_KEYS.featured())

      toast.success(`Recipe "${updatedRecipe.name}" updated successfully!`)
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to update recipe'
      toast.error(message)
    },
  })
}

// Delete recipe mutation
export function useDeleteRecipe() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => recipeApi.deleteRecipe(id),
    onSuccess: (_, deletedId) => {
      // Remove from all caches
      queryClient.removeQueries(RECIPE_KEYS.detail(deletedId))

      // Invalidate lists
      queryClient.invalidateQueries(RECIPE_KEYS.lists())
      queryClient.invalidateQueries(RECIPE_KEYS.featured())
      queryClient.invalidateQueries(RECIPE_KEYS.recent())

      toast.success('Recipe deleted successfully!')
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to delete recipe'
      toast.error(message)
    },
  })
}

// Upload recipe file mutation
export function useUploadRecipeFile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => recipeApi.uploadRecipeFile(file),
    onSuccess: (result) => {
      // Invalidate lists to show new recipe
      queryClient.invalidateQueries(RECIPE_KEYS.lists())
      queryClient.invalidateQueries(RECIPE_KEYS.recent())

      toast.success(`Recipe file "${result.filename}" uploaded successfully!`)

      if (result.conversion_note) {
        toast(result.conversion_note, { duration: 6000, icon: 'ℹ️' })
      }
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to upload recipe file'
      toast.error(message)
    },
  })
}