// cypress/reporters/custom.js

const MochaJUnitReporter = require('mocha-junit-reporter')
const fs = require('fs')
const path = require('path')

class CustomJUnitReporter extends MochaJUnitReporter {
  constructor(runner, options) {
    super(runner, options)

    // Access reporter options
    this.options = options.reporterOptions

    // Listen for the 'end' event to perform actions after all tests are run
    runner.on('end', () => {
      this.generateCustomXml()
    })
  }

  // TODO: FIX ME: this loop recreates the customAttribute mutiple times to the files

  generateCustomXml() {
    const reportsDir = path.dirname(this.options.mochaFile || './');
    const filePattern = /^custom-report-.*\.xml$/;

    const files = fs.readdirSync(reportsDir);
    const matchingFiles = files.filter((file) => filePattern.test(file));

    if (matchingFiles.length === 0) {
      console.warn(
        `No JUnit XML files matching pattern found in: ${reportsDir}`
      )
      return
    }

    // Read and modify each matching XML file. Uncomment the following lines to enable
    matchingFiles.forEach((file) => {
      //const fullPath = path.join(reportsDir, file);
      //let xmlContent = fs.readFileSync(fullPath, 'utf8');
      // Modify the XML content: Add a custom attribute to <testsuite>
      //xmlContent = xmlContent.replace('<testsuite ', '<testsuite customAttribute="yourValue" ');
      //fs.writeFileSync(fullPath, xmlContent, 'utf8');
      //console.log(`Custom XML modified at: ${fullPath}`);
    })
  }
}

module.exports = CustomJUnitReporter;
