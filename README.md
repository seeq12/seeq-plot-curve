# Plot Curve 

Plot Curve is a Seeq Add-On for fitting curves to tabular data, and pushing the resulting formulas to Seeq Workbench.

![drawing](https://github.com/seeq12/seeq-plot-curve/blob/main/_static/plot-curve-screenshot.png?raw=true)
----
# Installation

### User Installation Requirements (Seeq Data Lab)
If you want to install **seeq-plot-curve** as a Seeq Add-on Tool, you will need a version of Seeq Data Lab:

- Seeq Data Lab (> R50.5.0, >R51.1.0, or >R52.1.0)
- Seeq module whose version matches the Seeq server version, and the version of SPy >= 182.25
- Seeq server admin access

### User Installation (Seeq Data Lab)
1. Create a **new** Seeq Data Lab project, and open the terminal window.
2. Run pip install seeq-plot-curve
3. Run python -m seeq.addons.plot_curve [--users <users_list> --groups <groups_list>].  During the installation you will
   be prompted for your username/password (an access key can also be used).  It will also prompt for the url of the
   app notebook which will be available from the deployment folder in Seeq Data Lab.
4. Verify that the Plot Curve add-on is present in the AddOn menu in workbench.

### Source Installation

For development work, it is highly recommended creating a python virtual environment and install the package in that
working environment. If you are not familiar with python virtual environments, you can take a
look [here](https://docs.python.org/3.8/tutorial/venv.html)

Once your virtual environment is activated, you can install **seeq-plot-curve** from source with:

```shell
python setup.py install
```

----

# Development

We welcome new contributors of all experience levels.

- Official Source code repository : https://github.com/seeq12/seeq-plot-curve
- Issue tracker : https://github.com/seeq12/seeq-plot-curve/issues

You can get started by cloning the repository with the command : 
```sh
$ git clone git@gitub.com:seeq12/seeq-plot-curve.git
```

There is a template for the developer notebook in /development.  To get started, copy it to the root directory, create a new
virtual environment and install the requirements.

```sh
$ cp ./development/developer_notebook.ipynb developer_notebook.ipynb
$ pip install -r requirements.txt 
```

Next, modify the parameters within the workbook for your local environment (username, password, workbook, worksheet, etc.).
Finally, start a jupyter server and navigate to the development notebook in the root directory.

```sh
$ jupyter notebook
```

# Important links

* Official source code repo: https://github.com/seeq12/seeq-plot-curve
* Issue tracker (bugs, feature requests, etc. ) : https://github.com/seeq12/seeq-plot-curve/issues

----

# Citation

Please cite this work as:

```shell
seeq-plot-curve
Seeq Corporation, 2021
https://github.com/seeq12/seeq-plot-curve
```

