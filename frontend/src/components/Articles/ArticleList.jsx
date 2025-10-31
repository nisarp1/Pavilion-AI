import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchArticles } from '../../store/slices/articleSlice'
import { format } from 'date-fns'
import { FiEdit, FiPlay, FiCheck, FiArchive, FiRefreshCw } from 'react-icons/fi'
import { generateArticle, publishArticle, archiveArticle } from '../../store/slices/articleSlice'

function ArticleList() {
  const dispatch = useDispatch()
  const { items, loading, pagination } = useSelector((state) => state.articles)
  const [statusFilter, setStatusFilter] = useState('')
  const [generatingArticles, setGeneratingArticles] = useState(new Set())

  useEffect(() => {
    dispatch(fetchArticles({ status: statusFilter }))
  }, [dispatch, statusFilter])

  const handleGenerate = async (articleId) => {
    setGeneratingArticles(prev => new Set(prev).add(articleId))
    try {
      const result = await dispatch(generateArticle(articleId))
      if (generateArticle.fulfilled.match(result)) {
        // Success - refresh the list to show updated article
        dispatch(fetchArticles({ status: statusFilter }))
        alert('Article generated successfully! The article body has been created using Gemini AI.')
      } else {
        alert('Error generating article: ' + (result.payload?.error || 'Unknown error'))
      }
    } catch (error) {
      alert('Error generating article: ' + error.message)
    } finally {
      setGeneratingArticles(prev => {
        const next = new Set(prev)
        next.delete(articleId)
        return next
      })
    }
  }

  const handlePublish = async (articleId) => {
    await dispatch(publishArticle(articleId))
    dispatch(fetchArticles({ status: statusFilter }))
  }

  const handleArchive = async (articleId) => {
    await dispatch(archiveArticle(articleId))
    dispatch(fetchArticles({ status: statusFilter }))
  }

  const getStatusBadge = (status) => {
    const badges = {
      fetched: 'bg-yellow-100 text-yellow-800',
      draft: 'bg-blue-100 text-blue-800',
      published: 'bg-green-100 text-green-800',
      archived: 'bg-gray-100 text-gray-800',
    }
    return (
      <span
        className={`px-2 py-1 text-xs font-semibold rounded-full ${badges[status] || badges.fetched}`}
      >
        {status}
      </span>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <FiRefreshCw className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-800">Articles</h1>
      </div>

      {/* Filters */}
      <div className="mb-6 flex gap-2">
        <button
          onClick={() => setStatusFilter('')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            statusFilter === ''
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setStatusFilter('fetched')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            statusFilter === 'fetched'
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          Fetched
        </button>
        <button
          onClick={() => setStatusFilter('draft')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            statusFilter === 'draft'
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          Draft
        </button>
        <button
          onClick={() => setStatusFilter('published')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            statusFilter === 'published'
              ? 'bg-primary-600 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100'
          }`}
        >
          Published
        </button>
      </div>

      {/* Articles Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Author
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                  No articles found
                </td>
              </tr>
            ) : (
              items.map((article) => (
                <tr key={article.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-start gap-3">
                      {article.featured_image_url && (
                        <img
                          src={article.featured_image_url}
                          alt={article.title}
                          className="w-16 h-16 object-cover rounded border border-gray-200 flex-shrink-0"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900">{article.title}</div>
                        {article.summary && (
                          <div className="text-sm text-gray-500 truncate max-w-md mt-1">
                            {article.summary.substring(0, 100)}...
                          </div>
                        )}
                        {article.source_url && (
                          <div className="text-xs text-gray-400 mt-1 truncate">
                            <a href={article.source_url} target="_blank" rel="noopener noreferrer" className="hover:text-blue-600">
                              Source →
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(article.status)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {article.author_name || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {format(new Date(article.created_at), 'MMM dd, yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center justify-end gap-2">
                      {article.status === 'fetched' && (
                        <button
                          onClick={() => handleGenerate(article.id)}
                          disabled={generatingArticles.has(article.id)}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors text-sm font-medium flex items-center gap-2"
                          title="Generate Article with Gemini AI"
                        >
                          {generatingArticles.has(article.id) ? (
                            <>
                              <FiRefreshCw className="animate-spin" size={16} />
                              Generating...
                            </>
                          ) : (
                            <>
                              <FiPlay size={16} />
                              Generate
                            </>
                          )}
                        </button>
                      )}
                      {(article.status === 'draft' || article.status === 'fetched') && (
                        <Link
                          to={`/articles/${article.id}/edit`}
                          className="text-primary-600 hover:text-primary-900 p-2 hover:bg-primary-50 rounded"
                          title="Edit"
                        >
                          <FiEdit size={18} />
                        </Link>
                      )}
                      {article.status === 'draft' && (
                        <button
                          onClick={() => handlePublish(article.id)}
                          className="text-green-600 hover:text-green-900 p-2 hover:bg-green-50 rounded"
                          title="Publish"
                        >
                          <FiCheck size={18} />
                        </button>
                      )}
                      {article.status !== 'archived' && (
                        <button
                          onClick={() => handleArchive(article.id)}
                          className="text-gray-600 hover:text-gray-900 p-2 hover:bg-gray-50 rounded"
                          title="Archive"
                        >
                          <FiArchive size={18} />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ArticleList

