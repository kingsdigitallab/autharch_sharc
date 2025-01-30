module.exports = {
  devServer: {
    proxy: {
      "^/api": {
        target: "https://sharc-api.kdl.kcl.ac.uk",
        changeOrigin: true,
      },
      "^/media": {
        target: "https://sharc-api.kdl.kcl.ac.uk",
        changeOrigin: true,
      },
      "^/rct": {
        target: "https://sharc-api.kdl.kcl.ac.uk",
        changeOrigin: true,
      },
    },
  },
};
