# PyPI Analyser

This repository contains a set of Python scripts and Jupyter Notebooks. Their purpose is to ~~gather~~(see [Difficulties Encountered](dif)) and process data into a normalized format. This data will be used in the creation of a [time dependent graph structure for dependencies](https://github.com/AJMBrands/SoftwareThatMatters).

### Note
The `analyser_big_query` and `analyser_big_query_pandas` files were used as a more of a playground for exploring data. 
The `analyser_big_query_python` and `analyser_repology` represent the real processing that will be applied to the data. These might
be converted into their own script at a later date. Currently, there is no implementation to automatically acquire the data.
Please check out the [Explored Datasets](explored) to find the sources used.

# <a name="explored"> Explored Datasets
- [Libraries.io](https://libraries.io/)
- [An Analysis of Dependency Network Evolution in PyPI - Zenodo](https://zenodo.org/record/2620607)
- [Project Metadata Table - Google BigQuery](https://console.cloud.google.com/bigquery?project=the-psf&page=dataset&d=pypi&p=the-psf&redirect_from_classic=true) - a Google account is required
- [PyPI package metadata cache](https://pypicache.repology.org/)

# <a name="dif">Difficulties Encountered

The first attempt was to gather data directly from PyPI using their [JSON API](https://warehouse.pypa.io/api-reference/json.html). 
To achieve this, a call to their [Simple API](https://warehouse.pypa.io/api-reference/legacy.html#simple-project-api) needed to 
be made first to get a list of all the projects hosted on the repository. Next, I would need to call each project endpoint to 
get metadata about its dependencies. A part of the needed code can still be found in this repository. 

This attempt was stopped in its tracks quite early on when I discovered that the [robots.txt]( https://pypi.org/robots.txt) file 
(it specifies a set of rules for robots interacting with the site) provided by PyPI disallows automated requests to the needed endpoints.