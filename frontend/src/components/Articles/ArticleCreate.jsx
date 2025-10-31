import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { createArticle } from '../../store/slices/articleSlice'
import ArticleForm from './ArticleForm'

function ArticleCreate() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (formData) => {
    setSaving(true)
    try {
      const result = await dispatch(createArticle(formData)).unwrap()
      navigate(`/articles/${result.id}/edit`)
    } catch (error) {
      console.error('Error creating article:', error)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Create Article</h1>
        <p className="text-gray-600 mt-1">Create a new article</p>
      </div>

      <ArticleForm
        initialData={{}}
        onSubmit={handleSubmit}
        saving={saving}
        submitLabel="Create Article"
      />
    </div>
  )
}

export default ArticleCreate

