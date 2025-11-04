import { configureStore } from '@reduxjs/toolkit'
import authReducer from './slices/authSlice'
import articleReducer from './slices/articleSlice'
import rssReducer from './slices/rssSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    articles: articleReducer,
    rss: rssReducer,
  },
})

