# Upgrading frontend dependencies (react-scripts v3 to v5)

**Audience**: TDP Software Engineers <br>
**Subject**:  Upgrading frontend dependencies - React Scripts v5 upgrade <br>
**Date**:     Dec 2, 2024 <br>

## Summary
This technical memorandum focuses on the effort required to upgrade react-scripts (create-react-app) from v3 to v5. This update contains breaking changes which are described, along with the changes required to fix them, below.

1. Webpack changes
2. SASS updates
3. USWDS
4. Browser vs Node runtime (file-type)

## Out of Scope
Out-of-scope for the dependency upgrade is anything not strictly related to the library version differences, including
* Any refactoring for improving readability or performance
* Removing any libraries that are unnecessary
* Fixing any deprecations not causing exceptions
* Fixing any frontend syntax errors or bugs not causing exceptions

Follow-on work has been outlined below and will be incorporated into future tickets.

## Method/Design
This section outlines the process by which frontend dependencies were upgraded, for this cycle. Included are error messages encountered, some background behind the issue or change needed, and the implemented change (or a note that the change was implemented and will be included as part of follow-on work).

### 1. Update all the dependencies using `npm-check-updates`
`npm-check-updates` checks for newer versions of libraries listed in `package.json` and modifies the file so that they can be installed.
* [npm-check-updates](https://github.com/raineorshine/npm-check-updates)


```bash
npx npm-check-updates -u
npm install
```

This will bump every package version to the latest available. However, since certain dependencies require specific versions of other packages, this step is not complete until dependency conflicts are resolved. You may receive errors such as this when compiling the application:

```bash
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
npm ERR!
npm ERR! While resolving: my-website@0.1.0
npm ERR! Found: react@16.14.0
npm ERR! node_modules/react
npm ERR!   react@"^16.8.0" from the root project
npm ERR!   peer react@"^16.8.0" from @material-ui/core@4.11.0
npm ERR!   node_modules/@material-ui/core
npm ERR!     @material-ui/core@"^4.11.0" from the root project
npm ERR!
npm ERR! Could not resolve dependency:
npm ERR! peer react@"17.0.1" from react-dom@17.0.1
npm ERR! node_modules/react-dom
npm ERR!   react-dom@"^17.0.1" from the root project
```

Downgrade/pin any dependency versions that are in conflict, then recompile.

### 2. Update the linter rules to allow trailing commas 

This small change ignores a new linter rule.

* In `.eslintrc.json`, add
    ```json
    "comma-dangle": 0,
    ```
* In `.prettierrc.json`, add
    ```json
    "singleQuote": true,
    "trailingComma": "es5"
    ```

### 3. Remove SASS_PATH from env

This line appears in the `.env` files, as well as the dockerfile. It will be replaced in step 7 (upgrade USWDS)

```bash
ENV SASS_PATH=node_modules:src
```

### 4. Implement React 18 changes

Another small change enables React 18. In `src/index.js` the root component should now look like this

```javascript
import React from 'react'
import { createRoot } from 'react-dom/client'

// ... other stuff, all the same

const container = document.getElementById('root')
const root = createRoot(container)
root.render(
    <Provider store={store}>
        <Router store={store} history={history}>
        <App />
        </Router>
    </Provider>
)
```

### 5. Update library imports

Some library imports changed. The new paths are generally included in the error message when compiling/bundling. If they aren't, consult the library's documentation for the new version. If they STILL aren't (it happens), you can go into `node_modules/{package name}/package.json` and find the `exports` section, which lists the export paths. From there, you can dig through the files to find what you're looking for.


One example is `thunk`, which had some minor export changes
```javascript
import thunkMiddleware from 'redux-thunk' // old way

import { thunk } from 'redux-thunk' // new way
```


Named exports (e.g., `import { thunk } from 'redux-thunk'`) can be renamed using the `as` keyword, so implementation code doesn't have to be further changed
```javascript
import { thunk as thunkMiddleware } from 'redux-thunk'
```

### 6. Update SASS import syntax

SASS has deprecated `@import` and global built-in functions to support the new module syntax ([documentation](https://sass-lang.com/documentation/breaking-changes/import/)). The following change was needed

In `src/index.scss` `@import` becomes `@forward`

```scss
@forward "src/assets/uswds/_uswds-theme-general";

@forward "uswds";

@forward 'src/assets/App';
@forward 'src/assets/GovBanner';
@forward 'src/assets/Header';
// etc
```

### 7. Implement USWDS v3

Upgrading SASS required that USWDS be upgraded to v3, which supports the new SASS modules. The [v3 migration guide](https://designsystem.digital.gov/documentation/migration/) was primarily used to perform the updates.


* `package.json` - `start` and `build` need the following pre-pended to the react-scripts command
    ```
    SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\"
    ```
    * e.g.
        ```json
        "start": "SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\" react-scripts start",
        "build": "sh -ac '. ./.env.${REACT_APP_ENV}; SASS_PATH=\"`cd \"./src\";pwd`:./node_modules/@uswds:./node_modules/@uswds/uswds/packages\" react-scripts build'",
        ```
* Theme customizations must be moved to a single file (imported once in `src/index.scss`)
    * Everything was moved to `src/assets/uswds/_uswds-theme-general.scss` following the migration guide
    * It is critical that all variables customized must have matching default in uswds config. If not, you will get weird import errors, like: `SassError: This module was already loaded, so it can't be configured using "with".`
    * Variables must also be moved to a separate file, on their own: `src/assets/uswds/_variables.scss`
        ```scss
        $disabled-button-color: #4A4A4A;
        $gov-banner-background: #122E51;
        // etc
        ```
        * Now must be imported by `@use "./assets/uswds/_variables" as *;` in custom scss files (`GovBanner.scss`, `Footer.scss`, etc)
    * Imports changed slightly for components and sass files (import paths can be found in `node_modules/@uswds/uswds/package.json` in the `exports` section)
        * Components
            ```javascript
            import { fileInput } from '@uswds/uswds/src/js/components'
            ```
        * SASS files (must `@use "{lib/file}" as *` to bring it into the same namespace)
            ```scss
            @use "uswds-core" as *;
            @use "./assets/uswds/_variables" as *;
            @use 'include-media/dist/include-media' as *;
            ```

### 8. Fix test dependencies
Because of node runtime vs. browser runtime issues for certain packages, may get the following error: `Must use import to load ES Module`

Jest must be configured to ignore the es5 versions of some things. Add the following to the `jest` section of `package.json`
```json
"transform": {},
"moduleNameMapper": {
    "^axios$": "axios/dist/node/axios.cjs",
    "@uswds/uswds/src/js/components": "@uswds/uswds/packages/uswds-core/src/js/index.js",
    "\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$": "jest-transform-stub"
}
```


In `package.json`, update the `test` script to prepend the following to the `react-scripts test` command
```
"NODE_OPTIONS=\"$NODE_OPTIONS --experimental-vm-modules\"
```

e.g.
```json
"test": "NODE_OPTIONS=\"$NODE_OPTIONS --experimental-vm-modules\" react-scripts test",
```

### 9. Replace `file-type` library (node runtime) with `file-type-checker` (browser runtime)

Due to the browser runtime vs. node runtime conflict, the `file-type` library (requires the node runtime) is no longer compatible with our project. The following errors were presented:
    * `Must use import to load ES Module`
    * `Cannot find module 'strtok3/core' from 'node_modules/file-type/core.js'`

We will replace `file-type` with the browser-compatible `file-type-checker` ([file-type-checker](https://github.com/nir11/file-type-checker))

1. Remove the `file-type` line from `package.json`'s `dependencies` section.
2. Run
    ```bash
    npm i file-type-checker --save
    ```

* It may be required to delete the `node_modules` folder, then run `npm i` again (if you have cache issues)
* Implementation for this library was slightly different than `file-type`. Consult documentation

### 10. Fix tests

A number of imports needed to be updated in test files. Otherwise, the only major issue was with the `IdleTimer` tests, which simply needed to handle timers differently, and focus the element before continuing the test.

```javascript
jest.useFakeTimers()
let start = Date.now()

// pre-timeout test code

React.act(() => {
    jest.setSystemTime(start + 1200000) // replaces jest.runAllTimers() which wasn't working in this case
    fireEvent.focus(document) // required to apply the new time
})

// post-timeout test code

jest.useRealTimers()
```

Also in these tests, `act()` in tests becomes `React.act()` to address the following deprecation warning
```
ReactDOMTestUtils.act is deprecated in favor of React.act. Import act from react instead of react-dom/test-utils
```

### Follow-on work

The following issues (mostly deprecations) were identified and not resolved. Follow-up tickets should be created for this work.

1. Security vulnerabilities
    * Running `npm audit` results in the following
        ```bash
        37 vulnerabilities (19 moderate, 17 high, 1 critical)
        ```
2. Frontend deprecations
    * Default props deprecated (warning)
        ```
        Warning: STTComboBox: Support for defaultProps will be removed from function components in a future major release. Use JavaScript default parameters instead.
        ```
    * Span not allowed as table child - warning
        ```
        Warning: validateDOMNesting(...): <span> cannot appear as a child of <table>.
        ```
    * Router deprecation
        ```
        React Router Future Flag Warning: Relative route resolution within Splat routes is changing in v7. You can use the `v7_relativeSplatPath` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath.
        ```
2. Test library deprecations
    * wrapper.find
        ```
        Warning: findDOMNode is deprecated and will be removed in the next major release. Instead, add a ref directly to the element you want to reference. Learn more about using refs safely here: https://reactjs.org/link/strict-mode-find-node
        ```
    * redux configureStore
        ```
        The signature '(middlewares?: Middleware<{}, any, Dispatch<AnyAction>>[] | undefined): MockStoreCreator<any, {}>' of 'configureStore' is deprecated.
        ```
3. SASS deprecations
    * USWDS v3 still contains a number of references to deprecated SASS modules. These happen when webpack compiles the SASS. 
        ```bash
        <w> Deprecation color.lightness() is deprecated. Suggestion:
        <w> 
        <w> color.channel($color, "lightness", $space: hsl)
        <w> 
        <w> More info: https://sass-lang.com/d/color-functions
        <w> 
        <w> node_modules/@uswds/uswds/packages/uswds-core/src/styles/mixins/helpers/checkbox-and-radio-colors.scss 68:5  -checkbox-and-radio-colors()
        <w> node_modules/@uswds/uswds/packages/uswds-core/src/styles/mixins/helpers/checkbox-and-radio-colors.scss 12:3  checkbox-colors()
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/src/styles/_usa-checkbox.scss 5:1                            @forward
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/src/styles/_index.scss 4:1                                   @forward
        <w> node_modules/@uswds/uswds/packages/usa-checkbox/_index.scss 8:1                                              @forward
        <w> node_modules/@uswds/uswds/packages/uswds-form-controls/_index.scss 4:1                                       @forward
        <w> node_modules/@uswds/uswds/packages/uswds/_index.scss 51:1                                                    @forward
        <w> src/index.scss 3:1                                                                                           root stylesheet
        <w> 445 repetitive deprecation warnings omitted.
        ```
    * USWDS will need to be updated again at some point, once these are resolved - https://github.com/uswds/uswds/issues/6213
4. Remove customizations in `src/assets/uswds/_uswds-theme-general.scss` that are duplicates of the existing defaults
    * The defaults are listed in the [v3 migration guide](https://designsystem.digital.gov/documentation/migration/#5-update-to-sass-module-syntax-2)
5. Can utilize `fetch`, remove `axios`
6. A11y compliance has not been evaluated for this upgrade. Follow-on work may be necessary to bring us back into compliance.

## Affected Systems
Most of the frontend is affected by this change, but especially
* USWDS styles and components
* File type check when uploading data files
* Unit tests

## Use and Test cases to consider
1. Test the file upload feature thoroughly, including allowed and disallowed file types (extensions and signatures), search form behavior, modals, etc.
2. A11y compliance has not yet been evaluated; test with screenreaders and other a11y tools.