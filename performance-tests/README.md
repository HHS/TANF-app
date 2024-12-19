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

### Api vs browser - considerations

k6 allows tests to be written using the `k6/http` module, the `k6/browser` module, or both. These are described as api, browser, and hybrid tests, respectively.


#### Api performance tests
Api performance tests primarily rely on "api endpoints" when executing scenarios. These are best used when you're not trying to recreate a "realistic" user experience, or if the user experience you are trying to recreate is primarily api-driven. These kinds of tests are useful for stressing the system in a specific ways, allowing for parts of the system to be tested and monitored in isolation.

##### Api example


#### Browser performance tests
Browser performance tests use a headless browser similar to our end-to-end tests. They can step through the ui, click elements, and watch network requests that happen on the page. This is useful for creating tests that recreate a user's experience in a realistic way. These kinds of tests can tell you if the user might experience some page load delays or other performance-related things in some situations. They can also stress ancillary systems that may not have been the target of the test, providing better coverage and potentially revealing gaps in thinking or coverage.

##### Browser example



#### Hybrid performance tests
Hybrid performance tests simply consist of both api and browser performance testing techniques in the same test. These can be individual scenarios run in parallel, or the same scenario with different types of requests mixed in. These are useful for hybrid workflows, as well as for testing complex systems that may rely partly on user-experience-driven activities for some aspects and api-driven activities for others.

##### Hybrid example



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



#### Specifying a scenario to run