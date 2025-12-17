import os
import uuid
import asyncio
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json
from typing import Dict
from workflow import stream_pdf_summaries

app = FastAPI(title="DocVeil API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

active_jobs: Dict[str, dict] = {}


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "DocVeil API",
        "version": "1.0.0"
    }


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    job_id = str(uuid.uuid4())
    
    file_path = UPLOAD_DIR / f"{job_id}.pdf"
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        active_jobs[job_id] = {
            'filename': file.filename,
            'path': str(file_path),
            'status': 'uploaded'
        }
        
        print(f"Uploaded PDF: {file.filename} (Job ID: {job_id})")
        
        return {
            'job_id': job_id,
            'filename': file.filename,
            'message': 'PDF uploaded successfully'
        }
    
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/stream-summary/{job_id}")
async def stream_summary(job_id: str):
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    pdf_path = job['path']
    
    if not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    async def event_generator():
        try:
            job['status'] = 'processing'
            
            async for summary_data in stream_pdf_summaries(pdf_path):

                event_data = json.dumps(summary_data)
                yield {
                    "event": "summary",
                    "data": event_data
                }
                
                await asyncio.sleep(0.1)
                
                if summary_data['status'] == 'complete':
                    job['status'] = 'complete'
                    break
            
            print(f"Completed streaming job {job_id}")
            
        except Exception as e:
            print(f"Error in job {job_id}: {str(e)}")
            error_data = json.dumps({
                'error': str(e),
                'status': 'error'
            })
            yield {
                "event": "error",
                "data": error_data
            }
            job['status'] = 'error'
    
    return EventSourceResponse(event_generator())


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):

    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    return {
        'job_id': job_id,
        'status': job['status'],
        'filename': job['filename']
    }


@app.delete("/cleanup/{job_id}")
async def cleanup_job(job_id: str):
 
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = active_jobs[job_id]
    pdf_path = Path(job['path'])
    
    if pdf_path.exists():
        pdf_path.unlink()
    
    del active_jobs[job_id]
    
    print(f"Cleaned up job {job_id}")
    
    return {'message': 'Job cleaned up successfully'}


if __name__ == "__main__":
    import uvicorn
    print("Starting DocVeil API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
