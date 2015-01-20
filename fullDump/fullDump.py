__author__ = '@jotegui'

from googleapis import BigQuery as BQ
from googleapis import CloudStorage as CS
from fulldump_cred import bq_cred, cs_cred

from datetime import datetime
import requests
import json
import os

class Dumper():
    """Wrapper class for dumping a full snapshot of the harvested files to BigQuery."""
    
    def __init__(self):
        """Initialize instance variables."""
        self.bq = BQ.BigQuery(bq_cred)
        self.cs = CS.CloudStorage(cs_cred)
        
        # BigQuery naming
        self.dataset_name = 'dumps'
        self.table_version = format(datetime.today(), '%Y%m%d')
        self.table_name = 'full_{0}'.format(self.table_version)
        
        # Other files' naming
        self.dump_file = 'failed.txt'
        self.schema = json.load(open(os.path.join(os.path.dirname(__file__), 'schema.json')))
        
        self.resources = []
        self.load_jobs = {}
        self.failed_resources = []        
        
        return
    
    
    def get_resources(self):
        """Extract location of last indexed resources."""
        
        print "Extracting location of harvested files."
        
        # Call CartoDB API
        api_url = "https://vertnet.cartodb.com/api/v2/sql"
        # q = "select harvestfolder from resource_staging where ipt is true and networks like '%VertNet%'"
        q = "select harvestfoldernew from resource_staging where icode='UNR'"
        params = {'q': q}
        r = requests.get(api_url, params=params)
        
        # Return results
        if r.status_code == 200:
            rows = json.loads(r.content)['rows']
            for i in rows:
#                self.resources.append(i['harvestfolder'].split('/', 1)[1])
                self.resources.append(i['harvestfoldernew'].split('/', 1)[1])
        else:
            print "Something went wrong with the query:"
            print r.text
        
        return
    
    
    def create_dataset(self):
        """Create the dumps dataset if it doesn't exist."""
        
        print "Creating dataset '{0}'".format(self.dataset_name)
        
        self.bq.create_dataset(self.dataset_name)
        
        return
    
    
    def build_uri_list(self, resource):
        """Build a list containing the URIs of the shards of a single resource."""
        
        print "Building list of chunks for {0}".format(resource)
        
        uri_list = []
        for i in self.cs.list_bucket(prefix=resource)['items']:
            uri = '/'.join(["gs:/", self.cs._BUCKET_NAME, i['name']])
            uri_list.append(uri)
        
        return uri_list
        
    
    def launch_load_job(self, uri_list):
        """Launch a job for loading all the chunks in a single resource."""
        
        print "Launching load job"
        
        job_id = self.bq.create_load_job(ds_name=self.dataset_name,
                                        table_name=self.table_name,
                                        uri_list=uri_list,
                                        schema=self.schema)
        
        return job_id
    
    
    def wait_jobs(self, timeout=5):
        """Wait until all jobs finish."""
        
        print "Waiting for jobs to finish..."
        
        self.bq.wait_jobs(timeout)
        
        return 
        
    
    def check_failed(self):
        """Check failed jobs."""
        
        print "Checking for failed jobs..."
        
        # Reset the failed_resources list
        self.failed_resources = []
        
        # Check failed jobs
        for resource in self.load_jobs:
            job_id = self.load_jobs[resource]['jobReference']['jobId']
            status = self.bq.check_job(job_id)
            if status['state'] == 'DONE' and 'errorResult' in status:
                print 'Resource {0} failed and job was aborted. Queued for individual load.'
                self.failed_resources.append(resource)
        
        # Reset the job_ids dictionary
        self.load_jobs = {}
        
        return
        
    
    def dump_failed(self):
        """Dump the failed chunks into a file."""
        
        if len(self.failed_resources) > 0:
            print "Some chunks could not be loaded into BigQuery."
            with open(self.dump_file, 'w') as w:
                for i in self.failed_resources:
                    w.write(i)
                    w.write("\n")
            print "These have been written to {0}".format(self.dump_file)
        
        return
            
    def run(self):
        """Perform each step sequentially."""
        
        # Create the dumps dataset if it doesn't exist
        self.create_dataset()
        
        # Extract location of last indexed resources
        self.get_resources()
        
        # Launch a load job for each resource
        for resource in self.resources:

            # Build a list containing the URIs of the shards of a single resource
            uri_list = self.build_uri_list(resource)
            
            # Launch a job for loading all the chunks in a single resource
            job_id = self.launch_load_job(uri_list)
            
            # Store the job_id in the dictionary of job_ids
            self.load_jobs[resource] = job_id
        
        # Wait until all jobs finish
        self.wait_jobs(timeout=10)
        
        # Check failed jobs
        self.check_failed()
        
        # If any resource failed, run individual jobs for each chunk
        if len(self.failed_resources) > 0:
            
            # For each failed resource, launch an individual job for each chunk
            for resource in self.failed_resources:
                
                # Build a list containing the URIs of the shards of a single resource
                uri_list = self.build_uri_list(resource)
                
                # For each uri (individual chunk)
                for uri in uri_list:
                
                    # Launch a load job
                    job_id = self.launch_load_job(uri)
                    
                    # Store the job_id in the dictionary of job_ids
                    self.load_jobs[uri] = job_id
            
            # Wait until all jobs finish
            self.wait_jobs(timeout=10)
            
            # Check failed jobs
            self.check_failed()
            
            # Dump failed chunks
            self.dump_failed()
        
        # The end
        return
        

if __name__ == "__main__":
    
    # Create instance
    dmp = Dumper()
    
    # Run process
    dmp.run()
