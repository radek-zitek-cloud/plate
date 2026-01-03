import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync, existsSync } from 'fs'
import { resolve } from 'path'

// Read version from VERSION file at project root
// In Docker builds, VERSION is passed as an environment variable
let version = process.env.VERSION || '0.0.0'

// If VERSION env var is not set, try to read from file (development)
if (version === '0.0.0') {
  const versionFilePath = resolve(__dirname, '../VERSION')
  if (existsSync(versionFilePath)) {
    version = readFileSync(versionFilePath, 'utf-8').trim()
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  define: {
    '__APP_VERSION__': JSON.stringify(version),
  },
})
