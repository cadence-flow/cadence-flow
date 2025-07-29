import adapter from '@sveltejs/adapter-static'; // <-- IMPORT a_s
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Use adapter-static
    adapter: adapter({
      // Default options:
      pages: 'build', // output directory
      assets: 'build',
      fallback: 'index.html', // for Single-Page App mode
      precompress: false
    }),
    // This is important for SPA mode when running `npm run dev`
    prerender: {
      handleHttpError: 'ignore'
    }
  }
};

export default config;