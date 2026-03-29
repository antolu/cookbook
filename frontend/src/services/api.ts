import axios, { AxiosResponse } from 'axios';
import {
  Recipe,
  RecipeListItem,
  RecipeCreate,
  RecipeUpdate,
  RecipeSearchParams,
  RecipeSearchResponse,
} from '../types';
import config from '../config';

// Create axios instance
const api = axios.create({
  baseURL: config.apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  axiosConfig => {
    // In integrated mode, add JWT token from localStorage if available
    if (config.isIntegrated) {
      const token = localStorage.getItem('auth_token');
      if (token) {
        axiosConfig.headers.Authorization = `Bearer ${token}`;
      }
    }
    // In development mode, no auth required
    return axiosConfig;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // In integrated mode, redirect to login
      if (config.isIntegrated) {
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
      }
      // In development mode, just log the error
      else {
        console.warn('Authentication not available in development mode');
      }
    }
    return Promise.reject(error);
  }
);

// Recipe API functions
export const recipeApi = {
  // Get all recipes
  getRecipes: async (params?: {
    skip?: number;
    limit?: number;
    featured_only?: boolean;
  }): Promise<RecipeListItem[]> => {
    const response: AxiosResponse<RecipeListItem[]> = await api.get('/recipes', {
      params,
    });
    return response.data;
  },

  // Search recipes
  searchRecipes: async (params: RecipeSearchParams): Promise<RecipeSearchResponse> => {
    const response: AxiosResponse<RecipeSearchResponse> = await api.get('/recipes/search', {
      params,
    });
    return response.data;
  },

  // Get featured recipes
  getFeaturedRecipes: async (limit?: number): Promise<RecipeListItem[]> => {
    const response: AxiosResponse<RecipeListItem[]> = await api.get('/recipes/featured', {
      params: { limit },
    });
    return response.data;
  },

  // Get recent recipes
  getRecentRecipes: async (limit?: number): Promise<RecipeListItem[]> => {
    const response: AxiosResponse<RecipeListItem[]> = await api.get('/recipes/recent', {
      params: { limit },
    });
    return response.data;
  },

  // Get recipe by ID or slug
  getRecipe: async (identifier: string): Promise<Recipe> => {
    const response: AxiosResponse<Recipe> = await api.get(`/recipes/${identifier}`);
    return response.data;
  },

  // Create recipe
  createRecipe: async (recipe: RecipeCreate): Promise<Recipe> => {
    const response: AxiosResponse<Recipe> = await api.post('/recipes', recipe);
    return response.data;
  },

  // Update recipe
  updateRecipe: async (id: string, recipe: RecipeUpdate): Promise<Recipe> => {
    const response: AxiosResponse<Recipe> = await api.put(`/recipes/${id}`, recipe);
    return response.data;
  },

  // Delete recipe
  deleteRecipe: async (id: string): Promise<void> => {
    await api.delete(`/recipes/${id}`);
  },

  // Get categories
  getCategories: async (): Promise<string[]> => {
    const response: AxiosResponse<string[]> = await api.get('/recipes/categories');
    return response.data;
  },

  // Get cuisines
  getCuisines: async (): Promise<string[]> => {
    const response: AxiosResponse<string[]> = await api.get('/recipes/cuisines');
    return response.data;
  },

  // Get tags
  getTags: async (): Promise<string[]> => {
    const response: AxiosResponse<string[]> = await api.get('/recipes/tags');
    return response.data;
  },

  // Get recipes by category
  getRecipesByCategory: async (category: string, limit?: number): Promise<RecipeListItem[]> => {
    const response: AxiosResponse<RecipeListItem[]> = await api.get(
      `/recipes/category/${category}`,
      { params: { limit } }
    );
    return response.data;
  },

  // Upload recipe file
  uploadRecipeFile: async (file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/recipes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Export recipe
  exportRecipe: async (id: string, format: string): Promise<any> => {
    const response = await api.get(`/recipes/${id}/export/${format}`);
    return response.data;
  },

  // Get recipe stats (admin only)
  getRecipeStats: async (): Promise<any> => {
    const response = await api.get('/recipes/stats/summary');
    return response.data;
  },
};

export default api;
