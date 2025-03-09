const path = require('path');

module.exports = {
  entry: './static/js/react/index.js',
  output: {
    path: path.resolve(__dirname, 'static/js/dist'),
    filename: 'bundle.js',
    publicPath: '/static/js/dist/'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
  // Настройка для режима разработки
  devServer: {
    static: {
      directory: path.join(__dirname, 'static'),
    },
    hot: true,
    port: 8080,
    proxy: {
      '/game': 'http://backend:8085',
      '/health': 'http://backend:8085'
    },
    headers: {
      'Access-Control-Allow-Origin': '*'
    },
    allowedHosts: 'all',
  },
}; 