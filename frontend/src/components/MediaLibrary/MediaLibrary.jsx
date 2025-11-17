import { useState, useEffect, useRef } from 'react'
import { FiSearch, FiUpload, FiX, FiImage, FiCheck } from 'react-icons/fi'
import api from '../../services/api'

function MediaLibrary({ isOpen, onClose, onSelect }) {
  const [media, setMedia] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedMedia, setSelectedMedia] = useState(null)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (isOpen) {
      fetchMedia()
    }
  }, [isOpen, searchQuery])

  const fetchMedia = async () => {
    setLoading(true)
    try {
      const params = {}
      if (searchQuery) {
        params.search = searchQuery
      }
      const response = await api.get('/media/', { params })
      // Handle both paginated and non-paginated responses
      const mediaData = response.data.results || response.data || []
      setMedia(Array.isArray(mediaData) ? mediaData : [])
    } catch (error) {
      console.error('Error fetching media:', error)
      setMedia([])
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    const files = Array.from(e.target.files || [])
    if (files.length === 0) return

    setUploading(true)
    try {
      const uploadPromises = files.map(file => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('title', file.name)
        return api.post('/media/', formData)
      })

      await Promise.all(uploadPromises)
      await fetchMedia()
    } catch (error) {
      console.error('Error uploading media:', error)
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.file?.[0] || 
                          error.message || 
                          'Failed to upload image(s). Please try again.'
      alert(`Upload failed: ${errorMessage}`)
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleSelect = (mediaItem) => {
    setSelectedMedia(mediaItem)
  }

  const handleConfirm = () => {
    if (selectedMedia && onSelect) {
      onSelect(selectedMedia)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="relative bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-800">Media Library</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <FiX size={24} />
            </button>
          </div>

          {/* Toolbar */}
          <div className="p-4 border-b border-gray-200 space-y-4">
            {/* Search */}
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search media..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>

            {/* Upload Button */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploading}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <FiUpload size={18} />
                {uploading ? 'Uploading...' : 'Upload Images'}
              </button>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleUpload}
                accept="image/*"
                multiple
                className="hidden"
              />
              {selectedMedia && (
                <span className="text-sm text-gray-600">
                  {selectedMedia.title} selected
                </span>
              )}
            </div>
          </div>

          {/* Media Grid */}
          <div className="flex-1 overflow-y-auto p-6">
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              </div>
            ) : media.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-64 text-gray-500">
                <FiImage size={48} className="mb-4" />
                <p>No images found</p>
                <p className="text-sm mt-2">Upload images to get started</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {media.map((item) => (
                  <div
                    key={item.id}
                    onClick={() => handleSelect(item)}
                    className={`relative group cursor-pointer border-2 rounded-lg overflow-hidden transition-all ${
                      selectedMedia?.id === item.id
                        ? 'border-primary-600 ring-2 ring-primary-200'
                        : 'border-gray-200 hover:border-primary-300'
                    }`}
                  >
                    <div className="aspect-square bg-gray-100">
                      <img
                        src={item.url}
                        alt={item.alt_text || item.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none'
                          const parent = e.target.parentElement
                          if (parent) {
                            parent.innerHTML = '<div class="w-full h-full flex items-center justify-center text-gray-400"><svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg></div>'
                          }
                        }}
                      />
                    </div>
                    {selectedMedia?.id === item.id && (
                      <div className="absolute top-2 right-2 bg-primary-600 text-white rounded-full p-1">
                        <FiCheck size={16} />
                      </div>
                    )}
                    <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-2 text-xs truncate opacity-0 group-hover:opacity-100 transition-opacity">
                      {item.title}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={!selectedMedia}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Select Image
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MediaLibrary

