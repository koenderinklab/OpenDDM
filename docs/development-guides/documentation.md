# Documentation with Sphinx

We use Sphinx to generate the documentation for the project. For a general introduction into sphinx, please check out the following resources: 
- [Code Refinery lesson on documentation](https://coderefinery.org/documentation/)
- [quick start guide](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [tutorial](https://www.sphinx-doc.org/en/master/tutorial/index.html)
- [sphinx syntax](https://pythonhosted.org/an_example_pypi_project/sphinx.html)

## Updating the documentation
All documentation that sphinx needs to parse, should stored in the `/docs` folder. The documentation itself can be of `.rst` or `.md` format. All files to be included in the documentation need to be listed in the file `index.rst`. This file also generates the table of contents. Simple add a new `.rst` or `.md` file in the `sphinx` folder (or any subfolder) and add a link to it in `index.rst`.

The API references are generated with [sphinx-autosummary](https://www.sphinx-doc.org/en/master/usage/extensions/autosummary.html). This project follows the [Numpy style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html#example-numpy) for writing docstrings. 

The API references are build from the file `docs/api.rst`. This file contains the instructions for sphinx to retrieve all the docstrings from the functions within each of the modules in the project. The resulting documentation is stored in the (temporary) folder `docs/_autosummary`. 

We use the solution in this [StackOverflow solution](https://stackoverflow.com/questions/2701998/sphinx-autodoc-is-not-automatic-enough/62613202#62613202) to set up recursive generation of the api documentation.

## Sphinx configuration
Sphinx is configuration can be found in the file `docs/conf.py`. Here, you can add additional features through [extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html) or change the [theme](https://sphinx-themes.org/). Note, you might need to install the extensions or themes with pip. If so, please add them as dependencies in `setup.cfg` under the development dependencies.

## Building the documentation locally
If you want to view the documentation locally on your own system, please install the openddm package with its development dependencies with

```bash
pip install -e .[dev]
```
It is also recommended (but not required) to install [Make](https://coderefinery.org/installation/make/).

You can build the documentation locally using Make with 

```bash
cd docs/
make html
```

or without Make with

```bash
sphinx-build ./docs _build

```

You can then view the documentation by opening the file `docs/_build/html/index.rst` in a webbrowser.

## Automatically publish a documentation website
We have set up a GitHub action to build and publish the documentation when we push a new commit to the master branch. The workflow can be found in [`.github/workflows/CI_pages.yml`](https://github.com/koenderinklab/OpenDDM/blob/master/.github/workflows/CI_pages.yml) and the webpage at https://koenderinklab.github.io/OpenDDM/. 

Publishing documentation as a website is handled by GitHub with [GitHub pages](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site). In the settings of the repository, under the tab `pages`, we have pointed GitHub to the branch `gh-pages` to find the (sphinx-build) documentation. When the `CI_pages` action is run, it will build the documentation with sphinx and push the changes to the branch `gh-pages`. GitHub will then update the webpages accordingly. 
