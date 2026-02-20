import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteSingleFile } from 'vite-plugin-singlefile'

// vite-plugin-singlefile: CSS/JS をすべて index.html にインライン化し
// 単一ポータブル HTML ファイルとして出力する
export default defineConfig({
  plugins: [react(), viteSingleFile()],
  build: {
    // アセットをインライン化するしきい値を上限に設定
    assetsInlineLimit: 100_000_000,
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        // 単一チャンクに集約
        inlineDynamicImports: true,
      },
    },
  },
})
