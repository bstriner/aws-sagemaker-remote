
const path = require('path')
const awsExternals = require('webpack-aws-externals');
//import path from 'path'
//import awsExternals from 'webpack-aws-externals'
//const fs = require('fs');
//const ESLintPlugin = require('eslint-webpack-plugin');

const inputDir = process.env.INPUT_DIR
const outputDir = process.env.OUTPUT_DIR

console.log(`Running webpack from ${inputDir} to ${outputDir}`)

entries = {
  func: {
    import: path.join(inputDir, 'index.js'),
    filename: 'index.js'
  }
}

module.exports = {
  //plugins: [new ESLintPlugin({ context: inputDir })],
  context: inputDir,
  target: 'node',
  entry: entries,
  output: {
    libraryTarget: 'commonjs',
    path: outputDir
  },
  externals: [awsExternals()],
  module: {
    strictExportPresence: true,

    /*
    rules: [
      // ...
      // Rewrites and emits
      {
        test: /\.js$/,
        loader: "bindings-loader",
      },
    ],
    */
  }
}
