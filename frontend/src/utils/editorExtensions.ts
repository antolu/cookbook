import { Extension } from '@codemirror/state'
import { EditorView } from '@codemirror/view'
import { yaml } from '@codemirror/lang-yaml'
import { markdown } from '@codemirror/lang-markdown'
import { autocompletion, CompletionContext, CompletionResult } from '@codemirror/autocomplete'
import { linter, Diagnostic } from '@codemirror/lint'
import Ajv from 'ajv'
import jsYaml from 'js-yaml'

interface AutocompleteData {
  cuisines: string[]
  categories: string[]
  tags: string[]
  difficulty: string[]
}

interface RecipeSchema {
  schema: Record<string, unknown>
  field_descriptions: Record<string, string>
}

// Parse frontmatter from markdown
function parseFrontmatter(doc: string): { frontmatter: string; content: string; frontmatterEnd: number } {
  const lines = doc.split('\n')
  if (lines[0] !== '---') {
    return { frontmatter: '', content: doc, frontmatterEnd: 0 }
  }

  let endIndex = -1
  for (let i = 1; i < lines.length; i++) {
    if (lines[i] === '---') {
      endIndex = i
      break
    }
  }

  if (endIndex === -1) {
    return { frontmatter: '', content: doc, frontmatterEnd: 0 }
  }

  const frontmatter = lines.slice(1, endIndex).join('\n')
  const content = lines.slice(endIndex + 1).join('\n')
  const frontmatterEnd = lines.slice(0, endIndex + 1).join('\n').length

  return { frontmatter, content, frontmatterEnd }
}

// Create autocomplete extension
export function createAutocomplete(
  autocompleteData: AutocompleteData,
  fieldDescriptions: Record<string, string>
): Extension {
  const fieldCompletions = Object.keys(fieldDescriptions).map(field => ({
    label: field,
    type: 'keyword',
    info: fieldDescriptions[field],
    apply: `${field}: `
  }))

  return autocompletion({
    override: [
      (context: CompletionContext): CompletionResult | null => {
        const { state, pos } = context
        const doc = state.doc.toString()
        const { frontmatter, frontmatterEnd } = parseFrontmatter(doc)

        // Only autocomplete in frontmatter
        if (pos > frontmatterEnd) {
          return null
        }

        const line = state.doc.lineAt(pos)
        const lineText = line.text
        const beforeCursor = lineText.slice(0, pos - line.from)

        // Autocomplete field names at start of line
        if (/^\s*[a-z_]*$/.test(beforeCursor)) {
          return {
            from: line.from + beforeCursor.search(/[a-z_]*$/),
            options: fieldCompletions,
          }
        }

        // Autocomplete values after field name
        const fieldMatch = lineText.match(/^(\s*)([a-z_]+):\s*(.*)$/)
        if (fieldMatch) {
          const [, , fieldName, valueStart] = fieldMatch
          const cursorInValue = pos > line.from + fieldMatch[1].length + fieldMatch[2].length + 1

          if (cursorInValue) {
            // Provide value completions based on field
            switch (fieldName) {
              case 'difficulty':
                return {
                  from: line.from + beforeCursor.search(/\S*$/),
                  options: autocompleteData.difficulty.map(val => ({
                    label: val,
                    type: 'constant',
                  }))
                }
              case 'cuisine':
                return {
                  from: line.from + beforeCursor.search(/\S*$/),
                  options: autocompleteData.cuisines.map(val => ({
                    label: val,
                    type: 'text',
                  }))
                }
              case 'category':
                return {
                  from: line.from + beforeCursor.search(/\S*$/),
                  options: autocompleteData.categories.map(val => ({
                    label: val,
                    type: 'text',
                  }))
                }
              case 'tags':
                // Autocomplete individual tag values in array
                if (valueStart.includes('[')) {
                  return {
                    from: line.from + beforeCursor.search(/\S*$/),
                    options: autocompleteData.tags.map(val => ({
                      label: `"${val}"`,
                      type: 'text',
                    }))
                  }
                }
                break
            }
          }
        }

        return null
      }
    ]
  })
}

// Create validation extension
export function createValidator(schema: Record<string, unknown>): Extension {
  const ajv = new Ajv({ allErrors: true })
  const validate = ajv.compile(schema)

  return linter((view: EditorView): Diagnostic[] => {
    const doc = view.state.doc.toString()
    const { frontmatter, frontmatterEnd } = parseFrontmatter(doc)

    if (!frontmatter) {
      return []
    }

    const diagnostics: Diagnostic[] = []

    // Parse YAML
    let parsed: unknown
    try {
      parsed = jsYaml.load(frontmatter)
    } catch (error) {
      const err = error as { mark?: { line: number; column: number }; message?: string }
      if (err.mark) {
        const line = view.state.doc.line(err.mark.line + 2) // +2 for opening ---
        diagnostics.push({
          from: line.from,
          to: line.to,
          severity: 'error',
          message: `YAML Error: ${err.message || 'Invalid YAML syntax'}`,
        })
      }
      return diagnostics
    }

    // Validate against schema
    const valid = validate(parsed)
    if (!valid && validate.errors) {
      for (const error of validate.errors) {
        const fieldPath = error.instancePath.slice(1) || error.params.missingProperty
        const fieldName = fieldPath.split('/').pop() || fieldPath

        // Find the line with this field
        const lines = frontmatter.split('\n')
        let lineIndex = -1
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].startsWith(`${fieldName}:`)) {
            lineIndex = i
            break
          }
        }

        if (lineIndex === -1 && error.keyword === 'required') {
          // Required field missing - mark at end of frontmatter
          diagnostics.push({
            from: frontmatterEnd - 5,
            to: frontmatterEnd - 4,
            severity: 'error',
            message: `Missing required field: ${fieldName}`,
          })
        } else if (lineIndex >= 0) {
          const line = view.state.doc.line(lineIndex + 2) // +2 for opening ---
          diagnostics.push({
            from: line.from,
            to: line.to,
            severity: 'error',
            message: error.message || 'Validation error',
          })
        }
      }
    }

    return diagnostics
  })
}

// Create hybrid language extension (YAML frontmatter + Markdown content)
export function createHybridLanguage(): Extension {
  return EditorView.updateListener.of(update => {
    if (update.docChanged) {
      const doc = update.state.doc.toString()
      const { frontmatterEnd } = parseFrontmatter(doc)

      // TODO: Apply YAML highlighting to frontmatter region
      // and Markdown to rest - this requires custom parser
      // For now, we use markdown() which handles frontmatter reasonably well
    }
  })
}

// Combine all extensions
export function createEditorExtensions(
  autocompleteData: AutocompleteData,
  recipeSchema: RecipeSchema
): Extension[] {
  return [
    markdown(),
    yaml(),
    createAutocomplete(autocompleteData, recipeSchema.field_descriptions),
    createValidator(recipeSchema.schema),
    createHybridLanguage(),
    EditorView.lineWrapping,
  ]
}
