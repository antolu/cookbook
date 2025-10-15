import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { RecipeEditor } from '../components/RecipeEditor'
import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const EditorPage: React.FC = () => {
  const navigate = useNavigate()
  const [saving, setSaving] = useState(false)

  const handleSave = async (markdownContent: string) => {
    try {
      setSaving(true)

      // Create a Blob and File to upload
      const blob = new Blob([markdownContent], { type: 'text/markdown' })
      const file = new File([blob], 'recipe.md', { type: 'text/markdown' })

      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(`${API_BASE}/recipes/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast.success(`Recipe "${response.data.recipe_name}" created successfully!`)

      // Navigate to the recipe detail page
      setTimeout(() => {
        navigate(`/recipes/${response.data.recipe_slug}`)
      }, 1000)
    } catch (error: any) {
      console.error('Failed to save recipe:', error)
      const errorMessage = error.response?.data?.detail || 'Failed to save recipe'
      toast.error(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Create New Recipe</h1>
        <p className="text-gray-600 mt-2">
          Write your recipe in Markdown format with YAML frontmatter. Use autocomplete for field suggestions.
        </p>
      </div>

      {saving && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-4">
            <div className="spinner h-8 w-8"></div>
            <span className="text-lg font-medium">Saving recipe...</span>
          </div>
        </div>
      )}

      <RecipeEditor onSave={handleSave} />
    </div>
  )
}
