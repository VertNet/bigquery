byclass
=======

Extraction of class-level CSV files based on a given snapshot of the VertNet Harvesting.

Requirements
------------

In order to run, this script needs the googleapis module installed and accessible to python via the PYTHONPATH. The module and instructions on how to install it can be found here: https://github.com/jotegui/googleapis.

It also requires the client_secrets.json file, which can be obtained through the Developers' console (https://console.developers.google.com).

The configuration variables for the BigQuery and CloudStorage services are included in the folder, in the byclass_cred.py module. The byClass.py script is prepared to load them automatically.

Setup
-----

The first run of the script will generate two files: bigquery.dat and storage.dat. These files avoid having to re-authenticate each time the script is run.

Although not necessary, these files can be pre-built. This, in fact, can help making sure the googleapis module is accessible to python. To do that, open the python interpreter and execute the following code:

    from googleapis import BigQuery, CloudStorage  # Import the module
    from byclass_cred import cs_cred, bq_cred  # Import the credentials
    bq = BigQuery.BigQuery(bq_cred)
    cs = CloudStorage.CloudStorage(cs_cred)

The authentication flow will run twice (_i.e._, the authentication window will open twice), one for BigQuery and another one for CloudStorage. Keep the client_secrets.json file and the two .dat files in each folder that will run any googleapi services; that way, you won't need to re-authenticate.

How it works
------------

Make sure the client_secrets.json, bigquery.dat and storage.dat files are in the same folder as the byClass.py and byclass_cred.py files.

Inside byClass.py, on line 141, the version of the full dump to be used can be specified. By default, it has the 20140730 value, which points to the dumps.full_20140730 table in BigQuery. This can me modified before running the script to generate files based on different versions. The value must match the date value in dumps.full_YYYYMMDD.

Then simply run:

    python byClass.py

And enjoy the show. The program will throw updates on each step. It takes a while to finish, the longest step being the export to Cloud Storage.

Once finished, the class-based csv files will be found in he vertnet-byclass bucket on Cloud Storage.

Any question, shoot me an email (javier.otegui@gmail.com)
