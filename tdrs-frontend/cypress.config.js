const { defineConfig } = require('cypress')
const webpack = require('@cypress/webpack-preprocessor')
const preprocessor = require('@badeball/cypress-cucumber-preprocessor')
const fs = require('fs')

module.exports = defineConfig({
  video: true,
  reporter: 'mocha-multi-reporters',
  reporterOptions: {
    configFile: 'cypress/reporters/multi-reporters-config.json',
    mochaFile: 'cypress/results/custom-report-[hash].xml', // Output path for the XML
    // Add other options as needed for mocha-junit-reporter
    json: true,
    //html: true,
    messages: {
      enabled: true,
      output: 'cypress/reports/cucumber-messages.ndjson', // Important
    },
  },
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

      await preprocessor.addCucumberPreprocessorPlugin(on, config, {
        messages: {
          enabled: true,
          output: 'cypress/reports/cucumber-messages.ndjson', // Important
        },
      })

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
        log(message) {
          console.log(message)

          return null
        },
        table(message) {
          console.table(message)

          return null
        },
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
