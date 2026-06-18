# Test Conversion

> *There are critical, non-obvious patterns for converting UI5 test code from JavaScript to TypeScript. Standard ES6 module/class conversions and renaming of files to `*.ts` also applies, like for regular application code and controls.*

NOTE: The test code file related changes below (especially those for OPA tests) always apply when converting the tests to TypeScript, but the test setup and running (like in `testsuite.qunit.ts`) may depend on how exactly the tests are set up in the project.

Test conversion should only happen once the rest of the application has been converted successfully.

## Explicit QUnit Import Required

Unlike JavaScript where QUnit is often used as a global, TypeScript requires explicit import:

```typescript
import QUnit from "sap/ui/thirdparty/qunit-2";
```

## Test Registration in testsuite.qunit.ts

The testsuite configuration uses plain `export default` (no sap.ui.define wrapper):

```typescript
export default {
    name: "Testsuite for the com/myorg/myapp app",
    defaults: {
        page: "ui5://test-resources/...",
        loader: {
            paths: {
                "com/myorg/myapp": "../",
                "integration": "./integration",
                "unit": "./unit"
            }
        }
    },
    tests: {
        "unit/unitTests": { title: "..." },
        "integration/opaTests": { title: "..." }
    }
};
```

## tsconfig.json Path Mappings for Tests

**Essential**: Add path mappings and QUnit types (like in this sample, but adapt to the specific app which is converted):

```json
{
    "compilerOptions": {
        "types": ["@sapui5/types", "@types/qunit"],
        "paths": {
            "com/myorg/myapp/*": ["./webapp/*"],
            "unit/*": ["./webapp/test/unit/*"],
            "integration/*": ["./webapp/test/integration/*"]
        }
    }
}
```

## OPA Integration Tests - Fundamental Architecture Change

JavaScript Pattern (OLD) - NOT USED IN TYPESCRIPT:

```javascript
sap.ui.define(["sap/ui/test/opaQunit", "./pages/App"], (opaTest) => {
    opaTest("should add an item", (Given, When, Then) => {
        Given.iStartMyApp();
        When.onTheAppPage.iEnterText("test");
        Then.onTheAppPage.iShouldSeeItem("test");
        Then.iTeardownMyApp();
    });
});
```

TypeScript Pattern (NEW) - MUST BE USED:

```typescript
import opaTest from "sap/ui/test/opaQunit";
import AppPage from "./pages/AppPage";
import QUnit from "sap/ui/thirdparty/qunit-2";

const onTheAppPage = new AppPage();

QUnit.module("Test Module");

opaTest("Should open dialog", function () {
    onTheAppPage.iStartMyUIComponent({
        componentConfig: { name: "ui5.typescript.helloworld" }
    });
    
    onTheAppPage.iPressButton();
    onTheAppPage.iShouldSeeDialog();
    onTheAppPage.iTeardownMyApp();
});
```

Critical Rules:
1. **NO Given/When/Then parameters** in the opaTest callback
2. **Create page instances BEFORE tests**: `const onTheAppPage = new AppPage();`
3. **Call all methods directly on the page instance** (arrangements, actions, assertions, cleanup)

## OPA Page Objects - Class-Based Only

JavaScript uses createPageObjects() - DO NOT USE IN TYPESCRIPT

TypeScript uses classes extending Opa5:

```typescript
import Opa5 from "sap/ui/test/Opa5";
import Press from "sap/ui/test/actions/Press";

const viewName = "ui5.typescript.helloworld.view.App";

export default class AppPage extends Opa5 {
    iPressButton() {
        return this.waitFor({
            id: "myButton",
            viewName,
            actions: new Press(),
            errorMessage: "Did not find button"
        });
    }
    
    iShouldSeeDialog() {
        return this.waitFor({
            controlType: "sap.m.Dialog",
            success: function () {
                Opa5.assert.ok(true, "Dialog is open");
            },
            errorMessage: "Did not find dialog"
        });
    }
}
```

Key Points:
- **NO createPageObjects()** - use ES6 class extending Opa5
- **NO separation** between actions and assertions objects. They are regular class methods
- All lifecycle methods (iStartMyUIComponent, iTeardownMyApp) are inherited from Opa5

## Arrangements Pattern - Eliminated

DO NOT create separate Arrangements classes in TypeScript.

JavaScript often uses:
```javascript
sap.ui.define(["sap/ui/test/Opa5"], (Opa5) => {
    return Opa5.extend("namespace.Startup", {
        iStartMyApp() { this.iStartMyUIComponent({...}); }
    });
});
```

TypeScript eliminates this - call `iStartMyUIComponent()` directly on the page instance in the journey.

## OPA Test Registration (opaTests.qunit.ts)

JavaScript typically has:
```javascript
sap.ui.define(["sap/ui/test/Opa5", "./arrangements/Startup", "./Journey1"], (Opa5, Startup) => {
    Opa5.extendConfig({ arrangements: new Startup(), autoWait: true });
});
```
TypeScript simplifies to:
```typescript
// import all your OPA tests here
import "integration/HelloJourney";
```

No Opa5.extendConfig() needed, just import the journeys.

## Code Coverage in case of using `ui5-test-runner`

If (and only if!) the tests are set up using the `ui5-test-runner` tool, then the app must be started with a specific `ui5-coverage.yaml` configuration. Suitable `package.json` scripts may look like this:

```
    "start-coverage": "ui5 serve --port 8080 --config ui5-coverage.yaml",
    ...
    "test-runner-coverage": "ui5-test-runner --url http://localhost:8080/test/testsuite.qunit.html --coverage -ccb 60 -ccf 100 -ccl 80 -ccs 80",
    "test-ui5": "ui5-test-runner --start start-coverage --url http://localhost:8080/test/testsuite.qunit.html --coverage -ccb 60 -ccf 100 -ccl 80 -ccs 80",
```

The `test-runner-coverage` script expects `start-coverage` to be executed manually, `test-ui5` does it automatically.

When adding such scripts, explain them to the user!

The `ui5-coverage.yaml` file must configure the `ui5-tooling-transpile-middleware` like this by adding the `babelConfig`:

```yaml
...
server:
  customMiddleware:
    - name: ui5-tooling-transpile-middleware
      afterMiddleware: compression
      configuration:
        debug: true
        babelConfig:
          sourceMaps: true
          ignore:
          - "**/*.d.ts"
          presets:
          - - "@babel/preset-env"
            - targets: defaults
          - - transform-ui5
          - "@babel/preset-typescript"
          plugins:
          - istanbul
    - name: ui5-middleware-livereload
      afterMiddleware: compression
```

In this case, the `babel-plugin-istanbul` package must be added as dev dependency! (The other packages in the config are already required by `ui5-tooling-transpile`).
