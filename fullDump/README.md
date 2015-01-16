fullDump
========

Script to collect files harvested via gulo (https://github.com/VertNet/gulo) into BigQuery.

This program dumps a full snapshot of multiple files in Google Cloud storage into a new BigQuery table in the following steps:

1. Creates the 'dumps' dataset, if it doesn't previously exist.
2. Extracts a list of file paths from a CartoDB table (https://vertnet.cartodb.com/tables/resource_staging). Important: Make sure the the field ```harvestfolder``` or ```harvestfoldernew``` contains the Google Storage path to the latest file for each resource. Even more important: Make sure that the schema for every file is consistent with the schema for BigQuery. Any change in the source file structure requires a corresponding change in the ```schema.json``` file, which can be generated from the ```harvest_fields``` file.
3. For each file from step 2, a single job is created to load the data into the BigQuery table
4. Once all jobs have finished, checks are made to see if any job has failed. If a load job fails, the whole upload of that particular resource is aborted.
5. For failed jobs, an individual load job is run for each controbutin data file. Thus, partial resources can still be loaded from files that have no problematic data.
6. A list of the failed data files is created in the file 'failed.txt'.

Requirements
------------

googleapis
----------

The ```fullDump.py``` script requires the googleapis module. More information on the googleapis module and how to install it can be found here at https://github.com/jotegui/googleapis. Install the googleapis module and add the path to it in the environment variable ``PYTHONPATH`` (e.g., ```export PYTHONPATH=$PYTHONPATH:/Users/Me/Projects/VertNet/``` where the ```googlapis``` folder is under VertNet). Make sure the googleapis module is functional in python before continuing. In particular, make sure that an appropriate ```client_secrets.json``` file is in the ```googleapis``` folder. This file is described at https://developers.google.com/api-client-library/python/guide/aaa_client_secrets and can be generated and downloaded from the Developers' console (https://console.developers.google.com). In the console, select the project, then select the Credentials page under APIs & auth. If there is already a ClientID for native application in the OAuth list, click on "Download JSON" and put that file in the googleapis folder. Otherwise, click on "Create new Client ID". Select "Installed application" as the Application type and "Other" as the Installed Application type. Then click on "Create Client ID" and download the ```client_secrets.json``` file for this application as described above.

BigQuery and CloudStorage
-------------------------

The configuration variables for the BigQuery and CloudStorage services are included in ```fullDump_cred.py```. The ```fullDump.py``` script is prepared to load them automatically.

Setup
-----

The first run of ```fullDump.py``` will require two authentications and will generate two files: ```bigquery.dat``` and ```storage.dat```. These files avoid having to re-authenticate each time the script is run.

Although not necessary, these files can be pre-built. To do so, open the python interpreter and execute the following code:

```
cd fullDump
python

>>> from googleapis import BigQuery, CloudStorage  # Import the module
>>> from fulldump_cred import cs_cred, bq_cred  # Import the credentials
>>> bq = BigQuery.BigQuery(bq_cred) # Create the bigquery.dat file
>>> cs = CloudStorage.CloudStorage(cs_cred) # Create the storage.dat file
```

Authentication windows will open twice, once for BigQuery and once for CloudStorage. To avoid having to authenticate manually each time a script is run, keep the ```client_secrets.json``` file in the ```googleapis``` folder and the two .dat files in any folder with a script that will run googleapi services.

schema.json
-----------

The load jobs performed by BigQuery require that a schema of the table be specified. This must be provided in file ```schema.json```, which _must_ be in the same folder as ```fullDump.py```. The ```schema.json``` file can be built from a simpler file called ```harvest_fields```, which contains an ordered list of all the names of the fields in the harvested files, one name per line. The repository already has a working example of such file. Modify it to match the structure of the files that will be uploaded into BigQuery, then run the script ```build_schema.py```:

```
   $ ./build_schema.py
```

The number of fields _must match_ between the ```schema.json``` file and the data files, or the load jobs will fail.

How it works
------------

Make sure the ```client_secrets.json``` is in the ```googleapis``` folder and that the files ```schema.json```, ```bigquery.dat``` and ```storage.dat``` are in the same folder as the ```fullDump.py``` and ```fulldump_cred.py``` scripts.

Then simply run:

    python fullDump.py

And enjoy the show. The program will show updates on each step.

The ```fullDump.py``` script builds a new BigQuery table in the 'dumps' dataset, called full_YYYYMMDD, where YYYMMDD is replaced by the current date when the script is run. For example, running the script on July 30th, 2014 would create the table dumps.full_20140730. The default values can be overriden by changing the ```dataset_name``` in ```fullDump.py```. 

The script will also generate a file in the same folder as ```fullDump.py``` (based on the property ```dump_file```, named ```failed.txt``` by default) containing a list of files that fail to upload into BigQuery. Failures usually occur if there is an illegal character in the data files, and these files cannot be uploaded to BigQuery unless these characters have been removed with.

Contact
-------

For questions and comments, contact any of the repository contributors.
