import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchArticle, updateArticle } from '../../store/slices/articleSlice'
import ArticleForm from './ArticleForm'

function ArticleEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { currentArticle, loading } = useSelector((state) => state.articles)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    dispatch(fetchArticle(id))
  }, [dispatch, id])

  const handleSubmit = async (formData) => {
    setSaving(true)
    try {
      await dispatch(updateArticle({ id, data: formData })).unwrap()
      navigate('/articles')
    } catch (error) {
      console.error('Error updating article:', error)
    } finally {
      setSaving(false)
    }
  }

  if (loading || !currentArticle) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Edit Article</h1>
        <p className="text-gray-600 mt-1">Update article content and metadata</p>
        {currentArticle?.source_url && (
          <div className="mt-2 text-sm text-gray-500">
            Source: <a href={currentArticle.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {currentArticle.source_url}
            </a>
          </div>
        )}
      </div>

      <ArticleForm
        initialData={currentArticle}
        onSubmit={handleSubmit}
        saving={saving}
        submitLabel="Update Article"
      />
    </div>
  )
}

export default ArticleEdit

