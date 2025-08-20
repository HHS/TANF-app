const { defineConfig } = require('cypress')
const webpack = require('@cypress/webpack-preprocessor')
const preprocessor = require('@badeball/cypress-cucumber-preprocessor')
const fs = require('fs')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: '**/*.feature',

    env: {
      apiUrl: 'http://localhost:3000/v1',
      adminUrl: 'http://localhost:3000/admin',
      cypressToken: 'local-cypress-token',
    },

    viewportHeight: 1000,
    viewportWidth: 1600,

    async setupNodeEvents(on, config) {
      // implement node event listeners here
      await preprocessor.addCucumberPreprocessorPlugin(on, config)

      const webpackOptions = {
        resolve: {
          extensions: ['.ts', '.js'],
        },
        module: {
          rules: [
            {
              test: /\.feature$/,
              use: [
                {
                  loader: '@badeball/cypress-cucumber-preprocessor/webpack',
                  options: config,
                },
              ],
            },
          ],
        },
      }

      // Register custom task to execute JS in Node Environment
      on('task', {
        deleteDownloadFile(fileName) {
          const filePath = `${config.downloadsFolder}/${fileName}`

          if (fs.existsSync(filePath)) {
            fs.rmSync(filePath)
            return filePath
          } else {
            throw new Error(`File not found: ${filePath}`)
          }
        },
      })

      on('file:preprocessor', webpack({ webpackOptions }))

      return config
    },
  },
})
