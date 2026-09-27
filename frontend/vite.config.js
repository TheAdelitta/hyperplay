import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// Local dev forwards /api to the FastAPI backend, so the browser never needs CORS or a
// hard-coded backend URL. Override with VITE_API_PROXY when the backend runs elsewhere.
const apiTarget = process.env.VITE_API_PROXY ?? 'http://127.0.0.1:8000';

export default defineConfig({
	plugins: [svelte()],
	resolve: { alias: { $lib: fileURLToPath(new URL('./src/lib', import.meta.url)) } },
	server: { proxy: { '/api': { target: apiTarget, changeOrigin: true } } },
	build: { outDir: 'dist', emptyOutDir: true }
});
