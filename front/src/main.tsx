/**
 * @file Application bootstrap - mounts the React tree into the DOM.
 *
 * This is the single entry-point bundled by Vite. It:
 * 1. Locates the `#root` element defined in `index.html`.
 * 2. Creates a React root with `createRoot` (concurrent mode).
 * 3. Renders {@link App} wrapped in `StrictMode` to surface potential issues
 *    during development.
 *
 * @module main
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

/**
 * Mount the application.
 *
 * The non-null assertion (`!`) is intentional: `index.html` always contains
 * `<div id="root">`, so the element is guaranteed to exist at runtime.
 */
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
