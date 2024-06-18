export default {
  base: "./",
  build: {
    lib: {
      entry: "./src/main.js",
      name: "pan3d_components",
      formats: ["umd"],
      fileName: "pan3d-components",
    },
    rollupOptions: {
      external: ["vue"],
      output: {
        globals: {
          vue: "Vue",
        },
      },
    },
    outDir: "serve",
    assetsDir: ".",
  },
};
