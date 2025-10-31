import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export const fetchArticles = createAsyncThunk(
  'articles/fetchArticles',
  async ({ status, page = 1 }, { rejectWithValue }) => {
    try {
      const params = { page }
      if (status) params.status = status
      const response = await api.get('/articles/', { params })
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const fetchArticle = createAsyncThunk(
  'articles/fetchArticle',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/articles/${id}/`)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const createArticle = createAsyncThunk(
  'articles/createArticle',
  async (articleData, { rejectWithValue }) => {
    try {
      const response = await api.post('/articles/', articleData)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const updateArticle = createAsyncThunk(
  'articles/updateArticle',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.patch(`/articles/${id}/`, data)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const generateArticle = createAsyncThunk(
  'articles/generateArticle',
  async (articleId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/articles/${articleId}/generate/`)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const publishArticle = createAsyncThunk(
  'articles/publishArticle',
  async (articleId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/articles/${articleId}/publish/`)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

export const archiveArticle = createAsyncThunk(
  'articles/archiveArticle',
  async (articleId, { rejectWithValue }) => {
    try {
      const response = await api.post(`/articles/${articleId}/archive/`)
      return response.data
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message)
    }
  }
)

const articleSlice = createSlice({
  name: 'articles',
  initialState: {
    items: [],
    currentArticle: null,
    pagination: {
      count: 0,
      next: null,
      previous: null,
    },
    loading: false,
    error: null,
  },
  reducers: {
    clearCurrentArticle: (state) => {
      state.currentArticle = null
    },
    clearError: (state) => {
      state.error = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchArticles.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchArticles.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload.results || action.payload
        state.pagination = {
          count: action.payload.count || action.payload.length,
          next: action.payload.next,
          previous: action.payload.previous,
        }
      })
      .addCase(fetchArticles.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      .addCase(fetchArticle.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(fetchArticle.fulfilled, (state, action) => {
        state.loading = false
        state.currentArticle = action.payload
      })
      .addCase(fetchArticle.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload
      })
      .addCase(createArticle.fulfilled, (state, action) => {
        state.items.unshift(action.payload)
      })
      .addCase(updateArticle.fulfilled, (state, action) => {
        const index = state.items.findIndex((item) => item.id === action.payload.id)
        if (index !== -1) {
          state.items[index] = action.payload
        }
        if (state.currentArticle?.id === action.payload.id) {
          state.currentArticle = action.payload
        }
      })
      .addCase(generateArticle.fulfilled, (state, action) => {
        // Article generation started
      })
      .addCase(publishArticle.fulfilled, (state, action) => {
        const index = state.items.findIndex((item) => item.id === action.payload.id)
        if (index !== -1) {
          state.items[index] = action.payload
        }
        if (state.currentArticle?.id === action.payload.id) {
          state.currentArticle = action.payload
        }
      })
      .addCase(archiveArticle.fulfilled, (state, action) => {
        const index = state.items.findIndex((item) => item.id === action.payload.id)
        if (index !== -1) {
          state.items[index] = action.payload
        }
        if (state.currentArticle?.id === action.payload.id) {
          state.currentArticle = action.payload
        }
      })
  },
})

export const { clearCurrentArticle, clearError } = articleSlice.actions
export default articleSlice.reducer

