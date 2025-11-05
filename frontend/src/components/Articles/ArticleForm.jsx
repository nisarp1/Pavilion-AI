import { useState, useEffect, useRef } from 'react'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'
import Quill from 'quill'
import { convertUrlToEmbed } from '../../utils/embedUtils'

function ArticleForm({ initialData, onSubmit, saving, submitLabel }) {
  const quillRef = useRef(null)
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    summary: initialData.summary || '',
    body: initialData.body || '',
    meta_title: initialData.meta_title || '',
    meta_description: initialData.meta_description || '',
    og_title: initialData.og_title || '',
    og_description: initialData.og_description || '',
  })

  useEffect(() => {
    if (initialData) {
      setFormData({
        title: initialData.title || '',
        summary: initialData.summary || '',
        body: initialData.body || '',
        meta_title: initialData.meta_title || '',
        meta_description: initialData.meta_description || '',
        og_title: initialData.og_title || '',
        og_description: initialData.og_description || '',
      })
    }
  }, [initialData])

  // Simple paste handler for embeds
  useEffect(() => {
    if (!quillRef.current) return
    
    const quill = quillRef.current.getEditor()
    if (!quill || !quill.root) return
    
    const handlePaste = (e) => {
      const text = e.clipboardData?.getData('text/plain')
      if (text && /youtube\.com|youtu\.be|twitter\.com|x\.com|instagram\.com|facebook\.com/i.test(text.trim())) {
        e.preventDefault()
        const url = text.trim()
        const embedHtml = convertUrlToEmbed(url)
        if (embedHtml) {
          const range = quill.getSelection(true) || { index: quill.getLength(), length: 0 }
          
          // Insert newline and embed directly into DOM
          const editorRoot = quill.root
          const embedDiv = document.createElement('div')
          embedDiv.className = 'ql-video-embed'
          embedDiv.setAttribute('contenteditable', 'false')
          embedDiv.innerHTML = embedHtml
          
          // Insert before the last child or append
          const lastChild = editorRoot.lastElementChild
          if (lastChild) {
            lastChild.insertAdjacentElement('afterend', embedDiv)
          } else {
            editorRoot.appendChild(embedDiv)
          }
          
          // Add spacing paragraph
          const spacer = document.createElement('p')
          spacer.innerHTML = '<br>'
          embedDiv.insertAdjacentElement('afterend', spacer)
          
          // Update Quill and move cursor
          setTimeout(() => {
            quill.update('user')
            const newLength = quill.getLength()
            quill.setSelection(newLength, 'silent')
          }, 10)
        }
      }
    }
    
    quill.root.addEventListener('paste', handlePaste, true)
    return () => quill.root.removeEventListener('paste', handlePaste, true)
  }, [formData.body])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleBodyChange = (content) => {
    setFormData((prev) => ({ ...prev, body: content }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
      {/* Source URL & Featured Image Info */}
      {(initialData.source_url || initialData.featured_image_url) && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
          <h3 className="text-sm font-semibold text-blue-900">Article Information</h3>
          
          {initialData.source_url && (
            <div>
              <label className="block text-xs font-medium text-blue-700 mb-1">
                Source URL
              </label>
              <div className="flex items-center gap-2">
                <a
                  href={initialData.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 truncate"
                >
                  {initialData.source_url}
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          )}

          {initialData.featured_image_url && (
            <div>
              <label className="block text-xs font-medium text-blue-700 mb-1">
                Featured Image
              </label>
              <div className="flex items-center gap-3">
                <img
                  src={initialData.featured_image_url}
                  alt="Featured"
                  className="w-32 h-32 object-cover rounded-lg border border-gray-300"
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
                <div className="flex-1">
                  <a
                    href={initialData.featured_image_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-600 hover:text-blue-800 hover:underline"
                  >
                    View Full Size
                  </a>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Title */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
          Title *
        </label>
        <input
          type="text"
          id="title"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
          lang="en"
          autoComplete="off"
          spellCheck="true"
          style={{ imeMode: 'auto' }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Summary */}
      <div>
        <label htmlFor="summary" className="block text-sm font-medium text-gray-700 mb-2">
          Summary
        </label>
        <textarea
          id="summary"
          name="summary"
          value={formData.summary}
          onChange={handleChange}
          rows={3}
          lang="en"
          autoComplete="off"
          spellCheck="true"
          style={{ imeMode: 'auto' }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
      </div>

      {/* Body */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Body *</label>
        <div className="border border-gray-300 rounded-lg">
          <ReactQuill
              ref={quillRef}
              theme="snow"
              value={formData.body}
              onChange={handleBodyChange}
            modules={{
              toolbar: [
                [{ 'header': [1, 2, 3, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                [{ 'align': [] }],
                ['link', 'image'],
                ['clean'],
                ['code-block']
              ],
              clipboard: {
                matchVisual: false
              }
            }}
              formats={[
                'header',
                'bold', 'italic', 'underline', 'strike',
                'color', 'background',
                'list', 'bullet',
                'align',
                'link', 'image',
                'code-block'
              ]}
              style={{ height: '400px', marginBottom: '50px' }}
              placeholder="Write your article content here... (Paste YouTube or social media links to auto-embed)"
              className="text-sm"
            />
        </div>
      </div>

      {/* SEO Section */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">SEO Metadata</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="meta_title" className="block text-sm font-medium text-gray-700 mb-2">
              Meta Title
            </label>
            <input
              type="text"
              id="meta_title"
              name="meta_title"
              value={formData.meta_title}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label
              htmlFor="og_title"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              OG Title
            </label>
            <input
              type="text"
              id="og_title"
              name="og_title"
              value={formData.og_title}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label
              htmlFor="meta_description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Meta Description
            </label>
            <textarea
              id="meta_description"
              name="meta_description"
              value={formData.meta_description}
              onChange={handleChange}
              rows={2}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <div>
            <label
              htmlFor="og_description"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              OG Description
            </label>
            <textarea
              id="og_description"
              name="og_description"
              value={formData.og_description}
              onChange={handleChange}
              rows={2}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Submit Buttons */}
      <div className="flex justify-end gap-4 pt-6 border-t border-gray-200">
        <button
          type="button"
          onClick={() => window.history.back()}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={saving || !formData.title || !formData.body}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {saving ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  )
}

export default ArticleForm

