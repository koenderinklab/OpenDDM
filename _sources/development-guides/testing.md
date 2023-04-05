# Testing

>“Before relying on a new experimental device, an experimental scientist always establishes its accuracy. A new detector is calibrated when the scientist observes its responses to known input signals. The results of this calibration are compared against the expected response.”

Simulations and analysis using software should be held to the same standards as experimental measurement devices!

For a more in depth introduction with motivation on writing tests, see the [lesson on testing](https://coderefinery.github.io/testing/motivation/) from the Code Refinery.

Type of tests:
* **Unit test**: testing of individual units of source code (scripts, functions, classes).
* **Integration test**: testing of a combination of individual units as a group.
* **Regression test**: re-running all tests to ensure that the previously developed and tested code still performes after a code change.

## Executing tests
We will use the `pytest` package to run our tests in Python. The real advantage of pytest comes by writing concize test cases. `pytest` test cases are a series of functions in a Python file starting with the name `test_`. Additional documentation on `pytest` can be found [here](https://docs.pytest.org/en/7.1.x/).

All our tests can be found in the folder `/tests`. After you have installed the openddm package with development dependencies with 

```bash
pip install -e .[dev]
```

you can execute the available tests with the following command in the root of the repository:
```bash
pytest --cov
```
This will execute all tests and generate a code coverage report in the terminal.

## Writing tests
We use the following naming convention for out tests. The name of the test file should be the name as the function you want to test, prefixed by `test_` and saved in the folder `/tests`. Pytest will automatically recognize all tests with this convention. Each test file will contain multiple test functions that each test a different aspect of the function we would like to test. 

For example, if we want to write tests for the function `sum`, we can check whether it is capable of handling both lists and tuples as input data type with:

```
def test_sum():
    assert sum([1, 2, 3]) == 6, "Should be 6"

def test_sum_tuple():
    assert sum((1, 2, 3)) == 6, "Should be 6"

```

The general skeleton of a tests will follow:
1. Define test parameters, e.g. input arguments for the function you want to test
1. Set expected result
1. Execute function to produce actual result
1. Compare expected and actual result with an `assert` statement

## Automating testing
We have set up a GitHub Action to automatically run all the tests when a pushing changes to GitHub and upon opening a pull request. The workflow can be found in the folder `./github/workflows/CI_build.yml`. For more information on GitHub Actions for running tests, have a look at https://docs.github.com/en/actions/guides/building-and-testing-python.

## Code coverage
Code coverage establishes the percentage of code under tests. A good goal would be to have at least 70% of the code base under unit testing. To make inspection of the coverage easy, we are using the online service [Codecov](https://about.codecov.io/). Whenever we (automatically) run the tests with GitHub actions, the results will be uploaded to Codecov and made available at https://app.codecov.io/gh/koenderinklab/ddmPilotCode/. At the bottom of the page, you can look through the codebase and check which parts are currently covered by tests.  

Additionally, Codecov will produce coverage reports in pull requests for a quick check of the tests.

### Resources
- https://realpython.com/python-testing/ 
- https://realpython.com/pytest-python-testing/
- https://www.tutorialspoint.com/pytest/pytest_quick_guide.htm
- https://docs.pytest.org/en/6.2.x/goodpractices.html
