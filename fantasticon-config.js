module.exports = {
  name: 'custom-icons',
  inputDir: './assets/icons',
  outputDir: './static/fonts',
  fontTypes: ['woff2', 'woff'],
  assetTypes: ['css'],
  prefix: 'icon',
  selector: '.icon',
  // Use the full URL for fontsUrl to ensure it's used in the generated CSS
  fontsUrl: 'https://niallxd.github.io/ecoscapes-maps/static/fonts',
  // Use a simpler pathOptions format
  pathOptions: {
    css: './static/fonts/custom-icons.css'
  }
};
