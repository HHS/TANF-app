import http from 'k6/http';
import encoding from 'k6/encoding';
import { browser } from 'k6/browser';
import { sleep } from 'k6';
import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js';
import { attachAuthCookiesToBrowser, login } from '../utils.js'
import { Section2File, readAll } from '../files.js'

export const options = {
  scenarios: {
    browser: {
      vus: 1,
      iterations: 1,
      executor: 'shared-iterations',
      options: {
        browser: {
          type: 'chromium',
        },
      },
    },
  },

  thresholds: {
    checks: ['rate==1.0'],
  },
};


export default async () => {
  let context = await browser.newContext()

  login()
  context = attachAuthCookiesToBrowser(context)

  const page = await context.newPage()

  await page.goto(`${__ENV.BASE_URL}/`, { waitUntil: 'networkidle' })

  sleep(1)

  await page.goto(`${__ENV.BASE_URL}/data-files`, { waitUntil: 'networkidle' })

  sleep(1)

  const sttInput = page.locator('select[name="stt"]')
  await sttInput.selectOption('Arkansas')

  const yearInput = page.locator('#reportingYears')
  await yearInput.selectOption('2021')

  const quarterInput = page.locator('#quarter')
  await quarterInput.selectOption('Q1')

  const searchButton = page.locator('//button[text()="Search"]')
  await searchButton.click()

  await page.waitForLoadState('networkidle');

  sleep(1)

  const fileBuffer = await readAll(Section2File)
  const input = await page.$('#closed-case-data')
  await input.setInputFiles({
    name: 'load-test-file.txt',
    mimetype: 'text/plain',
    buffer: encoding.b64encode(fileBuffer),
  })

  sleep(1)

  const submitButton = page.locator('//button[text()="Submit Data Files"]')
  await submitButton.click()

  await page.waitForLoadState('networkidle');

  await check(page.locator('.usa-alert'), {
    'successfully submitted alert': async alert => {
      const text = await alert.textContent()
      return text.includes('Successfully submitted')
    }
  })

  page.close()
}
