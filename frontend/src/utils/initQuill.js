/**
 * Initialize Quill modules - called once when app loads
 */
import Quill from 'quill'
import AutoEmbedModule from './quillAutoEmbed'

// Register auto-embed module
try {
  Quill.register('modules/autoEmbed', AutoEmbedModule)
  console.log('✅ AutoEmbed module registered')
} catch (error) {
  console.error('❌ Error registering AutoEmbed module:', error)
  // Don't throw - let the app continue even if module registration fails
}

