from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import hashlib
import aiohttp
import aiofiles

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'biofetch')]

# Create directories for file storage
DOWNLOAD_DIR = ROOT_DIR / 'downloads'
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Create the main app
app = FastAPI(
    title="BioFetch API",
    description="Unified Bioinformatics Data Downloader",
    version="1.0.0"
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Database configurations with REAL API endpoints
DATABASE_CONFIGS = {
    'sra': {
        'name': 'Sequence Read Archive (NCBI)',
        'base_url': 'https://trace.ncbi.nlm.nih.gov/Traces/sra-reads-be/fastq',
        'file_extension': '.fastq',
        'validation_prefixes': ['SRR', 'ERR', 'DRR'],
        'example_ids': ['SRR000001', 'SRR000002']
    },
    'genbank': {
        'name': 'GenBank (NCBI)',
        'base_url': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi',
        'file_extension': '.fasta',
        'validation_prefixes': ['NC_', 'NT_', 'NW_', 'NZ_'],
        'example_ids': ['NC_045512', 'NC_000001']
    },
    'ena': {
        'name': 'European Nucleotide Archive',
        'base_url': 'https://www.ebi.ac.uk/ena/browser/api/fasta',
        'file_extension': '.fasta',
        'validation_prefixes': ['ERR', 'SRR'],
        'example_ids': ['ERR000001', 'SRR000001']
    },
    'uniprot': {
        'name': 'Universal Protein Resource',
        'base_url': 'https://rest.uniprot.org/uniprotkb',
        'file_extension': '.fasta',
        'validation_prefixes': [],
        'example_ids': ['P04637', 'Q9Y261']
    },
    'pdb': {
        'name': 'Protein Data Bank',
        'base_url': 'https://files.rcsb.org/download',
        'file_extension': '.pdb',
        'validation_prefixes': [],
        'example_ids': ['1A0O', '3J3Q']
    },
    'geo': {
        'name': 'Gene Expression Omnibus',
        'base_url': 'https://ftp.ncbi.nlm.nih.gov/geo',
        'file_extension': '.txt',
        'validation_prefixes': ['GSE', 'GSM', 'GPL'],
        'example_ids': ['GSE000001', 'GSM000001']
    }
}

# Pydantic Models
class DownloadRequest(BaseModel):
    accession_id: str
    database: str
    validate_format: bool = True
    
class BatchDownloadRequest(BaseModel):
    accession_ids: List[str]
    database: str
    validate_format: bool = True

class DownloadJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    accession_id: str
    database: str
    status: str = "pending"
    progress: float = 0.0
    file_size: Optional[int] = None
    file_path: Optional[str] = None
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DownloadJobResponse(BaseModel):
    id: str
    accession_id: str
    database: str
    status: str
    progress: float
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None

class DatabaseInfo(BaseModel):
    id: str
    name: str
    example_ids: List[str]
    validation_prefixes: List[str]
    total_downloads: int = 0

# Utility Functions
def validate_accession(accession: str, database: str) -> bool:
    """Validate accession format for given database"""
    if database not in DATABASE_CONFIGS:
        return False
    
    prefixes = DATABASE_CONFIGS[database]['validation_prefixes']
    if not prefixes:
        return True
    
    return any(accession.startswith(prefix) for prefix in prefixes)

def compute_checksum(file_path: Path) -> str:
    """Compute MD5 checksum of file"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()

def get_download_url(accession: str, database: str) -> str:
    """Generate actual download URL for given accession"""
    config = DATABASE_CONFIGS[database]
    
    if database == 'genbank':
        return f"{config['base_url']}?db=nucleotide&id={accession}&rettype=fasta&retmode=text"
    elif database == 'uniprot':
        return f"{config['base_url']}/{accession}.fasta"
    elif database == 'pdb':
        return f"{config['base_url']}/{accession}.pdb"
    elif database == 'ena':
        return f"{config['base_url']}/{accession}"
    elif database == 'sra':
        # SRA requires special handling via SRA toolkit
        return f"{config['base_url']}?acc={accession}"
    elif database == 'geo':
        # GEO FTP structure
        return f"{config['base_url']}/series/{accession[:5]}nnn/{accession}/matrix/{accession}_series_matrix.txt.gz"
    
    return None

async def download_file_real(url: str, file_path: Path, job_id: str) -> bool:
    """Download file from actual URL with progress tracking"""
    try:
        timeout = aiohttp.ClientTimeout(total=600)  # 10 minutes timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logging.error(f"Download failed with status {response.status}: {url}")
                    return False
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                async with aiofiles.open(file_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Update progress
                        if total_size > 0:
                            progress = downloaded / total_size
                        else:
                            progress = 0.5  # Unknown size, show 50%
                        
                        await db.download_jobs.update_one(
                            {"id": job_id},
                            {"$set": {"progress": progress, "status": "downloading"}}
                        )
                
                return True
                
    except asyncio.TimeoutError:
        logging.error(f"Download timeout for {job_id}")
        return False
    except Exception as e:
        logging.error(f"Download failed for {job_id}: {str(e)}")
        return False

async def process_download(job_id: str):
    """Background task to process download"""
    try:
        job_doc = await db.download_jobs.find_one({"id": job_id})
        if not job_doc:
            return
        
        accession = job_doc["accession_id"]
        database = job_doc["database"]
        
        # Generate download URL
        url = get_download_url(accession, database)
        if not url:
            await db.download_jobs.update_one(
                {"id": job_id},
                {"$set": {"status": "failed", "error_message": "Could not generate download URL"}}
            )
            return
        
        # Create file path
        ext = DATABASE_CONFIGS[database]['file_extension']
        file_path = DOWNLOAD_DIR / f"{accession}{ext}"
        
        # Download file (REAL download now!)
        logging.info(f"Starting real download: {accession} from {database}")
        success = await download_file_real(url, file_path, job_id)
        
        if success and file_path.exists():
            checksum = compute_checksum(file_path)
            file_size = file_path.stat().st_size
            
            await db.download_jobs.update_one(
                {"id": job_id},
                {"$set": {
                    "status": "completed",
                    "progress": 1.0,
                    "file_path": str(file_path),
                    "file_size": file_size,
                    "checksum": checksum,
                    "completed_at": datetime.now(timezone.utc)
                }}
            )
            logging.info(f"Download completed: {accession} ({file_size} bytes)")
        else:
            await db.download_jobs.update_one(
                {"id": job_id},
                {"$set": {"status": "failed", "error_message": "Download failed or file not created"}}
            )
            logging.error(f"Download failed: {accession}")
            
    except Exception as e:
        logging.error(f"Error processing download {job_id}: {str(e)}")
        await db.download_jobs.update_one(
            {"id": job_id},
            {"$set": {"status": "failed", "error_message": str(e)}}
        )

# API Endpoints
@api_router.get("/")
async def root():
    return {"message": "BioFetch API - Unified Bioinformatics Data Downloader", "version": "1.0.0"}

@api_router.get("/databases", response_model=List[DatabaseInfo])
async def get_databases():
    """Get list of supported databases"""
    databases = []
    
    for db_id, config in DATABASE_CONFIGS.items():
        count = await db.download_jobs.count_documents({"database": db_id})
        
        databases.append(DatabaseInfo(
            id=db_id,
            name=config['name'],
            example_ids=config['example_ids'],
            validation_prefixes=config['validation_prefixes'],
            total_downloads=count
        ))
    
    return databases

@api_router.post("/download", response_model=DownloadJobResponse)
async def create_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Create a new download job"""
    if request.database not in DATABASE_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unsupported database: {request.database}")
    
    if request.validate_format and not validate_accession(request.accession_id, request.database):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid accession format for {request.database}"
        )
    
    job = DownloadJob(
        accession_id=request.accession_id,
        database=request.database,
        metadata={"validate_format": request.validate_format}
    )
    
    job_doc = job.model_dump()
    job_doc['created_at'] = job_doc['created_at'].isoformat()
    
    await db.download_jobs.insert_one(job_doc)
    background_tasks.add_task(process_download, job.id)
    
    return DownloadJobResponse(
        id=job.id,
        accession_id=job.accession_id,
        database=job.database,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at
    )

