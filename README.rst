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
- `Examples`_
- `Best Practices`_
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

**eo-validation** is available on `PyPI <https://pypi.org/project/eo-validation/>`__.
To install **eo-validation**, run this command in your terminal:

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

Examples
--------------

Individual Validation Quickstart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the Validation Dashboard

.. code:: python

  wget https://raw.githubusercontent.com/nasa-nccs-hpda/eo-validation/main/notebooks/ValidationDashboard.ipynb

Then, open the validation notebook from a Jupyter interface. You will need to modify several arguments from the validation
dashboard in order to successfully point to the necessary directories and paths. An example is listed below:

.. code:: python

  from ipyleaflet import basemaps
  from IPython.display import display
  from eo_validation.validation_dashboard import ValidationDashboard

  dashboard = ValidationDashboard(
      center=[14, -14],
      zoom=3,
      max_zoom=20,
      default_max_zoom=20,
      default_zoom=18,
      scroll_wheel_zoom=True,
      keyboard=True,
      basemap=basemaps.Esri.WorldImagery,
      height="600px",
      data_dir="/efs/projects/3sl/data/Tappan",
      mask_dir="/efs/projects/3sl/labelsv2",
      output_dir="/home/jovyan/eo-validation-output-test",
      default_bands=[
          ('Coastal Blue', 1),
          ('Blue', 2),
          ('Green', 3),
          ('Yellow', 4),
          ('Red', 5),
          ('Red Edge', 6),
          ('NIR1', 7),
          ('NIR2', 8)
      ],
      rgb_bands = [7, 3, 2],
      rgb_disabled=False,
      validation_classes=[
          'other',
          'trees/shrub',
          'cropland',
          'other vegetation',
          'water',
          'build'
      ],
      mask_classes=[
          'other',
          'tree',
          'crop',
          'burn'
      ],
      points_dir='/home/jovyan/efs/projects/3sl/validation/original_points',
      gen_points=True,
      n_points=200,
      expected_accuracies=[0.90, 0.90, 0.90, 0.90],
      expected_standard_error=0.01,
      product_name='otcb',
      chunks={"band": 1, "x": 2048, "y": 2048}
  )
  display(dashboard)

The arguments from the ValidationDashboard class are as follow:

- **center** (List[int, int]): center location to start map at, default: [14, -14]
- **zoom** (int): zoom value to start map at, default: 3
- **max_zoom** (int): maximum zoom value to perform close up on validation points, default: 20
- **default_max_zoom** (int): default maximum zoom value, default: 20
- **default_zoom** (int): default zoom value, default: 18
- **scroll_wheel_zoom** (bool): enable mouse scroll to perform zoom, default: True
- **keyboard** (bool): enable keyboard options to move across points, default: True
- **basemap** (ipyleaflet.basemap): basemap object from ipyleaflet to use as background, default: basemaps.Esri.WorldImagery
- **height** (str): height of the output map in the Jupyter cell, default: 600px
- **data_dir** (str): directory to point at input data files in GeoTIFF, default: ~/
- **mask_dir** (str): directory to point at mask data files in GeoTIFF; if not available, random points without stratification will be generated, default: ~/
- **output_dir** (str): directory to store output database at, default: ~/eo-validation-output
- **default_bands** (List[tuple]): list of tuples representing band values, default: [('Coastal Blue', 1), ('Blue', 2), ('Green', 3), ('Yellow', 4), ('Red', 5), ('Red Edge', 6), ('NIR1', 7), ('NIR2', 8)]
- **rgb_bands** (List[int]): list of integer bands to use as RGB, default: [1, 2, 3]
- **rgb_disabled** (bool): disable toggling RGB band dropdown, default: False
- **validation_classes** (List[str]): list of validation classes to use, default: ['other', 'trees/shrub', 'cropland', 'other vegetation', 'water', 'build']
- **mask_classes** (List[str]): list of classes to use in the random stratification process, default: ['other', 'tree', 'crop', 'burn']
- **points_dir**: (str): directory where original points are located if they were already generated), default: ~/eo-validation/original_points
- **gen_points** (bool): generate random points on the fly, default: True
- **n_points** (int): number of points to generate if **gen_points** is True, default: 200
- **expected_accuracies** (List[float]): list of expected accuracies for each class following Oloffson method, default: [0.90, 0.90, 0.90, 0.90]
- **expected_standard_error** (float): expected standard error per class, default: 0.01
- **chunks** (dict): data sharding options from xarray, default: {"band": 1, "x": 2048, "y": 2048}

