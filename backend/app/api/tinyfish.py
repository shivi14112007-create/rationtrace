from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timezone

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.models import DataSource, ExtractionJob, SourceRecord
from backend.app.schemas.schemas import (
    DataSourceResponse,
    DataSourceCreateRequest,
    ExtractionJobResponse,
    ExtractionJobTriggerRequest,
    SourceRecordResponse,
    TinyFishStatusResponse,
)
from backend.app.integrations.tinyfish_client import (
    tinyfish_client,
    is_source_approved,
    SourceNotApprovedError,
    TinyFishError,
    MissingApiKeyError,
    NFSA_PUBLIC_ALLOCATION_URL,
)

router = APIRouter(prefix="/tinyfish", tags=["TinyFish Intelligence Center"])


@router.get("/status", response_model=TinyFishStatusResponse)
def get_tinyfish_status(db: Session = Depends(get_db)):
    """Returns the operational status, mode, and health of TinyFish integration."""
    has_key = tinyfish_client.has_api_key
    approved_count = db.query(DataSource).filter(DataSource.is_approved == True).count()
    total_jobs = db.query(ExtractionJob).count()

    latest_job = db.query(ExtractionJob).order_by(desc(ExtractionJob.started_at)).first()
    last_extraction_at = latest_job.started_at if latest_job else None

    return TinyFishStatusResponse(
        configured=has_key,
        mode="LIVE" if has_key else "DEMO",
        base_url=tinyfish_client.base_url,
        approved_sources_count=approved_count,
        total_jobs_count=total_jobs,
        last_extraction_at=last_extraction_at,
    )


@router.get("/sources", response_model=List[DataSourceResponse])
def get_data_sources(db: Session = Depends(get_db)):
    """Returns all registered portal sources and their approval status."""
    sources = db.query(DataSource).order_by(DataSource.name.asc()).all()
    return sources


@router.post("/sources", response_model=DataSourceResponse, status_code=status.HTTP_201_CREATED)
def create_data_source(payload: DataSourceCreateRequest, db: Session = Depends(get_db)):
    """Registers an approved portal data source into the allowlist."""
    # Check if approved according to domain rules
    approved = is_source_approved(payload.source_url)

    source = DataSource(
        name=payload.name,
        source_url=payload.source_url,
        jurisdiction=payload.jurisdiction,
        source_type=payload.source_type,
        is_approved=approved,
        is_enabled=True,
        last_checked_at=datetime.now(timezone.utc),
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.get("/jobs", response_model=List[ExtractionJobResponse])
def get_extraction_jobs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Returns extraction jobs history with source details."""
    jobs = db.query(ExtractionJob).order_by(desc(ExtractionJob.started_at)).limit(limit).all()
    results = []
    for j in jobs:
        results.append(
            ExtractionJobResponse(
                id=j.id,
                source_id=j.source_id,
                source_name=j.source.name if j.source else "Unknown Portal",
                source_url=j.source.source_url if j.source else "",
                job_status=j.job_status,
                started_at=j.started_at,
                completed_at=j.completed_at,
                records_extracted=j.records_extracted,
                records_validated=j.records_validated,
                error_summary=j.error_summary,
                mode=j.mode or "DEMO",
            )
        )
    return results


@router.get("/jobs/{job_id}", response_model=ExtractionJobResponse)
def get_extraction_job(job_id: int, db: Session = Depends(get_db)):
    """Returns details of a specific extraction job."""
    job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Extraction job not found")

    return ExtractionJobResponse(
        id=job.id,
        source_id=job.source_id,
        source_name=job.source.name if job.source else "Unknown Portal",
        source_url=job.source.source_url if job.source else "",
        job_status=job.job_status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        records_extracted=job.records_extracted,
        records_validated=job.records_validated,
        error_summary=job.error_summary,
        mode=job.mode or "DEMO",
    )


@router.get("/jobs/{job_id}/records", response_model=List[SourceRecordResponse])
def get_job_records(job_id: int, db: Session = Depends(get_db)):
    """Returns all source records parsed and validated during the specified job."""
    job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Extraction job not found")

    records = db.query(SourceRecord).filter(SourceRecord.extraction_job_id == job_id).all()
    return records


@router.post("/jobs", response_model=ExtractionJobResponse, status_code=status.HTTP_201_CREATED)
def trigger_extraction_job(payload: ExtractionJobTriggerRequest, db: Session = Depends(get_db)):
    """
    Triggers an automated extraction job using TinyFish Web Agent.
    - If mode is 'AUTO' and API key is present: executes LIVE extraction.
    - If key is missing or mode is 'DEMO': returns clearly labelled DEMO fixture.
    - If mode is 'LIVE' and key is missing: raises 400 Bad Request error.
    Never fakes a live success.
    """
    target_url = payload.url or NFSA_PUBLIC_ALLOCATION_URL

    try:
        result = tinyfish_client.extract_nfsa_allocations(
            url=target_url,
            reporting_period=payload.reporting_period,
            db=db,
            mode=payload.mode,
        )

        job_id = result.job_id
        if job_id:
            db_job = db.query(ExtractionJob).filter(ExtractionJob.id == job_id).first()
            if db_job:
                return ExtractionJobResponse(
                    id=db_job.id,
                    source_id=db_job.source_id,
                    source_name=db_job.source.name if db_job.source else "NFSA Portal",
                    source_url=db_job.source.source_url if db_job.source else target_url,
                    job_status=db_job.job_status,
                    started_at=db_job.started_at,
                    completed_at=db_job.completed_at,
                    records_extracted=db_job.records_extracted,
                    records_validated=db_job.records_validated,
                    error_summary=db_job.error_summary,
                    mode=db_job.mode,
                )

        # Fallback response if DB session was detached
        return ExtractionJobResponse(
            id=0,
            source_id=1,
            source_name="NFSA Public Allocation Portal",
            source_url=target_url,
            job_status=result.status,
            started_at=result.started_at,
            completed_at=result.completed_at,
            records_extracted=result.records_extracted,
            records_validated=result.records_validated,
            error_summary=result.error_summary,
            mode=result.mode,
        )

    except SourceNotApprovedError as snae:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Source URL rejected: {snae}"
        )
    except MissingApiKeyError as make:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key missing: {make}"
        )
    except TinyFishError as tfe:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"TinyFish Web Agent execution failed: {tfe}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction pipeline error: {e}"
        )
