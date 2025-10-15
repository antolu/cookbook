import React, { useState, useEffect } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { EditorView } from '@codemirror/view'
import { createEditorExtensions } from '../utils/editorExtensions'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

interface RecipeEditorProps {
  initialValue?: string
  onChange?: (value: string) => void
  onSave?: (value: string) => void
}

const DEFAULT_TEMPLATE = `---
name: ""
description: ""
servings: ""
prep_time: ""
cook_time: ""
difficulty: ""
cuisine: ""
category: ""
tags: []
notes: []
tips: []
public: true
featured: false
---

## Description



## Ingredients

-


## Instructions

1.


## Notes

-


## Tips

-
`

export const RecipeEditor: React.FC<RecipeEditorProps> = ({
  initialValue = DEFAULT_TEMPLATE,
  onChange,
  onSave,
}) => {
  const [value, setValue] = useState(initialValue)
  const [extensions, setExtensions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [validationErrors, setValidationErrors] = useState<string[]>([])

  // Load schema and autocomplete data
  useEffect(() => {
    const loadEditorData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [schemaRes, autocompleteRes] = await Promise.all([
          axios.get(`${API_BASE}/recipes/editor/schema`),
          axios.get(`${API_BASE}/recipes/editor/autocomplete`),
        ])

        const editorExtensions = createEditorExtensions(
          autocompleteRes.data,
          schemaRes.data
        )

        setExtensions(editorExtensions)
      } catch (err) {
        console.error('Failed to load editor data:', err)
        setError('Failed to load editor configuration')
      } finally {
        setLoading(false)
      }
    }

    loadEditorData()
  }, [])

  // Validate on change (debounced)
  useEffect(() => {
    const timeoutId = setTimeout(async () => {
      if (!value) return

      try {
        const response = await axios.post(`${API_BASE}/recipes/validate`, value, {
          headers: { 'Content-Type': 'text/plain' }
        })

        setValidationErrors(response.data.errors || [])
      } catch (err) {
        console.error('Validation error:', err)
      }
    }, 500)

    return () => clearTimeout(timeoutId)
  }, [value])

  const handleChange = (newValue: string) => {
    setValue(newValue)
    onChange?.(newValue)
  }

  const handleSave = () => {
    onSave?.(value)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="spinner h-12 w-12"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-md p-4">
        <p className="text-red-800">{error}</p>
      </div>
    )
  }

  return (
    <div className="recipe-editor">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Recipe Editor</h2>
          <p className="text-sm text-gray-600">
            Edit recipe in Markdown format with YAML frontmatter
          </p>
        </div>
        {onSave && (
          <button
            onClick={handleSave}
            className="btn btn-primary"
            disabled={validationErrors.length > 0}
          >
            Save Recipe
          </button>
        )}
      </div>

      {validationErrors.length > 0 && (
        <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <h3 className="text-sm font-semibold text-yellow-800 mb-2">
            Validation Errors:
          </h3>
          <ul className="list-disc list-inside text-sm text-yellow-700">
            {validationErrors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="border border-gray-300 rounded-md overflow-hidden">
        <CodeMirror
          value={value}
          height="600px"
          extensions={extensions}
          onChange={handleChange}
          theme="light"
          basicSetup={{
            lineNumbers: true,
            highlightActiveLineGutter: true,
            highlightSpecialChars: true,
            foldGutter: true,
            drawSelection: true,
            dropCursor: true,
            allowMultipleSelections: true,
            indentOnInput: true,
            bracketMatching: true,
            closeBrackets: true,
            autocompletion: true,
            rectangularSelection: true,
            crosshairCursor: true,
            highlightActiveLine: true,
            highlightSelectionMatches: true,
            closeBracketsKeymap: true,
            searchKeymap: true,
            foldKeymap: true,
            completionKeymap: true,
            lintKeymap: true,
          }}
        />
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <p><strong>Tip:</strong> Press <kbd className="px-2 py-1 bg-gray-100 border border-gray-300 rounded">Ctrl+Space</kbd> for autocomplete</p>
      </div>
    </div>
  )
}
