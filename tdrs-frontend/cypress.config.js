const { defineConfig } = require('cypress')
const webpack = require('@cypress/webpack-preprocessor')
const preprocessor = require('@badeball/cypress-cucumber-preprocessor')
const XLSX = require('xlsx')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: '**/*.feature',

    env: {
      apiUrl: 'http://localhost:3000/v1',
      adminUrl: 'http://localhost:3000/admin',
      cypressToken: 'local-cypress-token',
    },

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
      // TODO: Return json data for both worksheets
      on('task', {
        convertXlsxToJson(filePath) {
          const workbook = XLSX.readFile(filePath)
          const worksheet = workbook.Sheets[workbook.SheetNames[0]]
          const jsonData = XLSX.utils.sheet_to_json(worksheet)
          return jsonData
        },
      })

      on('file:preprocessor', webpack({ webpackOptions }))

      return config
    },
  },
})
