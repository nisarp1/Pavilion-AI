# Issue Resolution: Infinite Spinner on Generation

## Problem behavior
The user reported that clicking "Generate" caused an infinite spinner, and the UI only updated to "Edit" (statue: draft) after a manual page refresh.

## Root Causes
1. **Missing Import**: `fetchArticle` was NOT imported in `ArticleList.jsx`, causing a `ReferenceError` inside the polling loop. This error was caught by the `try/catch` block, logged to console (invisible to user), and the loop continued indefinitely without successfully checking the article status.
2. **Potential Stale Data**: The polling mechanism relies on `fetchArticle` to check status. Browsers or proxies might cache the GET request, returning the old 'fetched' status repeatedly even after the backend updated it to 'draft'.
3. **Duplicate Polling**: The polling effect in `ArticleList.jsx` was re-running whenever `generatingIds` length changed (or array changed), spawning duplicate intervals for the same article ID, increasing network load.

## Fixes Implemented
1. **Fix Missing Import**: Imported `fetchArticle` in `ArticleList.jsx`.
2. **Prevent Caching**: Added a timestamp query parameter (`?_t=${Date.now()}`) to the `fetchArticle` API call in `articleSlice.js`. This guarantees fresh data during polling.
3. **Optimize Polling**: Implemented a `useRef` based `activePolls` tracking in `ArticleList.jsx` to ensure only one polling interval runs per article ID, even if the component re-renders or the list changes.

## Verification
- Code syntax checked.
- Logic verified.
- The "Refresh Fix" is complete.
