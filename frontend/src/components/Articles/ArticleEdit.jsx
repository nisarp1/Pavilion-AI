import { useEffect, useState, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { fetchArticle, updateArticle, publishArticle } from '../../store/slices/articleSlice'
import { fetchCategoryTree } from '../../store/slices/categorySlice'
import { FiImage, FiUser, FiLink, FiTag, FiExternalLink } from 'react-icons/fi'
import ReactQuill from 'react-quill'
import 'react-quill/dist/quill.snow.css'
import Quill from 'quill'
import { convertUrlToEmbed } from '../../utils/embedUtils'

function ArticleEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { currentArticle, loading } = useSelector((state) => state.articles)
  const { categoryTree } = useSelector((state) => state.categories)
  const quillRef = useRef(null)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    summary: '',
    body: '',
    status: 'draft',
    category: 'reliable_sources',
    category_ids: [],
    author: '',
    meta_title: '',
    meta_description: '',
    og_title: '',
    og_description: '',
  })
  useEffect(() => {
    dispatch(fetchArticle(id))
    dispatch(fetchCategoryTree())
  }, [dispatch, id])

  useEffect(() => {
    if (currentArticle) {
      setFormData({
        title: currentArticle.title || '',
        slug: currentArticle.slug || '',
        summary: currentArticle.summary || '',
        body: currentArticle.body || '',
        status: currentArticle.status || 'draft',
        category: currentArticle.category || 'reliable_sources',
        category_ids: currentArticle.categories?.map(cat => cat.id) || [],
        author: currentArticle.author || '',
        meta_title: currentArticle.meta_title || '',
        meta_description: currentArticle.meta_description || '',
        og_title: currentArticle.og_title || '',
        og_description: currentArticle.og_description || '',
      })
    }
  }, [currentArticle])

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

  const handleStatusChange = (newStatus) => {
    setFormData((prev) => ({ ...prev, status: newStatus }))
  }

  const handleSave = async (status) => {
    setSaving(true)
    try {
      const dataToSave = { ...formData, status }
      await dispatch(updateArticle({ id, data: dataToSave })).unwrap()
      
      if (status === 'published') {
        await dispatch(publishArticle(id))
      }
      
      navigate('/articles')
    } catch (error) {
      console.error('Error saving article:', error)
      alert('Error saving article: ' + (error.message || 'Unknown error'))
    } finally {
      setSaving(false)
    }
  }

  const handlePublish = () => {
    handleSave('published')
  }

  const handleSaveDraft = () => {
    handleSave('draft')
  }

  if (loading || !currentArticle) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const categoryOptions = [
    { value: 'reliable_sources', label: 'Reliable Sources' },
    { value: 'trends', label: 'Trends' },
    { value: 'subscriptions', label: 'Subscriptions' },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header with Publish/Draft buttons */}
      <div className="mb-6 flex justify-between items-center border-b border-gray-200 pb-4">
    <div>
        <h1 className="text-3xl font-bold text-gray-800">Edit Article</h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleSaveDraft}
            disabled={saving}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              formData.status === 'draft'
                ? 'bg-gray-200 text-gray-700'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {saving ? 'Saving...' : 'Save Draft'}
          </button>
          <button
            onClick={handlePublish}
            disabled={saving}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm font-medium"
          >
            {saving ? 'Publishing...' : 'Publish'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Title */}
          <div className="bg-white rounded-lg shadow p-6">
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
              className="w-full px-4 py-3 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Enter article title"
            />
          </div>

          {/* Body Editor */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Content *</label>
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
                    matchVisual: false,
                    matchers: []
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

          {/* Summary */}
          <div className="bg-white rounded-lg shadow p-6">
            <label htmlFor="summary" className="block text-sm font-medium text-gray-700 mb-2">
              Excerpt
            </label>
            <textarea
              id="summary"
              name="summary"
              value={formData.summary}
              onChange={handleChange}
              rows={4}
              lang="en"
              autoComplete="off"
              spellCheck="true"
              style={{ imeMode: 'auto' }}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Write an excerpt..."
            />
          </div>

          {/* SEO Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">SEO Metadata</h3>
            <div className="space-y-4">
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
                <label htmlFor="meta_description" className="block text-sm font-medium text-gray-700 mb-2">
                  Meta Description
                </label>
                <textarea
                  id="meta_description"
                  name="meta_description"
                  value={formData.meta_description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
              <div>
                <label htmlFor="og_title" className="block text-sm font-medium text-gray-700 mb-2">
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
                <label htmlFor="og_description" className="block text-sm font-medium text-gray-700 mb-2">
                  OG Description
                </label>
                <textarea
                  id="og_description"
                  name="og_description"
                  value={formData.og_description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          {/* Publish/Draft Status */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Status</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="status"
                  value="draft"
                  checked={formData.status === 'draft'}
                  onChange={() => handleStatusChange('draft')}
                  className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Draft</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="status"
                  value="published"
                  checked={formData.status === 'published'}
                  onChange={() => handleStatusChange('published')}
                  className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                />
                <span className="ml-2 text-sm text-gray-700">Published</span>
              </label>
            </div>
          </div>

          {/* Featured Image */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
              <FiImage size={16} />
              Featured Image
            </h3>
            {currentArticle.featured_image_url ? (
              <div className="space-y-3">
                <img
                  src={currentArticle.featured_image_url}
                  alt="Featured"
                  className="w-full h-48 object-cover rounded-lg border border-gray-300"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <button
                  type="button"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg text-sm text-gray-700 hover:bg-gray-50"
                >
                  Change Image
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="w-full px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-600 hover:border-primary-500 hover:text-primary-600"
              >
                Set featured image
              </button>
            )}
          </div>

          {/* Author */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
              <FiUser size={16} />
              Author
            </h3>
            <input
              type="text"
              name="author"
              value={currentArticle.author_name || 'admin'}
              readOnly
              className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm text-gray-600"
            />
            <p className="mt-2 text-xs text-gray-500">Author cannot be changed</p>
          </div>

          {/* Slug */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
              <FiLink size={16} />
              Slug
            </h3>
            <input
              type="text"
              name="slug"
              value={formData.slug}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
              placeholder="article-slug"
            />
            <p className="mt-2 text-xs text-gray-500">The "slug" is the URL-friendly version of the name.</p>
          </div>

          {/* Reference Link */}
          {currentArticle.source_url && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
                <FiExternalLink size={16} />
                Reference Link
              </h3>
              <div className="space-y-2">
                <div className="flex items-center gap-2 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                  <a
                    href={currentArticle.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 hover:underline flex-1 truncate"
                  >
              {currentArticle.source_url}
            </a>
                  <FiExternalLink size={14} className="text-gray-400 flex-shrink-0" />
                </div>
                <p className="text-xs text-gray-500">Original source URL for this article.</p>
              </div>
            </div>
          )}

          {/* Source Category (reliable_sources, trends, subscriptions) */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
              <FiTag size={16} />
              Source
            </h3>
            <div className="space-y-2">
              {categoryOptions.map((option) => (
                <label key={option.value} className="flex items-center">
                  <input
                    type="radio"
                    name="category"
                    value={option.value}
                    checked={formData.category === option.value}
                    onChange={handleChange}
                    className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">{option.label}</span>
                </label>
              ))}
            </div>
            <p className="mt-3 text-xs text-gray-500">Article source type</p>
          </div>

          {/* Content Categories (Cricket, Football, etc.) */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide flex items-center gap-2">
              <FiTag size={16} />
              Content Categories
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {categoryTree.length === 0 ? (
                <p className="text-sm text-gray-500">
                  No categories available.{' '}
                  <Link to="/categories" className="text-blue-600 hover:underline">
                    Create categories
                  </Link>
                </p>
              ) : (
                categoryTree.map((parentCategory) => (
                  <div key={parentCategory.id} className="space-y-1">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.category_ids.includes(parentCategory.id)}
                        onChange={(e) => {
                          const newIds = e.target.checked
                            ? [...formData.category_ids, parentCategory.id]
                            : formData.category_ids.filter(id => id !== parentCategory.id)
                          setFormData({ ...formData, category_ids: newIds })
                        }}
                        className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="ml-2 text-sm font-medium text-gray-900">
                        {parentCategory.name}
                      </span>
                    </label>
                    {parentCategory.children && parentCategory.children.length > 0 && (
                      <div className="ml-6 space-y-1">
                        {parentCategory.children.map((childCategory) => (
                          <label key={childCategory.id} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={formData.category_ids.includes(childCategory.id)}
                              onChange={(e) => {
                                const newIds = e.target.checked
                                  ? [...formData.category_ids, childCategory.id]
                                  : formData.category_ids.filter(id => id !== childCategory.id)
                                setFormData({ ...formData, category_ids: newIds })
                              }}
                              className="w-4 h-4 text-primary-600 focus:ring-primary-500"
                            />
                            <span className="ml-2 text-sm text-gray-700">
                              {childCategory.name}
                            </span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
            <p className="mt-3 text-xs text-gray-500">
              Select content categories (Cricket, Football, etc.)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ArticleEdit
