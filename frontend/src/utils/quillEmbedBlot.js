/**
 * Custom Quill Blot for embedding iframes and social media content
 * This MUST be imported before any Quill instances are created
 */
import Quill from 'quill'

const BlockEmbed = Quill.import('blots/block/embed')
const Parchment = Quill.import('parchment')

class VideoEmbed extends BlockEmbed {
  static create(value) {
    const node = super.create()
    node.setAttribute('contenteditable', 'false')
    if (typeof value === 'string') {
      node.innerHTML = value
    } else {
      // Fallback or complex object handling if we add it later
      // For now, assume value is the HTML string
      console.warn('VideoEmbed: received non-string value', value)
    }
    return node
  }

  static value(node) {
    // Return the innerHTML if it exists, otherwise return object representation
    if (node.innerHTML) {
      return node.innerHTML
    }
    return {
      src: node.getAttribute('src'),
      width: node.getAttribute('width'),
      height: node.getAttribute('height')
    }
  }
}

VideoEmbed.blotName = 'videoEmbed'
VideoEmbed.tagName = 'div'
VideoEmbed.className = 'ql-video-embed'

class SocialEmbed extends BlockEmbed {
  static create(value) {
    const node = super.create()
    node.setAttribute('contenteditable', 'false')
    if (typeof value === 'string') {
      node.innerHTML = value
    }
    return node
  }

  static value(node) {
    return node.innerHTML || ''
  }
}

SocialEmbed.blotName = 'socialEmbed'
SocialEmbed.tagName = 'div'
SocialEmbed.className = 'ql-social-embed'

// Register the blots - this must happen before any Quill instances are created
try {
  Quill.register(VideoEmbed, true)
  Quill.register(SocialEmbed, true)
  console.log('✅ Custom embeds registered successfully')
} catch (error) {
  console.error('❌ Error registering custom blots:', error)
}

export { VideoEmbed, SocialEmbed }

