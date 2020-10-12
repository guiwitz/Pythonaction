# Publishing docs

This is a short guide explaining all the necessary steps to publish documentation for a Python package using Spinx, Jupyter Book, and GitHub, including GitHub-Actions and Github-Pages.

## Software structure

When I write a Python package, I usually only rely on setuptools and a ```setup.py``` file that contains all the necessary information for packaging. Instructions can be found [here](https://packaging.python.org/tutorials/packaging-projects/). Note that in the future, ```setup.py``` will be replaced by setting all information in a ```setup.cfg``` file (see [here](https://setuptools.readthedocs.io/en/latest/userguide/quickstart.html) for example).

## Writing docs

There are multiple ways of writing documentation for software. My personal preference is the [Numpy style](https://numpydoc.readthedocs.io/en/latest/format.html) documentation. It is important to follow the correct syntax so that automatic documentation tools like Sphinx can then parse the information. Here's just a quick example for a function:

```python
def my_function(a):
    """
    This is my function.

    Parameters
    ----------
    a: 2d array
        This is my array.

    Returns
    -------
    b: 2d array

    """

    b = 3 * a
    return b
```

## Creating the docs

The following guide is a shortened version of [this excellent Medium post](https://medium.com/better-programming/auto-documenting-a-python-project-using-sphinx-8878f9ddc6e9).

The main tool used to create the docs is Sphinx. It has to be installed using e.g.: 

```
pip install sphinx
```

When pointed to a package, Sphinx can discover all modules and parse the content of their docs. For a given project, we first need to initialize some Sphinx files. In our project we create a ```docs``` folder and from there we use: 

```
sphinx-quickstart
```

Answer the three questions (this information can also be updated later). Make sure you say ```y``` when asked about separating source and build. Now you should have a few files in the ```docs/source``` folder. Most importantly, you should have a ```conf.py``` file. This file needs to be completed:

1. Add these lines so that the package (situated two levels higher) is discoverable:
   ```
   import os
   import sys
   sys.path.insert(0, os.path.abspath('../..'))
   ```
2. So that Sphinx can automatically parse code documentation, it needs additional plugins. Add this information to the file:
   ```
   extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
    ]
    ```

Now we can let Sphinx parse the information from our package. In the terminal move to the level of the package folder and use:
```
sphinx-apidoc -o docs/source pythonaction/
```

(where of course you replace the package name). This generates two ```.rst``` files that describe the contents of the documentation.

## Generating the HTML

From this point, we could simply use Sphinx to generate the HTML from the above collected information. Instead of that, in order to include richer information, we include the docs in a Jupyter Book format. Under the hood, Jupyter Nook uses Sphinx to generate the HTML but it does it transparently for us. 

What we need to do now is to setup the Jupyter Book project. First we need to install the package: 

```
pip install jupyter-book
```

We only need to add two files to to base of our project: a ```_config.yml``` file that contains settings for our project and ```_toc.yml``` file that defines the contents of the book. You can find detailed information [here](https://jupyterbook.org/start/overview.html#anatomy-of-a-jupyter-book). In this project, ```_config.yml``` file is:

```
# Book settings
title: Pythonaction documentation
author: Guillaume Witz

sphinx:
  extra_extensions: [
  'sphinx.ext.autodoc',
  'sphinx.ext.napoleon'
  ]
```

(the spinx information might be redundant with that entered in the Sphinx configuration file).

The table of contents file ```_toc.yml``` is:
 
```
- file: docs/introd
- file: docs/notebook
- file: docs/source/modules
```

i.e. it includes the ```docs/introd.md``` Markdown file, the ```docs/notebook.ipynb``` Jupyter notebook and the ```docs/source/modules.rst``` restructured file. Note that the latter file is the one we previously  created using Sphinx and which will include our entire automated docs in the final document. Finally we can generate our HTML using:

```
jupyter-book build .
```

from within our project base. Now you can open your webpage by opening ```_build/html/index.html```.

## Publishing on GitHub

To automatically update and publish the documentation, we need to use GitHub-Actions and GitHub-Pages. The information that we have to include in our repository is:

- the ```_config.yml``` and ```_toc.yml``` files
- the contents of the ```docs/source``` folder (```conf.py```, ```make.bat```, ```Makefile```)
- Any document that we added in the ```docs``` folder with content we want to publish (e.g. a Jupyter notebook).

### GitHub actions with conda

Now that we have all the required files in our repository, we want to automatically update the documentation when we change the package or change the contents when we modify the ```_toc.yml``` file. This should happen every time we do a push to the repository. This can be achieved by using GitHub-Actions, i.e. scripts that are triggered to run on the repository every time some event (such as a push) happens.

The action is mostly copied from Jupyter Book (see [here](https://jupyterbook.org/publish/gh-pages.html#automatically-host-your-book-with-github-actions)) with a few modifications and it looks like this:

 ```
 name: deploy-book

# Only run this when the master branch changes
on:
  push:
    branches:
    - master

# This job installs dependencies, build the book, and pushes it to `gh-pages`
jobs:
  deploy-book:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    # Install dependencies
    - name: Set up Python 3.7
      uses: actions/setup-python@v1
      with:
        python-version: 3.7

    # Install conda dependencies
    - name: Install dependencies
      run: |
        # $CONDA is an environment variable pointing to the root of the miniconda directory
        $CONDA/bin/conda env update --file environment.yml --name base
    
    # Install pip dependencies
    - name: Install dependencies
      run: |
        $CONDA/bin/pip install -r requirements.txt

    # Show packages
    - name: Show packages
      run: |
        $CONDA/bin/conda list

    # Compile the docs
    - name: Compile sphinx
      run: |
        $CONDA/bin/sphinx-apidoc -o docs/source pythonaction/
    
        # Build the book
    - name: Build the book
      run: |
        $CONDA/bin/jupyter-book build .
    
    # Push the book's HTML to github-pages
    - name: GitHub Pages action
      uses: peaceiris/actions-gh-pages@v3.5.9
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./_build/html
```

As indicated, the action runs on a Ubuntu machine (```runs-on: ubuntu-latest```) and executes the list of ```steps``` described. In the regular GitHub-Action, necessary packages, in particular ```jupyter-book```, are installed via a ```requirements.yml``` file. If we want to be able to execute notebooks that use our package as demo, we need to include all dependencies for our package (```pythonaction```) in the file as well. As I usually prefer to use conda to install dependencies via an ```environment.yml``` file, I modified the action in that perspective. First I "Install conda dependencies". This has to be done in the (base) environment as it is hard (impossible?) to activate an other one in Gtihub-Actions. Once this is done, I also install the ```jupyter-book``` dependencies using the ```requirements.yml``` file.

```{note}
Note that we use ```$CONDA/bin/pip install -r requirements.txt``` instead of the simple ```$pip install -r requirements.txt```. The reason for that is that we want to use the (base) conda environment and not the default Python installation. Otherwise, ```jupyter-book``` won't have access to our package that we installed via conda.
```

What also differs from the standard action, is that we then create the docs via Sphinx in the next block. This ensures that our docs are always up-to-date. Finally we compile the book (still via conda) and push the result to the gh-pages branch.

### GitHub Pages

GitHub offers an automated mechanism to host a static web site. Whenever folder structure typical of a web-site is pushed to a branch of the repository **specifically** called ```gh-pages```, it will be accessible at an address of the type https://guiwitz.gtihub.io/Pythonaction (with your user name and project name). The last action in our GitHub-Action script does exactly that: push our docs built with Jupyter-book to a ```gh-pages``` branch.