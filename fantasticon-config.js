module.exports = {
  name: 'custom-icons',
  inputDir: './assets/icons',
  outputDir: './static/fonts',
  fontTypes: ['woff2', 'woff'],
  assetTypes: ['css'],
  prefix: 'icon',
  selector: '.icon',
  fontsUrl: '/static/fonts',
  pathOptions: {
    css: './static/fonts/custom-icons.css'
  }
};
