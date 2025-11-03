#!/usr/bin/env python3
"""
BioFetch CLI - Command Line Interface
Simple version for testing and basic operations
"""
import argparse
import requests
import time
import sys

class BioFetchCLI:
    def __init__(self, api_url='http://localhost:8001/api'):
        self.api_url = api_url
    
    def test_connection(self):
        """Test API connection"""
        try:
            response = requests.get(f"{self.api_url}/")
            print(f"✅ API Connection: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ API Connection failed: {e}")
            return False
    
    def list_databases(self):
        """List all supported databases"""
        try:
            response = requests.get(f"{self.api_url}/databases")
            databases = response.json()
            
            print("\n🗄️  Supported Databases:")
            print("="*50)
            for db in databases:
                print(f"  {db['id']:<12} - {db['name']}")
                print(f"    Examples: {', '.join(db['example_ids'])}")
                if db['validation_prefixes']:
                    print(f"    Prefixes: {', '.join(db['validation_prefixes'])}")
                print(f"    Downloads: {db['total_downloads']}")
                print()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def get_stats(self):
        """Get download statistics"""
        try:
            response = requests.get(f"{self.api_url}/stats")
            stats = response.json()
            
            print("\n📊 BioFetch Statistics")
            print("="*30)
            print(f"Total Downloads: {stats.get('total_downloads', 0)}")
            print(f"Completed: {stats.get('completed_downloads', 0)}")
            print(f"Failed: {stats.get('failed_downloads', 0)}")
            print(f"Success Rate: {stats.get('success_rate', 0)*100:.1f}%")
            
            if stats.get('database_breakdown'):
                print("\nDatabase Breakdown:")
                for db, count in stats['database_breakdown'].items():
                    print(f"  {db}: {count}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def list_jobs(self, limit=20):
        """List recent download jobs"""
        try:
            response = requests.get(f"{self.api_url}/jobs?limit={limit}")
            jobs = response.json()
            
            if not jobs:
                print("No jobs found.")
                return True
            
            print("\n📋 Recent Jobs:")
            print("="*80)
            print(f"{'Accession':<15} {'Database':<12} {'Status':<12} {'Progress':<10}")
            print("="*80)
            
            for job in jobs:
                progress = f"{job['progress']*100:.1f}%" if job['progress'] else "0%"
                print(f"{job['accession_id']:<15} {job['database']:<12} {job['status']:<12} {progress:<10}")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def download(self, accession, database, wait=True):
        """Start a download"""
        try:
            payload = {
                "accession_id": accession,
                "database": database,
                "validate_format": True
            }
            
            response = requests.post(f"{self.api_url}/download", json=payload)
            response.raise_for_status()
            job_data = response.json()
            
            print(f"✅ Download started for {accession}")
            print(f"📋 Job ID: {job_data['id']}")
            print(f"🔄 Status: {job_data['status']}")
            
            if wait:
                print("\nWaiting for download to complete...")
                return self.wait_for_job(job_data['id'])
            
            return True
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error: {e.response.json().get('detail', str(e))}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def wait_for_job(self, job_id):
        """Wait for job completion"""
        while True:
            try:
                response = requests.get(f"{self.api_url}/jobs/{job_id}")
                job = response.json()
                
                status = job['status']
                progress = job['progress']
                
                if status == 'downloading':
                    print(f"\r📥 Downloading... {progress*100:.1f}%", end='', flush=True)
                elif status == 'pending':
                    print(f"\r⏳ Pending...", end='', flush=True)
                elif status == 'completed':
                    print(f"\r✅ Download completed!              ")
                    print(f"📁 File size: {job.get('file_size', 0)} bytes")
                    print(f"🔗 Download URL: {self.api_url.replace('/api', '')}{job['download_url']}")
                    return True
                elif status == 'failed':
                    print(f"\r❌ Download failed: {job.get('error_message', 'Unknown error')}")
                    return False
                
                time.sleep(1)
            except Exception as e:
                print(f"\n❌ Error checking status: {e}")
                return False
    
    def batch_download(self, accessions, database):
        """Start batch download"""
        try:
            payload = {
                "accession_ids": accessions,
                "database": database,
                "validate_format": True
            }
            
            response = requests.post(f"{self.api_url}/batch-download", json=payload)
            response.raise_for_status()
            result = response.json()
            
            print(f"✅ Batch download started: {result['total']} jobs created")
            
            for job in result['jobs']:
                print(f"  - {job['accession_id']}: {job['id']}")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def get_job_status(self, job_id):
        """Get specific job status"""
        try:
            response = requests.get(f"{self.api_url}/jobs/{job_id}")
            job = response.json()
            
            print(f"\n📋 Job Details:")
            print(f"  ID: {job['id']}")
            print(f"  Accession: {job['accession_id']}")
            print(f"  Database: {job['database']}")
            print(f"  Status: {job['status']}")
            print(f"  Progress: {job['progress']*100:.1f}%")
            
            if job.get('file_size'):
                print(f"  Size: {job['file_size']} bytes")
            if job.get('error_message'):
                print(f"  Error: {job['error_message']}")
            if job.get('download_url'):
                print(f"  Download: {self.api_url.replace('/api', '')}{job['download_url']}")
            
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="BioFetch CLI - Unified Bioinformatics Data Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test API connection
  python biofetch_cli.py test
  
  # List supported databases
  python biofetch_cli.py databases
  
  # Download single file
  python biofetch_cli.py download --accession SRR000001 --db sra
  
  # Download without waiting
  python biofetch_cli.py download --accession SRR000001 --db sra --no-wait
  
  # Batch download
  python biofetch_cli.py batch --accessions SRR000001 SRR000002 --db sra
  
  # Check job status
  python biofetch_cli.py status --job-id <job_id>
  
  # List recent jobs
  python biofetch_cli.py jobs
  
  # View statistics
  python biofetch_cli.py stats

Supported databases: sra, genbank, ena, uniprot, pdb, geo
        """
    )
    
    parser.add_argument('--api-url', default='http://localhost:8001/api',
                       help='BioFetch API URL (default: http://localhost:8001/api)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Test command
    subparsers.add_parser('test', help='Test API connection')
    
    # Databases command
    subparsers.add_parser('databases', help='List supported databases')
    
    # Download command
    download_parser = subparsers.add_parser('download', help='Download single file')
    download_parser.add_argument('--accession', required=True, help='Accession ID')
    download_parser.add_argument('--db', required=True, help='Database name')
    download_parser.add_argument('--no-wait', action='store_true', help="Don't wait for completion")
    
    # Batch download command
    batch_parser = subparsers.add_parser('batch', help='Batch download')
    batch_parser.add_argument('--accessions', nargs='+', required=True, help='Accession IDs')
    batch_parser.add_argument('--db', required=True, help='Database name')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Check job status')
    status_parser.add_argument('--job-id', required=True, help='Job ID')
    
    # Jobs command
    jobs_parser = subparsers.add_parser('jobs', help='List recent jobs')
    jobs_parser.add_argument('--limit', type=int, default=20, help='Number of jobs')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    cli = BioFetchCLI(args.api_url)
    
    # Execute command
    success = False
    
    if args.command == 'test':
        success = cli.test_connection()
    elif args.command == 'databases':
        success = cli.list_databases()
    elif args.command == 'download':
        success = cli.download(args.accession, args.db, wait=not args.no_wait)
    elif args.command == 'batch':
        success = cli.batch_download(args.accessions, args.db)
    elif args.command == 'status':
        success = cli.get_job_status(args.job_id)
    elif args.command == 'jobs':
        success = cli.list_jobs(args.limit)
    elif args.command == 'stats':
        success = cli.get_stats()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()