@api_router.post("/batch-download")
async def create_batch_download(request: BatchDownloadRequest, background_tasks: BackgroundTasks):
    """Create multiple download jobs"""
    if request.database not in DATABASE_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Unsupported database: {request.database}")
    
    jobs = []
    
    for accession_id in request.accession_ids:
        if request.validate_format and not validate_accession(accession_id, request.database):
            continue
        
        job = DownloadJob(
            accession_id=accession_id,
            database=request.database,
            metadata={"validate_format": request.validate_format, "batch": True}
        )
        
        job_doc = job.model_dump()
        job_doc['created_at'] = job_doc['created_at'].isoformat()
        
        await db.download_jobs.insert_one(job_doc)
        background_tasks.add_task(process_download, job.id)
        
        jobs.append({"id": job.id, "accession_id": job.accession_id, "status": job.status})
    
    return {"jobs": jobs, "total": len(jobs)}

@api_router.get("/jobs/{job_id}", response_model=DownloadJobResponse)
async def get_download_job(job_id: str):
    """Get download job details"""
    job_doc = await db.download_jobs.find_one({"id": job_id}, {"_id": 0})
    
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if isinstance(job_doc['created_at'], str):
        job_doc['created_at'] = datetime.fromisoformat(job_doc['created_at'])
    
    if job_doc.get('completed_at') and isinstance(job_doc['completed_at'], str):
        job_doc['completed_at'] = datetime.fromisoformat(job_doc['completed_at'])
    
    download_url = None
    if job_doc['status'] == 'completed' and job_doc.get('file_path'):
        download_url = f"/api/download-file/{job_id}"
    
    return DownloadJobResponse(
        id=job_doc['id'],
        accession_id=job_doc['accession_id'],
        database=job_doc['database'],
        status=job_doc['status'],
        progress=job_doc['progress'],
        file_size=job_doc.get('file_size'),
        error_message=job_doc.get('error_message'),
        created_at=job_doc['created_at'],
        completed_at=job_doc.get('completed_at'),
        download_url=download_url
    )

