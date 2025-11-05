import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchArticles, fetchTrends, fetchAllFeeds, generateArticle, publishArticle, archiveArticle, updateArticle } from '../../store/slices/articleSlice'
import { format } from 'date-fns'
import { FiEdit, FiPlay, FiCheck, FiArchive, FiRefreshCw, FiMoreVertical, FiEye, FiTrash2, FiClock, FiExternalLink } from 'react-icons/fi'
import GoogleTrendsWidget from './GoogleTrendsWidget'

function ArticleList() {
  const dispatch = useDispatch()
  const { items, loading, pagination } = useSelector((state) => state.articles)
  const [activeTab, setActiveTab] = useState('all')
  const [generatingArticles, setGeneratingArticles] = useState(new Set())
  const [refreshing, setRefreshing] = useState(false)
  const [selectedArticles, setSelectedArticles] = useState(new Set())
  const [showQuickActions, setShowQuickActions] = useState(null)

  useEffect(() => {
    if (activeTab === 'all') {
      dispatch(fetchArticles({}))
    } else if (activeTab === 'reliable_sources' || activeTab === 'trends' || activeTab === 'subscriptions') {
      dispatch(fetchArticles({ category: activeTab }))
    } else {
      dispatch(fetchArticles({ status: activeTab }))
    }
  }, [dispatch, activeTab])

  // Auto-refresh for Reliable Sources and Trends tabs every 5 minutes
  useEffect(() => {
    if (activeTab === 'reliable_sources' || activeTab === 'trends') {
      const intervalId = setInterval(() => {
        dispatch(fetchArticles({ category: activeTab }))
      }, 5 * 60 * 1000) // 5 minutes

      return () => clearInterval(intervalId)
    }
  }, [dispatch, activeTab])

  const handleRefresh = async (e) => {
    e?.preventDefault()
    e?.stopPropagation()
    
    setRefreshing(true)
    try {
      // If on reliable_sources or trends tab, fetch new feeds first
      if (activeTab === 'reliable_sources') {
        await dispatch(fetchAllFeeds())
        // Wait a moment for feeds to process, then refresh articles
        await new Promise(resolve => setTimeout(resolve, 1000))
        await dispatch(fetchArticles({ category: 'reliable_sources' }))
      } else if (activeTab === 'trends') {
        await dispatch(fetchTrends())
        // Wait a moment for trends to process, then refresh articles
        await new Promise(resolve => setTimeout(resolve, 1000))
        await dispatch(fetchArticles({ category: 'trends' }))
      } else if (activeTab === 'all') {
        await dispatch(fetchArticles({}))
      } else if (activeTab === 'subscriptions') {
        await dispatch(fetchArticles({ category: 'subscriptions' }))
      } else {
        // For status tabs (draft, published, fetched, archived)
        await dispatch(fetchArticles({ status: activeTab }))
      }
    } catch (error) {
      console.error('Refresh error:', error)
      alert('Error refreshing articles: ' + (error.message || 'Unknown error'))
    } finally {
      setRefreshing(false)
    }
  }

  const handleGenerate = async (articleId) => {
    setGeneratingArticles(prev => new Set(prev).add(articleId))
    try {
      const result = await dispatch(generateArticle(articleId))
      if (generateArticle.fulfilled.match(result)) {
        // Success - refresh the list to show updated article
        // Note: Article status changes from 'fetched' to 'draft' after generation
        // So if viewing 'fetched' tab, article will move to 'draft' tab
        if (activeTab === 'all') {
          dispatch(fetchArticles({}))
        } else if (activeTab === 'reliable_sources' || activeTab === 'trends' || activeTab === 'subscriptions') {
          dispatch(fetchArticles({ category: activeTab }))
        } else {
          dispatch(fetchArticles({ status: activeTab }))
        }
        alert('Article generated successfully! The article body has been created using Gemini AI.')
      } else {
        alert('Error generating article: ' + (result.payload?.error || result.payload?.message || 'Unknown error'))
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
    refreshList()
  }

  const handleArchive = async (articleId) => {
    await dispatch(archiveArticle(articleId))
    refreshList()
  }

  const handleMoveToDraft = async (articleId) => {
    await dispatch(updateArticle({ id: articleId, data: { status: 'draft' } }))
    refreshList()
  }

  const refreshList = () => {
    if (activeTab === 'all') {
      dispatch(fetchArticles({}))
    } else if (activeTab === 'reliable_sources' || activeTab === 'trends' || activeTab === 'subscriptions') {
      dispatch(fetchArticles({ category: activeTab }))
    } else {
      dispatch(fetchArticles({ status: activeTab }))
    }
  }

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedArticles(new Set(items.map(article => article.id)))
    } else {
      setSelectedArticles(new Set())
    }
  }

  const handleSelectArticle = (articleId) => {
    setSelectedArticles(prev => {
      const next = new Set(prev)
      if (next.has(articleId)) {
        next.delete(articleId)
      } else {
        next.add(articleId)
      }
      return next
    })
  }

  const getCategoryLabel = (category) => {
    const labels = {
      reliable_sources: 'Reliable Sources',
      trends: 'Trends',
      subscriptions: 'Subscriptions',
    }
    return labels[category] || category
  }

  const getStatusBadge = (status) => {
    const badges = {
      fetched: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      draft: 'bg-blue-100 text-blue-800 border-blue-200',
      published: 'bg-green-100 text-green-800 border-green-200',
      archived: 'bg-gray-100 text-gray-800 border-gray-200',
    }
    return (
      <span
        className={`px-2 py-1 text-xs font-medium rounded border ${badges[status] || badges.fetched}`}
      >
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const getTimeDisplay = (article) => {
    if (article.published_at) {
      return {
        label: 'Published',
        date: format(new Date(article.published_at), 'MMM dd, yyyy HH:mm'),
        relative: format(new Date(article.published_at), 'MMM dd, yyyy')
      }
    } else if (article.status === 'draft') {
      return {
        label: 'Draft',
        date: format(new Date(article.updated_at), 'MMM dd, yyyy HH:mm'),
        relative: format(new Date(article.updated_at), 'MMM dd, yyyy')
      }
    } else {
      return {
        label: 'Created',
        date: format(new Date(article.created_at), 'MMM dd, yyyy HH:mm'),
        relative: format(new Date(article.created_at), 'MMM dd, yyyy')
      }
    }
  }

  if (loading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <FiRefreshCw className="animate-spin text-primary-600" size={32} />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">Posts</h1>
        </div>
        <div className="flex gap-3">
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 ${
              refreshing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <FiRefreshCw className={refreshing ? 'animate-spin' : ''} size={16} />
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <Link
            to="/articles/create"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
          >
            Add New
          </Link>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-8 -mb-px">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'all'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setActiveTab('published')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'published'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Published
          </button>
          <button
            onClick={() => setActiveTab('draft')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'draft'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Draft
          </button>
          <button
            onClick={() => setActiveTab('fetched')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'fetched'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Fetched
          </button>
          <button
            onClick={() => setActiveTab('archived')}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'archived'
                ? 'border-primary-600 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Trash
          </button>
          <div className="ml-auto flex gap-2">
            <button
              onClick={() => setActiveTab('reliable_sources')}
              className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'reliable_sources'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Reliable Sources
            </button>
            <button
              onClick={() => setActiveTab('trends')}
              className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'trends'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Trends
            </button>
            <button
              onClick={() => setActiveTab('subscriptions')}
              className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
                activeTab === 'subscriptions'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Subscriptions
            </button>
          </div>
        </div>
      </div>

      {/* Google Trends Widget - Show only on Trends tab */}
      {activeTab === 'trends' && <GoogleTrendsWidget />}

      {/* Bulk Actions Bar */}
      {selectedArticles.size > 0 && (
        <div className="mb-4 bg-gray-50 border border-gray-200 rounded-lg p-3 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            {selectedArticles.size} item{selectedArticles.size > 1 ? 's' : ''} selected
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50">
              Edit
            </button>
            <button className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50">
              Move to Draft
            </button>
            <button className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50">
              Publish
            </button>
            <button className="px-3 py-1.5 text-sm bg-white border border-red-300 text-red-600 rounded hover:bg-red-50">
              Move to Trash
            </button>
          </div>
        </div>
      )}

      {/* Articles Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={selectedArticles.size === items.length && items.length > 0}
                  onChange={handleSelectAll}
                  className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Author
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {items.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                  No articles found
                </td>
              </tr>
            ) : (
              items.map((article) => {
                const timeInfo = getTimeDisplay(article)
                return (
                  <tr key={article.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedArticles.has(article.id)}
                        onChange={() => handleSelectArticle(article.id)}
                        className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-start gap-3">
                        {article.featured_image_url && (
                          <img
                            src={article.featured_image_url}
                            alt={article.title}
                            className="w-12 h-12 object-cover rounded border border-gray-200 flex-shrink-0"
                            onError={(e) => {
                              e.target.style.display = 'none'
                            }}
                          />
                        )}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Link
                              to={`/articles/${article.id}/edit`}
                              className="font-medium text-gray-900 hover:text-primary-600"
                            >
                              {article.title || '(No title)'}
                            </Link>
                            {getStatusBadge(article.status)}
                          </div>
                          {article.source_url && (
                            <div className="text-xs text-gray-400 mt-1">
                              <a
                                href={article.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="hover:text-blue-600 flex items-center gap-1"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <FiExternalLink size={10} />
                                {article.source_url.length > 60 
                                  ? article.source_url.substring(0, 60) + '...' 
                                  : article.source_url}
                              </a>
                            </div>
                          )}
                          <div className="flex items-center gap-3 text-xs text-gray-500">
                            <Link
                              to={`/articles/${article.id}/edit`}
                              className="hover:text-primary-600"
                            >
                              Edit
                            </Link>
                            {article.status === 'published' && (
                              <>
                                <span>|</span>
                                <a
                                  href="#"
                                  className="hover:text-primary-600"
                                  onClick={(e) => {
                                    e.preventDefault()
                                    // TODO: Open preview
                                  }}
                                >
                                  View
                                </a>
                              </>
                            )}
                            {article.source_url && (
                              <>
                                <span>|</span>
                                <a
                                  href={article.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="hover:text-blue-600 flex items-center gap-1"
                                  title="View source article"
                                >
                                  <FiExternalLink size={12} />
                                  Source
                                </a>
                              </>
                            )}
                            <span>|</span>
                            <button
                              onClick={() => handleArchive(article.id)}
                              className="hover:text-red-600"
                            >
                              Trash
                            </button>
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-600">
                        {getCategoryLabel(article.category)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {article.author_name || '—'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        <div className="font-medium">{timeInfo.relative}</div>
                        <div className="text-xs text-gray-400">{timeInfo.label}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        {/* Quick Actions */}
                        {article.status === 'fetched' && (
                          <button
                            onClick={() => handleGenerate(article.id)}
                            disabled={generatingArticles.has(article.id)}
                            className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors text-xs font-medium flex items-center gap-1"
                            title="Generate Article"
                          >
                            {generatingArticles.has(article.id) ? (
                              <>
                                <FiRefreshCw className="animate-spin" size={12} />
                                Generating...
                              </>
                            ) : (
                              <>
                                <FiPlay size={12} />
                                Generate
                              </>
                            )}
                          </button>
                        )}
                        {article.status === 'draft' && (
                          <>
                            <button
                              onClick={() => handlePublish(article.id)}
                              className="px-3 py-1.5 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs font-medium flex items-center gap-1"
                              title="Publish"
                            >
                              <FiCheck size={12} />
                              Publish
                            </button>
                            <Link
                              to={`/articles/${article.id}/edit`}
                              className="px-3 py-1.5 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-xs font-medium flex items-center gap-1"
                              title="Edit Article"
                            >
                              <FiEdit size={12} />
                              Edit
                            </Link>
                          </>
                        )}
                        {article.status === 'published' && (
                          <>
                            <Link
                              to={`/articles/${article.id}/edit`}
                              className="px-3 py-1.5 bg-primary-600 text-white rounded hover:bg-primary-700 transition-colors text-xs font-medium flex items-center gap-1"
                              title="Edit Article"
                            >
                              <FiEdit size={12} />
                              Edit
                            </Link>
                            <button
                              onClick={() => handleArchive(article.id)}
                              className="px-3 py-1.5 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors text-xs font-medium flex items-center gap-1"
                              title="Move to Trash"
                            >
                              <FiTrash2 size={12} />
                              Trash
                            </button>
                          </>
                        )}
                        <div className="relative">
                          <button
                            onClick={() => setShowQuickActions(showQuickActions === article.id ? null : article.id)}
                            className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded"
                            title="More actions"
                          >
                            <FiMoreVertical size={16} />
                          </button>
                          {showQuickActions === article.id && (
                            <>
                              <div
                                className="fixed inset-0 z-10"
                                onClick={() => setShowQuickActions(null)}
                              />
                              <div className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-20">
                                <div className="py-1">
                                  <Link
                                    to={`/articles/${article.id}/edit`}
                                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    onClick={() => setShowQuickActions(null)}
                                  >
                                    <FiEdit className="inline mr-2" size={14} />
                                    Edit
                                  </Link>
                                  {article.status !== 'published' && article.status !== 'fetched' && (
                                    <button
                                      onClick={() => {
                                        handlePublish(article.id)
                                        setShowQuickActions(null)
                                      }}
                                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    >
                                      <FiCheck className="inline mr-2" size={14} />
                                      Publish
                                    </button>
                                  )}
                                  {article.status === 'published' && (
                                    <button
                                      onClick={() => {
                                        handleMoveToDraft(article.id)
                                        setShowQuickActions(null)
                                      }}
                                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                                    >
                                      <FiClock className="inline mr-2" size={14} />
                                      Move to Draft
                                    </button>
                                  )}
                                  <button
                                    onClick={() => {
                                      handleArchive(article.id)
                                      setShowQuickActions(null)
                                    }}
                                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                                  >
                                    <FiTrash2 className="inline mr-2" size={14} />
                                    Move to Trash
                                  </button>
                                </div>
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ArticleList
