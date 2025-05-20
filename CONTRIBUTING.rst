===========================
Contributing to Pan3D
===========================

#. Clone the repository using ``git clone``
#. Install pre-commit via ``pip install pre-commit``
#. Run ``pre-commit install`` to set up pre-commit hooks
#. Make changes to the code, and commit your changes to a separate branch
#. Create a fork of the repository on GitHub
#. Push your branch to your fork, and open a pull request

Tips
##########################################################

#. When first creating a new project, it is helpful to run ``pre-commit run --all-files`` to ensure all files pass the pre-commit checks.
#. A quick way to fix ``ruff`` issues is by installing black (``pip install ruff``) and running the ``ruff format`` and ``ruff check`` command at the root of your repository.
#. A quick way to fix ``codespell`` issues is by installing codespell (``pip install codespell``) and running the ``codespell -w`` command at the root of your directory.
#. The `.codespellrc file <https://github.com/codespell-project/codespell#using-a-config-file>`_ can be used fix any other codespell issues, such as ignoring certain files, directories, words, or regular expressions.

Release process and commit messages
##########################################################

Releases are automatically produced based on the commits that are merged into master.
We rely on semantic-release to tag releases and produce CHANGELOG.md.
To support that automated process, you need to follow `that convention on your commit messages <https://semantic-release.gitbook.io/semantic-release#how-does-it-work>`_.
