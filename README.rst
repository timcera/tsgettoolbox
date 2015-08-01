TSgettoolbox - Quick Guide
==========================
TSgettoolbox will work with Python 2.6+ and 3.0+.

Documentation
-------------
Reference documentation is at http://pythonhosted.org/tsgettoolbox/

Installation
------------
At the command line::

    $ pip install tsgettoolbox
    # OR
    $ easy_install tsgettoolbox

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv tsgettoolbox
    $ pip install tsgettoolbox

Usage - Command Line
--------------------

tsgettoolbox get_station NWIS,02245600 EPA,9499939

Station,Parameter,Start_date,End_date
NWIS:02245600,water_level,2000-01-01,2010-09-30
NWIS:02245600,water_level,2000-01-01,2010-09-30
EPA:9499939,water_level,1990-01-01,2001-08-09
EPA:9499939,ddt,1990-01-01,2001-08-09

tsgettoolbox get_data NWIS,02245600,water_level EPA,9499939,

Datetime,NWIS_02245600_water_level,EPA_9499939_water_level,EPA_9499939_ddt
1990-01-01,,4.5,0.0045
1990-01-02,,4.52,0.005
...

Usage - Python Library
----------------------
To use TSgettoolbox in a project::

	from tsgettoolbox import tsgettoolbox

Refer to the API Documentation at http://pythonhosted.org/tsgettoolbox/

Development
~~~~~~~~~~~
Development is managed on bitbucket at
https://bitbucket.org/timcera/tsgettoolbox/overview.