Teams' Validation Quickstart
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The overall workflow is as follows:

#. Upload the data to your system of choice.
#. Create a set of general points for use and locate them in a single directory.
#. Copy the Validation Dashboard notebook under a general directory so observers can choose the notebook.
#. Let the observers perform the validation and aggregate the points at the end of the validation period.

This will allow you to have multiple observers per point for the possibility of more robust uncertainty metrics.

Teams' Validation Example on the Science Managed Cloud Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following is an example workflow using the Science Managed Cloud Environment. Depending on your environment,
you will need to modify some of these steps. If you have been notified that a tutorial environment is already 
generated for you, feel free to skip to step 3.

**1. Setup the working environment - Only done by the Team Administrator**

For this first step we will setup the working directories for your team. In this case we need 3 main directories.
When using the Daskhub system, we have a directory called /home/jovyan, which is your personal home directory. Then
we have the project directory where we will store the data and overall validation files.

To setup this environment, pull the following notebook into your system and run each cell for it to automatically
setup your Daskhub working environment.

.. code:: bash

  wget https://raw.githubusercontent.com/nasa-nccs-hpda/eo-validation/main/notebooks/ValidationEnvironmentSetup.ipynb


**2. Upload the data to your system of choice - Only done by the Team Administrator**

In this step you will need to upload the data you will be using in the validation exercise. In general this will require
you to upload a pair of data (GeoTIFF satellite imagery) and labels (GeoTIFF single band label), and locate them in a 
general location. To upload the data to SMCE, you can use scp from a terminal within Daskhub, or manually uploading the
imagery using Drag and Drop options.

**3. Start working on your environment**

In this step users can start working on their personal notebooks. These notebooks can be accessed by opening the 
ValidationDashboard.ipynb file from your working directory. For example, if you are part of Dr. Peng group, you can
access your personal tutorial notebook under /efs/Bin_UIUC/<your_username>/ValidationDashboard.ipynb.

If you need additional help walking through the notebook, here is a short video on how to get started `YouTube <https://youtu.be/3tG7bQ-10ac>`__.

.. image:: https://img.youtube.com/vi/3tG7bQ-10ac/maxresdefault.jpg
    :alt: eo-validation demo
    :target: https://www.youtube.com/watch?v=3tG7bQ-10ac

Overall Validation Workflow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Close unnecessary tabs in your browser. Make sure you have fast internet connection (>5Mb/s).
#. Login to SMCE daskhub via URL: https://daskhub.dsg.smce.nasa.gov (same user name (GMU NetID) and PW as in Nov 2022) 
#. Receive text and enter verification code (2 factor authentication – will be required each time you log in)
#. Choose “Large Server” from list of resources
#. Open terminal window by clicking on the “terminal” icon in the lower left of the launcher window.  
#. Change directory if not in correct folder: cd /efs/<project_name>/<your_userID> (you can use folders GUI on left)
#. Double click on the Validation tool notebook
#. Use the >> button to run the notebook from the beginning (RESTART Kernel?– click on Restart). Wait a few minutes for mapping window to open below (close any other tabs in your browser) 
#. A following window will open
#. Click on tool icon (spanner) in upper right corner, then folder icon.
#. Click / select/ highlight assigned image from Google list / click Select / new dialogue box click Apply. Select images assigned to you.
#. Click “Apply” in dialogue box below, wait for validation points to be created and image to load.
#. Set map window to full screen
#. Click forward arrow to take you to the first marker / validation point, and automatically zoom in
#. Make your selections, then click “Verified”
#. Click forward arrow to go to next point / marker
#. You may indicate when you are not confident in your selection of cover type.

Best Practices
---------------

#. End session: go to toolbar/file/hub control panel/ stop my server. You need to end the AWS session, otherwise the server stays
active wasting money and project funding. 
#. Finishing and starting up again: If you have completed with one raster image press >> to Restart and select a new image. If you Do 
not restart, it multiple layers will be displayed, causing problems.
#. If your session dies and you were working on an existing number of points, reload your session and reselect the file you were working
on. The notebook will continue where it left. Just click on the right arrow and it will take you to the next point you need to work on.

Contributing
-------------

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
