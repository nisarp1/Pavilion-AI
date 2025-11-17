import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Login from './components/Auth/Login'
import Dashboard from './components/Dashboard/Dashboard'
import ArticleList from './components/Articles/ArticleList'
import ArticleEdit from './components/Articles/ArticleEdit'
import ArticleCreate from './components/Articles/ArticleCreate'
import RSSFeedManager from './components/RSSFeeds/RSSFeedManager'
import CategoryManager from './components/Categories/CategoryManager'
import ProtectedRoute from './components/ProtectedRoute'
import WebStoryList from './components/WebStories/WebStoryList'
import WebStoryCreate from './components/WebStories/WebStoryCreate'
import WebStoryEdit from './components/WebStories/WebStoryEdit'

function App() {
  const { isAuthenticated } = useSelector((state) => state.auth)

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" /> : <Login />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      >
        <Route index element={<ArticleList />} />
        <Route path="articles" element={<ArticleList />} />
        <Route path="articles/create" element={<ArticleCreate />} />
        <Route path="articles/:id/edit" element={<ArticleEdit />} />
        <Route path="rss-feeds" element={<RSSFeedManager />} />
        <Route path="categories" element={<CategoryManager />} />
        <Route path="webstories" element={<WebStoryList />} />
        <Route path="webstories/create" element={<WebStoryCreate />} />
        <Route path="webstories/:id/edit" element={<WebStoryEdit />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App

