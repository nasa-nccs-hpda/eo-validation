=============
eo-validation
=============

.. image:: https://github.com/nasa-nccs-hpda/eo-validation/actions/workflows/lint.yml/badge.svg
        :target: https://github.com/nasa-nccs-hpda/eo-validation/actions/workflows/lint.yml

**Earth Observation Validation Tool for Individuals and Teams**

* GitHub repo: https://github.com/nasa-nccs-hpda/eo-validation
* Documentation: https://nasa-nccs-hpda.github.io/eo-validation

**Contents**

- `Objectives`_
- `Installation`_
- `Contributing`_
- `Contributors`_
- `References`_

Objectives
------------

- Platform for collaborative validation of remotely sensed data
- Infrastructure to support multi-tenant visualization of moderate to very-high resolution data
- Interactive dashboard for data and validation analysis

Installation
------------

The following library is intended to be used to accelerate the development of validation products
for remote sensing satellite imagery, or any other applications. eo-validation can be installed
by itself, but instructions for installing the full environment are listed under the requirements
directory so projects, examples, and notebooks can be run.

The original implementation of this tool was implemented with the cloud-based DaskHub environment 
in mind, but additional guidance and installation scripts are provided to support the portability
of the tool on commodity-based and on-premises environments.

**eo-validation** is available on `PyPI <https://pypi.org/project/eo-validation/>`__. To install **eo-validation**, run this command in your terminal:

.. code:: python

  pip install eo-validation


**eo-validation** is also available on `conda-forge <https://anaconda.org/conda-forge/eo-validation>`__.
If you have `Anaconda <https://www.anaconda.com/distribution/#download-section>`__ or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`__ 
installed on your computer, you can create a conda Python environment to install eo-validation:

.. code:: python

  conda create -n eo-validation-env python=3.9
  conda activate eo-validation-env
  conda install geopandas
  conda install -c conda-forge mamba
  mamba install -c conda-forge eo-validation localtileserver

Optionally, you can install `Jupyter notebook extensions <https://github.com/ipython-contrib/jupyter_contrib_nbextensions>`__,
which can improve your productivity in the notebook environment. Some useful extensions include Table of Contents, Gist-it,
Autopep8, Variable Inspector, etc. See this `post <https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231>`__
for more information.       

.. code:: python

  conda install jupyter_contrib_nbextensions -c conda-forge 


If you have installed **eo-validation** before and want to upgrade to the latest version, you can run the following command in your terminal:

.. code:: python

  pip install -U eo-validation


If you use conda, you can update eo-validation to the latest version by running the following command in your terminal:
  
.. code:: python

  conda update -c conda-forge eo-validation

Contributing
------------

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Report Bugs
^^^^^^^^^^^

Report bugs at https://github.com/nasa-nccs-hpda/eo-validation/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
^^^^^^^^

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
^^^^^^^^^^^^^^^^^^

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
^^^^^^^^^^^^^^^^^^^

eo-validation could always use more documentation, whether as part of the
official eo-validation docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
^^^^^^^^^^^^^^^

The best way to send feedback is to file an issue at https://github.com/nasa-nccs-hpda/eo-validation/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Contributors
------------

* Jordan A. Caraballo-Vega, jordan.a.caraballo-vega@nasa.gov
* Caleb S. Spradlin, caleb.s.spradlin@nasa.gov

References
------------

`leafmap <https://github.com/opengeos/leafmap>`_