@api_router.get("/jobs", response_model=List[DownloadJobResponse])
async def get_download_jobs(limit: int = 50, skip: int = 0):
    """Get list of download jobs"""
    jobs_cursor = db.download_jobs.find({}, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    jobs_docs = await jobs_cursor.to_list(length=limit)
    
    jobs = []
    for job_doc in jobs_docs:
        if isinstance(job_doc['created_at'], str):
            job_doc['created_at'] = datetime.fromisoformat(job_doc['created_at'])
        
        if job_doc.get('completed_at') and isinstance(job_doc['completed_at'], str):
            job_doc['completed_at'] = datetime.fromisoformat(job_doc['completed_at'])
        
        download_url = None
        if job_doc['status'] == 'completed' and job_doc.get('file_path'):
            download_url = f"/api/download-file/{job_doc['id']}"
        
        jobs.append(DownloadJobResponse(
            id=job_doc['id'],
            accession_id=job_doc['accession_id'],
            database=job_doc['database'],
            status=job_doc['status'],
            progress=job_doc['progress'],
            file_size=job_doc.get('file_size'),
            error_message=job_doc.get('error_message'),
            created_at=job_doc['created_at'],
            completed_at=job_doc.get('completed_at'),
            download_url=download_url
        ))
    
    return jobs

@api_router.get("/download-file/{job_id}")
async def download_file(job_id: str):
    """Download completed file"""
    job_doc = await db.download_jobs.find_one({"id": job_id})
    
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job_doc['status'] != 'completed' or not job_doc.get('file_path'):
        raise HTTPException(status_code=400, detail="File not ready for download")
    
    file_path = Path(job_doc['file_path'])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        path=str(file_path),
        filename=f"{job_doc['accession_id']}{DATABASE_CONFIGS[job_doc['database']]['file_extension']}",
        media_type='application/octet-stream'
    )

@api_router.get("/stats")
async def get_stats():
    """Get download statistics"""
    total_downloads = await db.download_jobs.count_documents({})
    completed_downloads = await db.download_jobs.count_documents({"status": "completed"})
    failed_downloads = await db.download_jobs.count_documents({"status": "failed"})
    
    db_stats = {}
    for db_id in DATABASE_CONFIGS.keys():
        count = await db.download_jobs.count_documents({"database": db_id})
        db_stats[db_id] = count
    
    return {
        "total_downloads": total_downloads,
        "completed_downloads": completed_downloads,
        "failed_downloads": failed_downloads,
        "success_rate": completed_downloads / total_downloads if total_downloads > 0 else 0,
        "database_breakdown": db_stats
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
