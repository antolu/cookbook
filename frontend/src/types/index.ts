// API Types
export interface Recipe {
  id: string;
  name: string;
  slug: string;
  description?: string;
  servings?: string;
  prep_time?: number;
  cook_time?: number;
  total_time?: number;
  temperature?: number;
  content?: string;
  difficulty?: string;
  cuisine?: string;
  category?: string;
  tags: string[];
  image_url?: string;
  notes: string[];
  tips: string[];
  is_public: boolean;
  is_featured: boolean;
  language: string;
  created_at: string;
  updated_at: string;
  published_at?: string;
}

export interface RecipeListItem {
  id: string;
  name: string;
  slug: string;
  description?: string;
  servings?: string;
  total_time?: number;
  difficulty?: string;
  cuisine?: string;
  category?: string;
  tags: string[];
  image_url?: string;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

export interface RecipeCreate {
  name: string;
  description?: string;
  servings?: string;
  prep_time?: number;
  cook_time?: number;
  temperature?: number;
  content?: string;
  difficulty?: string;
  cuisine?: string;
  category?: string;
  tags?: string[];
  image_url?: string;
  notes?: string[];
  tips?: string[];
  is_public?: boolean;
  is_featured?: boolean;
  language?: string;
}

export interface RecipeUpdate {
  name?: string;
  description?: string;
  servings?: string;
  prep_time?: number;
  cook_time?: number;
  temperature?: number;
  content?: string;
  difficulty?: string;
  cuisine?: string;
  category?: string;
  tags?: string[];
  image_url?: string;
  notes?: string[];
  tips?: string[];
  is_public?: boolean;
  is_featured?: boolean;
}

export interface RecipeSearchParams {
  q?: string;
  category?: string;
  cuisine?: string;
  difficulty?: string;
  tags?: string[];
  max_prep_time?: number;
  max_cook_time?: number;
  max_total_time?: number;
  is_featured?: boolean;
  limit?: number;
  offset?: number;
}

export interface RecipeSearchResponse {
  recipes: RecipeListItem[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface ApiError {
  detail: string;
}

// UI Types
export interface SearchFilters {
  query: string;
  category: string;
  cuisine: string;
  difficulty: string;
  tags: string[];
  maxPrepTime?: number;
  maxCookTime?: number;
  maxTotalTime?: number;
  featuredOnly: boolean;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
}

// Constants
export const DIFFICULTY_LEVELS = ['easy', 'medium', 'hard'] as const;
export const TIME_UNITS = ['minutes', 'hours'] as const;

export type DifficultyLevel = (typeof DIFFICULTY_LEVELS)[number];
export type TimeUnit = (typeof TIME_UNITS)[number];
