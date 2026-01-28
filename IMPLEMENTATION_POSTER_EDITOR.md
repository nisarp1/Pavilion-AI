# CMS Poster Editor Implementation Plan

## Objective
Enable manual editing of social media posters within the CMS. Users should be able to drag, resize, and edit text/images on a canvas before saving the final poster.

## Architecture

### Backend (Django)
1.  **New API Action**: `GET /api/v1/cms/articles/{id}/poster_editor_config/`
    *   Returns JSON containing:
        *   Template dimensions (1080x1350 etc)
        *   Background Image URL
        *   **Asset URL**: The background-removed version of the article's featured image.
        *   **Text Layers**: Initial text content (Headline, Summary) with X/Y/Font/Color from `poster_layouts.json`.
2.  **Asset Preparation**:
    *   The `poster_editor_config` endpoint must ensure the background-removed image exists. If not, it runs `rembg` and saves a temporary/cached version (e.g., `media/articles/cutouts/cutout_{id}.png`).
3.  **Save Action**: `POST /api/v1/cms/articles/{id}/upload_poster/`
    *   Already exists or easy to add. Accepts a file blob and saves it to `generated_poster`.

### Frontend (Next.js)
1.  **Editor Component**:
    *   Using **Fabric.js** (v5 or v6) for the canvas.
    *   Loads the configuration from the backend.
    *   Layers:
        *   Background Image (Locked)
        *   Cutout Image (Movable, Resizable)
        *   Headline Text (Editable, Movable)
        *   Summary Text (Editable, Movable)
        *   Logo/Footer (Locked or Movable)
2.  **UI Controls**:
    *   "Regenerate Cutout" (if auto-removal failed).
    *   Text editing tools (simple font size/color toggle?).
    *   **SAVE** button: Converts canvas to Blob -> Uploads to API.

## Step-by-Step Implementation

### Step 1: Backend - Cutout Management
- [ ] Add `cutout_image` field to Article model (optional, or just manage file path manually).
- [ ] Create `prepare_cutout_image(article)` utility function using `rembg`.
- [ ] Update `ArticleViewSet` with `poster_editor_config` action.

### Step 2: Frontend - Editor UI
- [ ] Install `fabric`.
- [ ] Create `PosterCanvas` component.
- [ ] Integrate with CMS Article View.

### Step 3: Deployment & Testing
- [ ] Verify `rembg` performance on Railway.
- [ ] Test Save functionality.
