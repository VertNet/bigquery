from googleapis import BigQuery as BQ
from googleapis import CloudStorage as CS
from byclass_cred import bq_cred, cs_cred

class Exporter():
    """Wrapper class. This object performs the following tasks:
    - create_tables: Creates a single table for each taxonomic class in BigQuery
    - export_tables: Moves the new tables to Cloud Storage, in small chunks
    - merge_files: Merges all chunks into a single file for each class
    - remove_chunks: Deletes all the small chunks
"""
    
    def __init__(self, table_version):
        """Initialize object variables."""
        self.bq = BQ.BigQuery(bq_cred)
        self.cs = CS.CloudStorage(cs_cred)
        self.table_version = table_version
        self.classes = ['Aves','Mammalia','Amphibia','Reptilia','Actinopterygii','Chondrichthyes']
        self.dataset_name = 'byClass'
        self.bucket_name = 'vertnet-byclass'
        self.query_jobs = {}
        self.extract_jobs = {}
    
    
    def create_dataset(self):
        """Create a dataset to store the class tables."""
        print "Creating new BigQuery dataset..."
        resp = self.bq.create_dataset(self.dataset_name)
        print "New dataset {0} created".format(resp['datasetReference']['datasetId'])
        
        return
    
    
    def create_tables(self):
        """Create one table per class."""
        print "Creating individual tables..."
        for i in self.classes:
            table_name = '{0}_{1}'.format(i, self.table_version)
            query = 'select * from dumps.full_{0} where classs="{1}"'.format(self.table_version, i)
            resp = self.bq.run_query_to_table(query, self.dataset_name, table_name)
            self.query_jobs[i] = resp['jobReference']['jobId']
            print "Query: class: {0}, jobId: {1}".format(i, resp['jobReference']['jobId'])
        
        return
    
    
    def wait_jobs(self, timeout=5):
        """Wait until all jobs finish."""
        print "Waiting for jobs to finish..."
        self.bq.wait_jobs(timeout)
        return 
    
    
    def export_tables(self):
        """Export tables to Cloud Storage."""
        print "Exporting tables to Cloud Storage..."
        for i in self.classes:
            table_name = '{0}_{1}'.format(i, self.table_version)
            object_name = table_name+"_*.csv"
            resp = self.bq.extract_table(self.dataset_name, table_name, self.bucket_name, object_name)
            self.extract_jobs[i] = resp['jobReference']['jobId']
            print "Export: class: {0}, jobId: {1}".format(i, resp['jobReference']['jobId'])
        
        return
    
    
    def remove_dataset(self):
        """Remove all class tables."""
        print "Deleting BigQuery dataset..."
        resp = self.bq.delete_dataset(self.dataset_name, force=True)
        print resp
        return
    
    
    def merge_files(self):
        """Merge all chunks into single file."""
        print "Merging chunks..."
        for i in self.classes:
            req_body = self.cs.prepare_merge(i)[0]
            
            if len(req_body['sourceObjects']) > 1:
                destinationObject = "{0}_{1}.csv".format(i, self.table_version)
                resp = self.cs.compose(req_body, destinationObject)
                print 'File {0} created in bucket {1}'.format(resp['name'], resp['bucket'])
                #self.compose_jobs[i] = resp['jobReference']['jobId']
                #print "Compose: class: {0}, jobId: {1}".format(i, resp['jobReference']['jobId'])
            else:
                sourceObject = req_body['sourceObjects'][0]['name']
                destinationObject = "{0}_{1}.csv".format(i, self.table_version)
                resp = self.cs.copy_object_within_bucket(sourceObject, destinationObject)
                print 'File {0} created in bucket {1}'.format(resp['name'], resp['bucket'])

        return
    
    
    def remove_chunks(self):
        """Delete chunks."""
        print "Deleting chunks..."
        for i in self.classes:
            files = self.cs.list_bucket("{0}_{1}_0".format(i, self.table_version))
            for j in files['items']:
                name = j['name']
                resp = self.cs.delete_object(name)
        
        return


    def run(self):
        """Performs each step sequentially."""
        
        print "Starting extraction of class-level files for full dump version {0}".format(self.table_version)
        
        # Create a dataset to store the class tables
        self.create_dataset()
        
        # Create tables
        self.create_tables()
        
        # Wait until all jobs finish
        self.wait_jobs(timeout=10)
        
        # Export tables to Cloud Storage
        self.export_tables()
        
        # Wait until all jobs finish
        self.wait_jobs(timeout=20)
        
        # Remove all class tables
        self.remove_dataset()
        
        # Merge all chunks into single file
        self.merge_files()
        
        # Delete chunks
        self.remove_chunks()


if __name__ == "__main__":
    
    # Full dump version
    table_version = '20140730'
    
    # Create instance
    exp = Exporter(table_version)
    
    # Run process
    exp.run()
