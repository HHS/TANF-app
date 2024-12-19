# TDP Performance Tests

This part of the repo contains performance tests written in [k6](https://k6.io/), a Go-based load test runner that allows the tests to be written in JavaScript. This offers superior performance and flexibility for developers, as well as allowing for tests to be easily run from a CI pipeline.

## Running tests
### Installation

Follow the [k6 installation documentation](https://grafana.com/docs/k6/latest/set-up/install-k6/) for the most up-to-date instructions on installing the tool.

For Mac, it is recommended to install with HomeBrew
```bash
brew install k6
```

You can now create a sample script
```bash
k6 new
```

or, run an existing script
```bash
cd ./performance-tests
k6 run path/to/script.js
```

For convenience, a command containing some extra features has been added to the `Taskfile`.

### Taskfile command

The `Taskfile` at the root of the repo contains a `k6` command that executes the `k6 run` command. At its simplest, the task can be run like this:
```bash
task k6 SCRIPT=path/to/script.js
```

The following parameters are provided

* `SCRIPT` (required) - the path of the script to execute. No need to include the `performance-tests` directory, as that is the `dir` of the task.
* `BASE_URL` (optional, default: `http://localhost:3000`) - the base url can be switched to run tests in different environments.
* `CYPRESS_TOKEN` (optional, default: `local-cypress-token`) - if changing the `BASE_URL`, make sure the cypress token matches the environment you're running tests for. This is required so that test users can authenticate.
* `SCENARIO` (optional, default: `null`) - the name of the test scenario to run. If `null`, will run all scenarios.

#### Running against a deployed environment

To run tests against a deployed environment, update the `BASE_URL` and `CYPRESS_TOKEN` provided to the `task`

```bash
task k6 BASE_URL=https://deployed-env.app.cloud.gov CYPRESS_TOKEN=not-the-real-one SCRIPT=path/to/script.js
```

## Writing tests

k6 has two primary approaches for writing tests (api and browser) as well as options to customize the load applied to the system, thus creating many "types" of tests that can be written with the tool. This section explores different approaches and considerations when writing performance tests, as well as describes a few useful techniques that appear in existing tests.

### Api vs browser

k6 allows tests to be written using the `k6/http` module, the `k6/browser` module, or both. These are described as api, browser, and hybrid tests, respectively.


#### Api performance tests
Api performance tests primarily rely on "api endpoints" when executing scenarios. These are best used when you're not trying to recreate a "realistic" user experience, or if the user experience you are trying to recreate is primarily api-driven. These kinds of tests are useful for stressing the system in a specific ways, allowing for parts of the system to be tested and monitored in isolation.

##### Api example

The below example executes a `POST` request on an endopint, checks that the response is a `201`, then ends. This is an api test simply because it only interacts with api endpoints and not a page in a browser.
```js
import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js';

export const options = {
    executor: 'per-vu-iterations',
    vus: 1,
    iterations: 1,
}

export default () => {
    const body = {
        year: '2021',
        stt: 4,
        quarter: 'Q1',
        ssp: false,
    }

    const response = http.post(`${__ENV.BASE_URL}/v1/data_files/`, JSON.stringify(body), {
        headers: {
        'Content-Type': 'application/json',
        }
    })

    check(response, {
        'post request 201': r => {
            return r.status === 201
        }
    })

    sleep(1)
}
```


#### Browser performance tests
Browser performance tests use a headless browser similar to our end-to-end tests. They can step through the ui, click elements, and watch network requests that happen on the page. This is useful for creating tests that recreate a user's experience in a realistic way. These kinds of tests can tell you if the user might experience some page load delays or other performance-related things in some situations. They can also stress ancillary systems that may not have been the target of the test, providing better coverage and potentially revealing gaps in thinking or coverage.

##### Browser example

This example navigates to a page using a headless browser (similar to our cypress tests), then fills out the form by selecting elements on the page. The form is submitted by clicking the "Submit" button and waiting for the network requests to complete, then checking that the UI updated accordingly. We don't use http requests or api endpoints directly, but instead use them in the context of the user's interaction with the page. This is useful because additional requests may be sent by the page when loaded in the browser, requests which wouldn't have been replicated by the api-only version of the test.
```js
import { browser } from 'k6/browser';
import { sleep } from 'k6';
import { check } from 'https://jslib.k6.io/k6-utils/1.5.0/index.js';

export const options = {
    executor: 'per-vu-iterations',
    vus: 1,
    iterations: 1,
}

export default () => {
    let context = await browser.newContext()
    const page = await context.newPage()
    await page.goto(`${__ENV.BASE_URL}/data-files`, { waitUntil: 'networkidle' })

    sleep(1)

    const sttInput = page.locator('#stt')
    await sttInput.selectOption('Arkansas')

    const yearInput = page.locator('#reportingYears')
    await yearInput.selectOption('2021')

    const quarterInput = page.locator('#quarter')
    await quarterInput.selectOption('Q1')

    const submitButton = page.locator('//button[text()="Submit"]')
    await submitButton.click()

    sleep(1)

    await page.waitForLoadState('networkidle')

    await check(page.locator('.usa-alert'), {
        'successfully submitted alert': async alert => {
            const text = await alert.textContent()
            return text.includes('Successfully submitted')
        }
    })
}
```

#### Hybrid performance tests
Hybrid performance tests simply consist of both api and browser performance testing techniques in the same test. These can be individual scenarios run in parallel, or the same scenario with different types of requests mixed in. These are useful for hybrid workflows, as well as for testing complex systems that may rely partly on user-experience-driven activities for some aspects and api-driven activities for others.

### Types of performance tests

The "type" of performance test is generally defined by how the load is applied to the system. The k6 documentation provides an excellent [guide for the types of load tests](https://grafana.com/docs/k6/latest/testing-guides/test-types/), which is the basis for this section.

* Smoke tests - very low throughput. Start here when developing tests and to get a baseline for how the system performs under minimal load.
* Average load tests - how the system performs under expected conditions
* Stress tests - how the system performs during higher-than-expected load
* Soak tests - how the system performs over an extended period of time. These can help identify issues that normally wouldn't be revealed by a system test, such as api limits exceeded or maintenance windows causing exceptions.
* Spike tests - how the system handles a sudden, high increase in load over a short period
* Breakpoint tests - gradually increased load to identify the system's limits

Different types of tests can help to identify different issues. The type of test you choose should reflect the use-case for which you're writing the test. In k6, the load applied is managed by Scenarios. The same test script can be used with different scenarios, making it easy to change the test type on-the-fly, or incoporate the same script into multiple tests. Multiple test types should be incorporated to assess different failure points in the system.

#### Scenarios

Scenarios are specified as part of the exported `options` object in everyt test, and consist of a few parts
* `executor` - controls how k6 schedules traffic for the test. Depending on the executor you choose, you may specify the following
   * `vus` - the number of virtual users (concurrent executions) to spin up.
   * `iterations` - how many iterations should be run in the test (depending on the executor, these can be iterations per-vu iterations, or total iterations shared between all VUs).
   * `duration` - how long the test should run.
* `stages` - an optional parameter that can be provided for any executor. Allows you to configure `vus`, `iterations`, and/or `duration` to change at different points of the test.
* `exec` - the function that the scenario should execute (`default` by default).

The k6 documentation provides a [guide on executors](https://grafana.com/docs/k6/latest/using-k6/scenarios/executors/) included examples for how each can be used. A couple of commonly-used examples are reproduced below.


##### No stages

A smoke test is the simplest scenario. The goal is simply to ensure the test passes and the system works. This uses the `per-vu-iterations` executor to spin up a single VU that executes the scenario a single time.
```js
export const options = {
    scenarios: {
        executor: 'per-vu-iterations',
        vus: 1,
        iterations: 1,
    }
}
```

This can be further configured for constant-load tests by using more `vus` and/or `iterations`. Or, using the `constant-vus` executor, we can configure `duration` so that each VU executes for a set amount of time.
```js
export const options = {
    scenarios: {
        executor: 'constant-vus',
        vus: 1,
        duration: `30s`,
    }
}
```

##### Stages

For more control over how much load is applied to the system when, `stages` can be configured. This allows you to change the `vus` and `iterations` (or `duration`, depending on the executor) at specified points in the test.

For example, to introduce a ramp-up and ramp-down stage to a scenario:
```js
export const options = {
    scenarios: {
        executor: 'ramping-vus',
        startVUs: 2,
        stages: [
            { duration: '20s', target: 4 },
            { duration: '2m', target: 4 },
            { duration: '40s', target: 0 }
        ],
        gracefulRampDown: '60s',
    }
}
```

This starts the test with 2 VUs, then, over the course of 20 seconds, will add 2 additional VUs. After 2 minutes executing 4 VUs, the test will spend 40 seconds attempting to ramp-down (VUs will be discontinued once they complete their iteration. They are given additional `gracefulRampDown` to complete the iteration before they are hard-stopped).

These stages can be used to configure the Average Load, Stress, Soak, Spike, and Breakpoint tests described above. Visit the [k6 documentation on load test types](https://grafana.com/docs/k6/latest/testing-guides/test-types/) for examples pertaining to each type of test.


#### Specifying a scenario to run

The k6 command in the `Taskfile` accepts a `SCENARIO` argument, but there's some work to do to make this work in every individual test.

In the global scope of the test (outside any functions), get the value of the `SCENARIO` environment variable (or `null` as a default)
```js
const SCENARIO = __ENV.SCENARIO || null
```

Scenarios should be specified as their own object, outside of `options`
```js
const scenarios = {
    scenario1: {
        exec: 'scenario1Function',
        executor: 'per-vu-iterations'
        vus: 1,
        iterations: 1,
    },
    scenario2: {
        exec: 'scenario2Function',
        executor: 'ramping-vus',
        startVUs: 2,
        stages: [
            { duration: '20s', target: 4 },
            { duration: '2m', target: 4 },
            { duration: '40s', target: 0 }
        ],
        gracefulRampDown: '60s',
    }
}
```

Next, the `options` object should be modified to select a scenario if one is provided (otherwise provide the entire `scenarios` object)
```js
export const options = {
    scenarios: SCENARIO ? { [SCENARIO]: scenarios[SCENARIO] } : scenarios,

    // ...
}
```

if `SCENARIO` is not provided to the `task k6` command (so `__ENV.SCENARIO` is `null`), all scenarios will be run.


### Features to consider in the future
* thresholds, groups/tags, metrics/custom metrics
* grafana cloud - https://grafana.com/docs/grafana-cloud/testing/k6/
* synthetic monitoring - https://grafana.com/docs/k6/latest/testing-guides/synthetic-monitoring/
* disruptor - https://grafana.com/docs/k6/latest/testing-guides/injecting-faults-with-xk6-disruptor/