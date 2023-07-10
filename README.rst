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
- `Infrastructure`_
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

  conda create -n eo-validation-env jupyter ipysheet leafmap geopandas localtileserver rioxarray --channel anaconda --channel conda-forge
  conda activate eo-validation-env
  pip install eo-validation

Optionally, you can install `Jupyter notebook extensions <https://github.com/ipython-contrib/jupyter_contrib_nbextensions>`__,
which can improve your productivity in the notebook environment. Some useful extensions include Table of Contents, Gist-it,
Autopep8, Variable Inspector, etc. See this `post <https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231>`__
for more information.       

.. code:: python

  conda install jupyter_contrib_nbextensions -c conda-forge 


If you have installed **eo-validation** before and want to upgrade to the latest version, you can run the following command in your terminal:

.. code:: python

  pip install -U eo-validation

Infrastructure
--------------

The eo-validation package is a set of Jupyter-based notebooks to manage and structure the validation of remote sensing data.
The validation notebooks can be run Individually and/or via a Team of observers.

The **Individual** option assumes that a single observer will be performing the entire validation. This will generate a single
database for the observer. The **Team** option assumes that multiple observers will evaluate each point in the database, being
the end output an aggregated database that includes the points of all the observers.

The core validation procedures followed by this notebook rely on the
`Oloffson Best Practices method <https://reddcr.go.cr/sites/default/files/centro-de-documentacion/olofsson_et_al._2014_-_good_practices_for_estimating_area_and_assessing_accuracy_of_land_change.pdf>`_.
The main requirements are a **data file** in GeoTIFF format, and a **mask file** in GeoTIFF format. This data file
will be used for visual interpretation. The mask file will be used to perform a stratified random sampling of points per
mask class. If the mask file is not present, a completely random set of points will be generated for each data file.

Individual Validation Quickstart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the Validation Dashboard

.. code:: python

  wget https://raw.githubusercontent.com/nasa-nccs-hpda/eo-validation/main/notebooks/ValidationDashboard.ipynb

Then, open the validation notebook from a Jupyter interface. You will need to modify several arguments from the validation
dashboard in order to successfully point to the necessary directories and paths. An example is listed below:

.. code:: python

  from IPython.display import display
  from eo_validation.validation_dashboard import ValidationDashboard

  dashboard = ValidationDashboard(
      center=[14, -14]
  )
  display(dashboard)

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
