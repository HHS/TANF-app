import http from 'k6/http';
import encoding from 'k6/encoding';
import { browser } from 'k6/browser';
import { sleep } from 'k6';
import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js';
import { attachAuthCookiesToBrowser, login } from '../utils.js'
import { Section2File, readAll } from '../files.js'

const file = open('../data/ADS.E2J.FTP2.TS06')

const loadProfiles = {
  unit: {
    vus: 1,
    iterations: 1,
    executor: 'per-vu-iterations'
  },

  ramping: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '20s', target: 2 }, // 0-10vu over 20s
      { duration: '20s', target: 4 },
      { duration: '20s', target: 6 },
      { duration: '20s', target: 8 },
      { duration: '20s', target: 10 },
      { duration: '2m', target: 10 },
      { duration: '40s', target: 0 }
    ],
    gracefulRampDown: '60s',
  }
}

const scenarios = {
  browser: {
    options: {
      browser: {
        type: 'chromium',
      },
    },
    exec: 'dataFileBrowserSubmission',
    ...loadProfiles.unit,
  },
  api: {
    exec: 'dataFileApiSubmission',
    ...loadProfiles.ramping,
  }
}

const SCENARIO = __ENV.SCENARIO || null

export const options = {
  scenarios: SCENARIO ? { [SCENARIO]: scenarios[SCENARIO] } : scenarios,

  thresholds: {
    checks: ['rate==1.0'],
  },
};

// how to stress celery process specifically?
// - long running tasks
// - large files
// - large queries
// http-based, pointed stress test
// submit data files (of different sizes?)
// track time to parse, overwhelm on celery workers
// - memory (reaches 2gb)
// - restarts due to OOM (not max-child) (celery_task_failed_total)
export const dataFileApiSubmission = async () => {
  login()
  const httpCookies = http.cookieJar().cookiesForURL(__ENV.BASE_URL)

  const body = {
    file: http.file(file, 'loadtest-file.txt'),
    original_filename: 'ADS.E2J.FTP2.TS06',
    user: 'f94b3a2e-4ee5-4d4b-bab3-20147cb6f480',
    section: 'Closed Case Data',
    year: '2021',
    stt: 4,
    quarter: 'Q1',
    ssp: false,
    slug: '123'
  }

  const response = http.post(`${__ENV.BASE_URL}/v1/data_files/`, body, {
    headers: {
      'X-CSRFToken': httpCookies['csrftoken'],
    }
  })

  check(response, {
    'upload request 201': r => {
      console.log(r.status)
      console.log(r.body)
      return r.status === 201
    }
  })

  sleep(1)
}

export const dataFileBrowserSubmission = async () => {
  login()

  let context = await browser.newContext()
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
