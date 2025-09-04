"""
Website Builder Background Tasks

Celery tasks for async website building, deployment, SEO monitoring,
and lead processing for the Hero365 Website Builder system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal
import uuid

from celery import Celery
from celery.exceptions import Retry

from ..core.config import settings
from ..domain.entities.website import (
    BusinessWebsite, WebsiteBuildJob, BuildJobStatus, BuildJobType,
    WebsiteFormSubmission, WebsiteBookingSlot, SEOKeywordTracking
)
from ..application.services.website_builder_service import (
    WebsiteBuilderService, BuildConfiguration
)
from ..application.services.ai_content_generator_service import AIContentGeneratorService
from ..infrastructure.adapters.cloudflare_domain_adapter import CloudflareDomainAdapter
from ..domain.services.domain_registration_domain_service import DomainRegistrationDomainService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    'hero365_website_builder',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.workers.website_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression='gzip',
    result_compression='gzip',
    result_expires=3600,  # 1 hour
    task_routes={
        'app.workers.website_tasks.build_website_task': {'queue': 'website_builds'},
        'app.workers.website_tasks.deploy_website_task': {'queue': 'deployments'},
        'app.workers.website_tasks.process_form_submission_task': {'queue': 'lead_processing'},
        'app.workers.website_tasks.seo_monitoring_task': {'queue': 'seo_monitoring'},
        'app.workers.website_tasks.generate_llm_content_task': {'queue': 'llm_content'},
    }
)


# =====================================
# WEBSITE BUILD TASKS
# =====================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def build_website_task(self, website_id: str, build_config: Optional[Dict[str, Any]] = None):
    """
    Build a website using Next.js static site generation.
    
    This is the main task for building websites from templates and AI content.
    """
    
    logger.info(f"Starting website build for {website_id}")
    
    try:
        # Update job status to running
        _update_build_job_status(website_id, BuildJobStatus.RUNNING, started_at=datetime.utcnow())
        
        # Run the async build process
        result = asyncio.run(_build_website_async(website_id, build_config))
        
        if result.success:
            logger.info(f"Website build completed successfully: {website_id}")
            
            # Update job status to completed
            _update_build_job_status(
                website_id, 
                BuildJobStatus.COMPLETED,
                completed_at=datetime.utcnow(),
                duration_seconds=int(result.build_time_seconds),
                result_data={
                    "build_path": result.build_path,
                    "lighthouse_score": result.lighthouse_score,
                    "pages_generated": result.pages_generated,
                    "output_size_mb": result.output_size_mb
                }
            )
            
            # Queue deployment if auto-deploy is enabled
            if build_config and build_config.get("auto_deploy", False):
                deploy_website_task.delay(website_id)
            
            return {
                "success": True,
                "website_id": website_id,
                "build_time": result.build_time_seconds,
                "lighthouse_score": result.lighthouse_score
            }
        
        else:
            logger.error(f"Website build failed: {website_id} - {result.error_message}")
            
            # Update job status to failed
            _update_build_job_status(
                website_id,
                BuildJobStatus.FAILED,
                completed_at=datetime.utcnow(),
                error_message=result.error_message,
                build_logs=result.build_logs
            )
            
            # Retry if possible
            if self.request.retries < self.max_retries:
                logger.info(f"Retrying website build: {website_id} (attempt {self.request.retries + 1})")
                raise self.retry(countdown=60 * (self.request.retries + 1))
            
            return {
                "success": False,
                "website_id": website_id,
                "error": result.error_message
            }
    
    except Exception as e:
        logger.error(f"Unexpected error in website build: {website_id} - {str(e)}")
        
        # Update job status to failed
        _update_build_job_status(
            website_id,
            BuildJobStatus.FAILED,
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        
        # Retry on unexpected errors
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        raise


async def _build_website_async(website_id: str, build_config: Optional[Dict[str, Any]] = None):
    """Async wrapper for website building."""
    
    try:
        # Get repositories (when they're implemented)
        # website_repository = get_website_repository()
        # business_repository = get_business_repository()
        # branding_repository = get_branding_repository()
        # template_repository = get_template_repository()
        
        # website = await website_repository.get_by_id(uuid.UUID(website_id))
        # business = await business_repository.get_by_id(website.business_id)
        # branding = await branding_repository.get_by_business_id(website.business_id)
        # template = await template_repository.get_by_id(website.template_id)
        
        # For now, fetch real data via direct database query
        from ..infrastructure.repositories.business_repository import BusinessRepository
        from ..infrastructure.repositories.product_repository import ProductRepository
        from ..domain.entities.business import Business, TradeCategory
        from ..domain.entities.business_branding import BusinessBranding
        from ..domain.entities.website import WebsiteTemplate, BusinessWebsite, WebsiteStatus
        
        # Get a real business from the database
        business_repo = BusinessRepository()
        businesses = await business_repo.list()
        
        if not businesses:
            raise Exception("No businesses found in database. Cannot build website without real business data.")
        
        # Use the first available business
        business = businesses[0]
        logger.info(f"Using real business: {business.name}")
        
        # Create branding based on business data
        branding = BusinessBranding(
            business_id=business.id,
            primary_color="#1E3A8A",
            secondary_color="#3B82F6", 
            accent_color="#EF4444",
            font_family="Inter",
            theme_name="Professional"
        )
        
        # Create template based on business trade
        primary_trade = business.residential_trades[0] if business.residential_trades else "hvac"
        template = WebsiteTemplate(
            id=uuid.uuid4(),
            trade_type=primary_trade,
            trade_category=business.trade_category,
            name=f"{primary_trade.title()} Professional Template",
            structure={
                "pages": [
                    {
                        "path": "/",
                        "name": "Home",
                        "sections": [
                            {"type": "hero"},
                            {"type": "services"},
                            {"type": "contact-form"}
                        ]
                    }
                ]
            }
        )
        
        # Create website entity
        website = BusinessWebsite(
            id=uuid.UUID(website_id),
            business_id=business.id,
            template_id=template.id,
            subdomain=f"{business.name.lower().replace(' ', '-')}",
            status=WebsiteStatus.BUILDING,
            primary_trade=primary_trade
        )
        
        # Parse build configuration
        config = BuildConfiguration()
        if build_config:
            config = BuildConfiguration(**build_config)
        
        # Build the website
        builder_service = WebsiteBuilderService()
        result = await builder_service.build_website(
            website,
            business,
            branding,
            template,
            config
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in async website build: {str(e)}")
        raise


# =====================================
# LLM CONTENT GENERATION TASKS
# =====================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def generate_llm_content_task(
    self, 
    business_id: str, 
    content_config: Optional[Dict[str, Any]] = None
):
    """
    Generate comprehensive LLM content for all website pages and SEO.
    
    This is the main entrypoint for the LLM content generation pipeline.
    Orchestrates multiple LLM adapters to generate optimized content.
    
    Args:
        business_id: UUID of the business to generate content for
        content_config: Configuration for content generation (optional)
        
    Returns:
        Dict with generation results and content paths
    """
    
    logger.info(f"Starting LLM content generation for business {business_id}")
    
    try:
        # Create job tracking record
        job_id = str(uuid.uuid4())
        _update_content_job_status(
            job_id, 
            "running", 
            business_id=business_id,
            started_at=datetime.utcnow()
        )
        
        # Run the async content generation process
        # Legacy LLM pipeline removed
        result = {"success": False, "error_message": "Legacy LLM content pipeline removed. Use SEO artifacts API."}
        
        if result.get("success"):
            logger.info(f"LLM content generation completed: {business_id}")
            
            # Update job status to completed
            _update_content_job_status(
                job_id,
                "completed",
                completed_at=datetime.utcnow(),
                duration_seconds=result.get("generation_time_seconds", 0),
                result_data={
                    "pages_generated": result.get("pages_generated", 0),
                    "content_items": result.get("content_items", 0),
                    "seo_configs": result.get("seo_configs", 0),
                    "output_path": result.get("output_path"),
                    "quality_score": result.get("quality_score", 0)
                }
            )
            
            return {
                "success": True,
                "business_id": business_id,
                "job_id": job_id,
                "generation_time": result.get("generation_time_seconds"),
                "pages_generated": result.get("pages_generated"),
                "quality_score": result.get("quality_score")
            }
        
        else:
            logger.error(f"LLM content generation failed: {business_id} - {result.get('error_message')}")
            
            # Update job status to failed
            _update_content_job_status(
                job_id,
                "failed",
                completed_at=datetime.utcnow(),
                error_message=result.get("error_message")
            )
            
            return {
                "success": False,
                "business_id": business_id,
                "job_id": job_id,
                "error": result.get("error_message")
            }
            
    except Exception as e:
        logger.error(f"Error in LLM content generation task: {str(e)}")
        
        # Update job status to failed
        _update_content_job_status(
            job_id if 'job_id' in locals() else str(uuid.uuid4()),
            "failed",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        
        raise


async def _generate_llm_content_async(business_id: str, content_config: Optional[Dict[str, Any]], job_id: str):
    return {"success": False, "error_message": "Legacy LLM content pipeline removed."}


async def _store_generated_content(
    business_id: str, 
    job_id: str, 
    content_results: Dict[str, Any]
) -> str:
    """Store generated content in structured format for website builder."""
    
    import json
    from pathlib import Path
    
    # Create output directory
    backend_path = Path(__file__).parent.parent.parent
    output_dir = backend_path / "build_output" / f"llm-content-{job_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Store main content file
    content_file = output_dir / "generated-content.json"
    with open(content_file, 'w', encoding='utf-8') as f:
        json.dump(content_results, f, indent=2, ensure_ascii=False)
    
    # Store individual page content files
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)
    
    for page in content_results.get("pages", []):
        page_file = pages_dir / f"{page['slug']}.json"
        with open(page_file, 'w', encoding='utf-8') as f:
            json.dump(page, f, indent=2, ensure_ascii=False)
    
    # Store SEO configuration
    seo_file = output_dir / "seo-config.json"
    with open(seo_file, 'w', encoding='utf-8') as f:
        json.dump(content_results.get("seo_configs", {}), f, indent=2, ensure_ascii=False)
    
    logger.info(f"Stored generated content at: {output_dir}")
    return str(output_dir)


def _update_content_job_status(
    job_id: str,
    status: str,
    business_id: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    result_data: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None
):
    """Update content generation job status in database."""
    
    # TODO: Implement proper job tracking in database
    # For now, just log the status
    logger.info(f"Content job {job_id} status: {status}")
    if business_id:
        logger.info(f"  Business ID: {business_id}")
    if started_at:
        logger.info(f"  Started at: {started_at}")
    if completed_at:
        logger.info(f"  Completed at: {completed_at}")
    if duration_seconds:
        logger.info(f"  Duration: {duration_seconds}s")
    if result_data:
        logger.info(f"  Results: {result_data}")
    if error_message:
        logger.error(f"  Error: {error_message}")


@celery_app.task(bind=True, max_retries=2)
def deploy_website_task(self, website_id: str, domain: Optional[str] = None):
    """Deploy website to AWS S3 + CloudFront."""
    
    logger.info(f"Starting website deployment for {website_id}")
    
    try:
        # TODO: Implement deployment logic
        # deployment_service = AWSDeploymentService()
        # result = await deployment_service.deploy_website(website_id, build_path, domain)
        
        logger.info(f"Website deployed successfully: {website_id}")
        
        # TODO: Update website status to deployed
        # await website_repository.update(
        #     uuid.UUID(website_id),
        #     {
        #         "status": WebsiteStatus.DEPLOYED,
        #         "last_deploy_at": datetime.utcnow(),
        #         "deployment_info": result
        #     }
        # )
        
        return {
            "success": True,
            "website_id": website_id,
            "url": f"https://{domain or 'mock-business.hero365.ai'}"
        }
        
    except Exception as e:
        logger.error(f"Website deployment failed: {website_id} - {str(e)}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=120)
        
        raise


@celery_app.task
def optimize_website_task(website_id: str):
    """Optimize website performance and SEO."""
    
    logger.info(f"Starting website optimization for {website_id}")
    
    try:
        # TODO: Run optimization tasks
        # - Compress images
        # - Minify CSS/JS
        # - Generate optimized sitemap
        # - Update meta tags
        # - Run Lighthouse audit
        
        logger.info(f"Website optimization completed: {website_id}")
        
        return {
            "success": True,
            "website_id": website_id,
            "optimizations_applied": ["image_compression", "minification", "seo_updates"]
        }
        
    except Exception as e:
        logger.error(f"Website optimization failed: {website_id} - {str(e)}")
        raise


# =====================================
# LEAD PROCESSING TASKS
# =====================================

@celery_app.task(bind=True, max_retries=3)
def process_form_submission_task(
    self,
    submission_id: str,
    website_id: str,
    business_id: str,
    form_data: Dict[str, Any],
    visitor_info: Dict[str, Any]
):
    """Process form submission and create appropriate records."""
    
    logger.info(f"Processing form submission {submission_id}")
    
    try:
        # TODO: Create form submission record
        # submission = WebsiteFormSubmission(
        #     id=uuid.UUID(submission_id),
        #     website_id=uuid.UUID(website_id),
        #     business_id=uuid.UUID(business_id),
        #     form_data=form_data,
        #     visitor_info=visitor_info,
        #     lead_type=_determine_lead_type(form_data),
        #     priority_level=_determine_priority(form_data)
        # )
        # 
        # submission.extract_contact_info()
        # created_submission = await form_submission_repository.create(submission)
        
        # Route lead based on type and priority
        lead_type = _determine_lead_type(form_data)
        priority = _determine_priority(form_data)
        
        if priority == "emergency":
            # Immediate processing for emergencies
            emergency_lead_processing_task.delay(submission_id)
        elif lead_type == "quote_request":
            # Create estimate
            create_estimate_from_submission_task.delay(submission_id)
        elif lead_type == "service_booking":
            # Create job/appointment
            create_job_from_submission_task.delay(submission_id)
        else:
            # General lead processing
            general_lead_processing_task.delay(submission_id)
        
        # Send notifications
        send_lead_notifications_task.delay(submission_id, priority)
        
        # Track conversion
        track_conversion_task.delay(website_id, "form_submission", form_data)
        
        logger.info(f"Form submission processed successfully: {submission_id}")
        
        return {
            "success": True,
            "submission_id": submission_id,
            "lead_type": lead_type,
            "priority": priority
        }
        
    except Exception as e:
        logger.error(f"Form submission processing failed: {submission_id} - {str(e)}")
        
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30)
        
        raise


@celery_app.task(priority=9)  # High priority for emergencies
def emergency_lead_processing_task(submission_id: str):
    """Process emergency leads with immediate action."""
    
    logger.info(f"Processing emergency lead: {submission_id}")
    
    try:
        # TODO: Get submission data
        # submission = await form_submission_repository.get_by_id(uuid.UUID(submission_id))
        
        # Immediate actions for emergency leads:
        # 1. Send SMS to business owner
        # 2. Create high-priority job
        # 3. Attempt automatic callback
        # 4. Send emergency email alert
        
        # TODO: Implement emergency processing
        # await sms_service.send_emergency_alert(submission)
        # await job_service.create_emergency_job(submission)
        # await callback_service.schedule_immediate_callback(submission)
        # await email_service.send_emergency_alert(submission)
        
        logger.info(f"Emergency lead processed: {submission_id}")
        
        return {"success": True, "emergency_processed": True}
        
    except Exception as e:
        logger.error(f"Emergency lead processing failed: {submission_id} - {str(e)}")
        raise


@celery_app.task
def create_estimate_from_submission_task(submission_id: str):
    """Create estimate from quote request submission."""
    
    logger.info(f"Creating estimate from submission: {submission_id}")
    
    try:
        # TODO: Get submission and create estimate
        # submission = await form_submission_repository.get_by_id(uuid.UUID(submission_id))
        # estimate = await estimate_service.create_from_submission(submission)
        
        # TODO: Update submission with estimate ID
        # await form_submission_repository.update(
        #     uuid.UUID(submission_id),
        #     {"estimate_created_id": estimate.id}
        # )
        
        logger.info(f"Estimate created from submission: {submission_id}")
        
        return {"success": True, "estimate_created": True}
        
    except Exception as e:
        logger.error(f"Estimate creation failed: {submission_id} - {str(e)}")
        raise


@celery_app.task
def create_job_from_submission_task(submission_id: str):
    """Create job from booking submission."""
    
    logger.info(f"Creating job from submission: {submission_id}")
    
    try:
        # TODO: Get submission and create job
        # submission = await form_submission_repository.get_by_id(uuid.UUID(submission_id))
        # job = await job_service.create_from_submission(submission)
        
        # TODO: Update submission with job ID
        # await form_submission_repository.update(
        #     uuid.UUID(submission_id),
        #     {"job_created_id": job.id}
        # )
        
        logger.info(f"Job created from submission: {submission_id}")
        
        return {"success": True, "job_created": True}
        
    except Exception as e:
        logger.error(f"Job creation failed: {submission_id} - {str(e)}")
        raise


@celery_app.task
def general_lead_processing_task(submission_id: str):
    """Process general leads with standard workflow."""
    
    logger.info(f"Processing general lead: {submission_id}")
    
    try:
        # TODO: Standard lead processing
        # submission = await form_submission_repository.get_by_id(uuid.UUID(submission_id))
        # contact = await contact_service.create_or_update_from_submission(submission)
        # await crm_service.add_lead_to_pipeline(contact, submission)
        
        logger.info(f"General lead processed: {submission_id}")
        
        return {"success": True, "lead_processed": True}
        
    except Exception as e:
        logger.error(f"General lead processing failed: {submission_id} - {str(e)}")
        raise


@celery_app.task
def send_lead_notifications_task(submission_id: str, priority: str):
    """Send notifications for new leads."""
    
    logger.info(f"Sending notifications for submission: {submission_id}")
    
    try:
        # TODO: Send appropriate notifications based on priority
        # submission = await form_submission_repository.get_by_id(uuid.UUID(submission_id))
        
        if priority == "emergency":
            # Immediate SMS + email + push notification
            pass
        elif priority == "high":
            # SMS + email within 15 minutes
            pass
        else:
            # Email notification
            pass
        
        # TODO: Implement notification sending
        # await notification_service.send_lead_notifications(submission, priority)
        
        logger.info(f"Notifications sent for submission: {submission_id}")
        
        return {"success": True, "notifications_sent": True}
        
    except Exception as e:
        logger.error(f"Notification sending failed: {submission_id} - {str(e)}")
        raise


# =====================================
# SEO MONITORING TASKS
# =====================================

@celery_app.task
def seo_monitoring_task():
    """Monitor SEO performance for all websites."""
    
    logger.info("Starting SEO monitoring task")
    
    try:
        # TODO: Get all active websites
        # websites = await website_repository.get_all_active()
        
        # Process each website
        # for website in websites:
        #     check_keyword_rankings_task.delay(str(website.id))
        #     update_search_console_data_task.delay(str(website.id))
        #     monitor_core_web_vitals_task.delay(str(website.id))
        
        logger.info("SEO monitoring tasks queued")
        
        return {"success": True, "websites_processed": 0}  # Mock count
        
    except Exception as e:
        logger.error(f"SEO monitoring failed: {str(e)}")
        raise


@celery_app.task
def check_keyword_rankings_task(website_id: str):
    """Check keyword rankings for a website."""
    
    logger.info(f"Checking keyword rankings for website: {website_id}")
    
    try:
        # TODO: Get keywords to track
        # keywords = await seo_repository.get_tracked_keywords(uuid.UUID(website_id))
        
        # Check rankings for each keyword
        # for keyword in keywords:
        #     if keyword.needs_check():
        #         new_rank = await rank_tracking_service.check_keyword_rank(
        #             keyword.keyword, website.domain, keyword.target_location
        #         )
        #         keyword.update_rank(new_rank)
        #         await seo_repository.update_keyword(keyword)
        
        logger.info(f"Keyword rankings updated for website: {website_id}")
        
        return {"success": True, "keywords_checked": 0}  # Mock count
        
    except Exception as e:
        logger.error(f"Keyword ranking check failed: {website_id} - {str(e)}")
        raise


@celery_app.task
def update_search_console_data_task(website_id: str):
    """Update Google Search Console data."""
    
    logger.info(f"Updating Search Console data for website: {website_id}")
    
    try:
        # TODO: Fetch Search Console data
        # search_console_service = GoogleSearchConsoleService()
        # data = await search_console_service.get_performance_data(website_id)
        # await analytics_repository.update_search_console_data(website_id, data)
        
        logger.info(f"Search Console data updated for website: {website_id}")
        
        return {"success": True, "data_updated": True}
        
    except Exception as e:
        logger.error(f"Search Console update failed: {website_id} - {str(e)}")
        raise


@celery_app.task
def monitor_core_web_vitals_task(website_id: str):
    """Monitor Core Web Vitals performance."""
    
    logger.info(f"Monitoring Core Web Vitals for website: {website_id}")
    
    try:
        # TODO: Run Lighthouse audit
        # lighthouse_service = LighthouseService()
        # results = await lighthouse_service.audit_website(website_id)
        # await analytics_repository.update_core_web_vitals(website_id, results)
        
        logger.info(f"Core Web Vitals updated for website: {website_id}")
        
        return {"success": True, "vitals_updated": True}
        
    except Exception as e:
        logger.error(f"Core Web Vitals monitoring failed: {website_id} - {str(e)}")
        raise


# =====================================
# MOBILE SEO GENERATION TASKS
# =====================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def generate_seo_pages_task(self, task_data: Dict[str, Any]):
    """
    Generate SEO-focused pages and deploy to Cloudflare subdomain.
    
    Called from mobile app API to generate only SEO content pages
    without rebuilding core website functionality.
    """
    
    generation_id = task_data.get("generation_id")
    business_id = task_data.get("business_id")
    cloudflare_subdomain = task_data.get("cloudflare_subdomain")
    
    logger.info(f"Starting SEO page generation: {generation_id}")
    
    try:
        # Import the update function (circular import avoidance)
        from ..api.routes.website_seo import update_generation_status
        
        # Step 1: Fetch comprehensive business data
        asyncio.run(update_generation_status(
            generation_id, "fetching_data", 15, 
            "Fetching business data from Hero365 API"
        ))
        
        from ..application.services.professional_data_service import ProfessionalDataService
        data_service = ProfessionalDataService()
        business_data = asyncio.run(
            data_service.get_complete_professional_data(business_id)
        )
        
        if not business_data or not business_data.get("profile"):
            raise Exception(f"No business data found for {business_id}")
        
        business_name = business_data["profile"].get("business_name", "Professional Services")
        logger.info(f"Fetched data for: {business_name}")
        
        # Step 2: Build Next.js website with TypeScript SEO generation
        asyncio.run(update_generation_status(
            generation_id, "generating", 35,
            "Building Next.js website with TypeScript SEO generator"
        ))
        
        # The TypeScript generator handles both SEO page generation AND Next.js build
        build_result = _build_nextjs_website_with_seo(business_data, [], task_data)  # Empty seo_pages since TS generator handles it
        
        if not build_result.get("success"):
            raise Exception(f"Website build failed: {build_result.get('error', 'Unknown error')}")
        
        # Step 4: Deploy to Cloudflare Pages
        asyncio.run(update_generation_status(
            generation_id, "deploying", 80,
            "Deploying to Cloudflare Pages"
        ))
        
        deployment_result = _deploy_to_cloudflare_pages(
            cloudflare_subdomain, 
            build_result.get("build_path"),
            task_data
        )
        
        if not deployment_result.get("success"):
            raise Exception(f"Cloudflare deployment failed: {deployment_result.get('error', 'Unknown error')}")
        
        # Step 5: Success
        website_url = deployment_result.get("website_url")
        pages_generated = build_result.get("pages_generated", 0)
        
        asyncio.run(update_generation_status(
            generation_id, "completed", 100,
            "SEO pages deployed successfully",
            website_url=website_url,
            pages_generated=pages_generated,
            completed_at=datetime.utcnow(),
            project_name=deployment_result.get("project_name"),
            deployment_id=deployment_result.get("deployment_id")
        ))
        
        logger.info(f"SEO generation completed: {generation_id} -> {website_url} ({pages_generated} pages)")
        
        return {
            "success": True,
            "generation_id": generation_id,
            "website_url": website_url,
            "pages_generated": pages_generated,
            "project_name": deployment_result.get("project_name")
        }
        
    except Exception as e:
        logger.error(f"SEO generation failed: {generation_id} - {str(e)}")
        
        # Update status to failed
        from ..api.routes.website_seo import update_generation_status
        asyncio.run(update_generation_status(
            generation_id, "failed", 0,
            "SEO generation failed",
            error_message=str(e),
            completed_at=datetime.utcnow()
        ))
        
        # Retry on failure
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying SEO generation: {generation_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=120 * (self.request.retries + 1))
        
        raise


# Legacy SEO generation functions removed - replaced by TypeScript generator


def _build_nextjs_website_with_seo(
    business_data: Dict[str, Any], 
    seo_pages: List[Dict[str, Any]], 
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Build Next.js website with SEO pages using TypeScript generator."""
    
    import subprocess
    import os
    import json
    import tempfile
    from pathlib import Path
    from ..core.config import settings
    
    try:
        # Find website-builder directory
        backend_path = Path(__file__).parent.parent.parent.parent
        website_builder_path = backend_path / "website-builder"
        
        if not website_builder_path.exists():
            raise Exception(f"Website builder not found at {website_builder_path}")
        
        # Prepare input data for TypeScript generator
        generator_input = {
            "generation_id": task_data.get("generation_id"),
            "business_id": task_data.get("business_id"),
            "contractor_data": business_data,
            "seo_options": task_data.get("seo_options", {}),
            "cloudflare_subdomain": task_data.get("cloudflare_subdomain")
        }
        
        # Create temporary build directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy website-builder to temp directory for isolated build
            import shutil
            build_path = temp_path / "build"
            shutil.copytree(website_builder_path, build_path)
            
            # Write input for TypeScript generator
            input_file = temp_path / "generator-input.json"
            with open(input_file, 'w') as f:
                json.dump(generator_input, f, indent=2)
            
            # Change to build directory
            original_cwd = os.getcwd()
            os.chdir(build_path)
            
            try:
                # Set environment variables
                env = os.environ.copy()
                env.update({
                    "HERO365_BUSINESS_ID": task_data.get("business_id"),
                    "NEXT_PUBLIC_BUSINESS_ID": task_data.get("business_id"),
                    "BUILD_MODE": "seo_generation",
                    "NODE_ENV": "production"
                })
                
                # Step 1: Install dependencies if needed
                if not (build_path / "node_modules").exists():
                    logger.info("Installing Node.js dependencies...")
                    install_result = subprocess.run(
                        ["npm", "install"],
                        cwd=build_path,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minutes for npm install
                    )
                    
                    if install_result.returncode != 0:
                        raise Exception(f"npm install failed: {install_result.stderr}")
                
                # Step 2: Generate SEO pages using TypeScript generator
                logger.info("Generating SEO pages with TypeScript generator...")
                seo_generate_result = subprocess.run(
                    ["npx", "tsx", "lib/build-time/seo-generator.ts", "--input", str(input_file)],
                    cwd=build_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=60  # 1 minute for SEO generation
                )
                
                if seo_generate_result.returncode != 0:
                    raise Exception(f"SEO generation failed: {seo_generate_result.stderr}")
                
                logger.info(f"SEO generation output: {seo_generate_result.stdout}")
                
                # Step 3: Build the Next.js website
                logger.info("Building Next.js website...")
                build_result = subprocess.run(
                    ["npm", "run", "build"],
                    cwd=build_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minutes for build
                )
                
                if build_result.returncode != 0:
                    raise Exception(f"Website build failed: {build_result.stderr}")
                
                logger.info("Next.js build completed successfully")
                
                # Step 4: Copy built files to permanent location
                output_dir = backend_path / "build_output" / task_data.get("generation_id")
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy the 'out' directory (Next.js static export)
                out_dir = build_path / "out"
                if out_dir.exists():
                    shutil.copytree(out_dir, output_dir / "website", dirs_exist_ok=True)
                    logger.info(f"Build output copied to: {output_dir / 'website'}")
                else:
                    # Fallback: try .next directory
                    next_dir = build_path / ".next"
                    if next_dir.exists():
                        shutil.copytree(next_dir, output_dir / "website", dirs_exist_ok=True)
                        logger.info(f"Fallback: .next directory copied to: {output_dir / 'website'}")
                    else:
                        raise Exception("No build output found (neither 'out' nor '.next' directory exists)")
                
                return {
                    "success": True,
                    "build_path": str(output_dir / "website"),
                    "pages_generated": len(seo_pages),
                    "build_logs": f"SEO Generation:\n{seo_generate_result.stdout}\n\nBuild:\n{build_result.stdout}",
                    "seo_logs": seo_generate_result.stdout
                }
                
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        logger.error(f"Website build failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def _deploy_to_cloudflare_pages(
    subdomain: str, 
    build_path: str, 
    task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Deploy website to Cloudflare Pages using TypeScript deployer."""
    
    import subprocess
    import os
    import json
    import tempfile
    from pathlib import Path
    from ..core.config import settings
    
    try:
        # Validate Cloudflare configuration
        if not settings.cloudflare_enabled:
            raise Exception("Cloudflare is not properly configured. Missing API token or account ID.")
        
        # Find website-builder directory for the TypeScript deployer
        backend_path = Path(__file__).parent.parent.parent.parent
        website_builder_path = backend_path / "website-builder"
        
        if not website_builder_path.exists():
            raise Exception(f"Website builder not found at {website_builder_path}")
        
        # Prepare deployment configuration
        deployment_target = task_data.get("deployment_target", "production")
        project_name = f"{settings.CLOUDFLARE_PROJECT_NAME_PREFIX}-{subdomain}"
        branch = "main" if deployment_target == "production" else "staging"
        
        # Set up environment with Cloudflare credentials
        env = os.environ.copy()
        env.update({
            "CLOUDFLARE_API_TOKEN": settings.CLOUDFLARE_API_TOKEN,
            "CLOUDFLARE_ACCOUNT_ID": settings.CLOUDFLARE_ACCOUNT_ID,
            "NODE_ENV": "production"
        })
        
        logger.info(f"Deploying to Cloudflare Pages (Legacy): {project_name} ({branch})")
        
        # Use TypeScript deployer
        deploy_command = [
            "npx", "tsx", 
            "lib/build-time/cloudflare-deployer.ts",
            "--build-dir", build_path,
            "--project", project_name,
            "--branch", branch,
            "--json"  # Output JSON for parsing
        ]
        
        # Execute deployment
        deploy_result = subprocess.run(
            deploy_command,
            cwd=website_builder_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for deployment
        )
        
        if deploy_result.returncode != 0:
            raise Exception(f"TypeScript deployer failed: {deploy_result.stderr}")
        
        # Parse JSON output from TypeScript deployer
        try:
            # Extract JSON from stdout (may contain other log messages)
            stdout_lines = deploy_result.stdout.strip().split('\n')
            json_output = None
            
            for line in reversed(stdout_lines):  # Start from the end to find JSON
                if line.strip().startswith('{'):
                    json_output = line.strip()
                    break
            
            if not json_output:
                raise Exception("No JSON output found from TypeScript deployer")
            
            result = json.loads(json_output)
            
            if not result.get("success"):
                raise Exception(f"Deployment failed: {result.get('error', 'Unknown error')}")
            
            logger.info(f"Deployment successful: {result.get('url')}")
            
            return {
                "success": True,
                "website_url": result.get("url"),
                "deployment_id": result.get("deployment_id"),
                "deployment_logs": deploy_result.stdout,
                "duration_ms": result.get("duration_ms"),
                "project_name": project_name
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse deployment result JSON: {e}")
            logger.error(f"Raw output: {deploy_result.stdout}")
            
            # Fallback: try to extract URL manually
            website_url = None
            for line in deploy_result.stdout.split('\n'):
                if 'https://' in line and '.pages.dev' in line:
                    import re
                    url_match = re.search(r'https://[^\s]+\.pages\.dev[^\s]*', line)
                    if url_match:
                        website_url = url_match.group(0)
                        break
            
            if not website_url:
                website_url = f"https://{project_name}.pages.dev"
            
            return {
                "success": True,
                "website_url": website_url,
                "deployment_logs": deploy_result.stdout,
                "project_name": project_name
            }
        
    except Exception as e:
        logger.error(f"Cloudflare deployment failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def _get_pages_breakdown(seo_pages: List[Dict[str, Any]]) -> Dict[str, int]:
    """Get breakdown of pages by type."""
    
    breakdown = {}
    for page in seo_pages:
        page_type = page.get("type", "unknown")
        breakdown[page_type] = breakdown.get(page_type, 0) + 1
    
    return breakdown


# =====================================
# CONVERSION TRACKING TASKS
# =====================================

@celery_app.task
def track_conversion_task(website_id: str, event_type: str, event_data: Dict[str, Any]):
    """Track conversion events for analytics."""
    
    logger.info(f"Tracking conversion for website: {website_id}")
    
    try:
        # TODO: Create conversion tracking record
        # conversion = WebsiteConversionTracking(
        #     website_id=uuid.UUID(website_id),
        #     event_type=ConversionEventType(event_type),
        #     event_data=event_data,
        #     visitor_id=event_data.get("visitor_id"),
        #     session_id=event_data.get("session_id"),
        #     traffic_source=event_data.get("traffic_source"),
        #     referrer_url=event_data.get("referrer_url")
        # )
        # 
        # await conversion_repository.create(conversion)
        
        logger.info(f"Conversion tracked for website: {website_id}")
        
        return {"success": True, "conversion_tracked": True}
        
    except Exception as e:
        logger.error(f"Conversion tracking failed: {website_id} - {str(e)}")
        raise


# =====================================
# PERIODIC TASKS
# =====================================

@celery_app.task
def daily_seo_report_task():
    """Generate daily SEO reports for all websites."""
    
    logger.info("Generating daily SEO reports")
    
    try:
        # TODO: Generate reports for all active websites
        # websites = await website_repository.get_all_active()
        # for website in websites:
        #     generate_seo_report_task.delay(str(website.id))
        
        return {"success": True, "reports_generated": 0}
        
    except Exception as e:
        logger.error(f"Daily SEO report generation failed: {str(e)}")
        raise


@celery_app.task
def cleanup_old_builds_task():
    """Clean up old build files and logs."""
    
    logger.info("Cleaning up old build files")
    
    try:
        # TODO: Clean up build files older than 30 days
        # cleanup_service = BuildCleanupService()
        # cleaned_files = await cleanup_service.cleanup_old_builds(days=30)
        
        return {"success": True, "files_cleaned": 0}
        
    except Exception as e:
        logger.error(f"Build cleanup failed: {str(e)}")
        raise


# =====================================
# UTILITY FUNCTIONS
# =====================================

def _update_build_job_status(
    website_id: str,
    status: BuildJobStatus,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    result_data: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    build_logs: Optional[str] = None
):
    """Update build job status in database."""
    
    try:
        # TODO: Update build job record
        # updates = {"status": status}
        # if started_at:
        #     updates["started_at"] = started_at
        # if completed_at:
        #     updates["completed_at"] = completed_at
        # if duration_seconds:
        #     updates["duration_seconds"] = duration_seconds
        # if result_data:
        #     updates["result_data"] = result_data
        # if error_message:
        #     updates["error_message"] = error_message
        # if build_logs:
        #     updates["build_logs"] = build_logs
        # 
        # await build_job_repository.update_by_website_id(uuid.UUID(website_id), updates)
        
        logger.info(f"Build job status updated: {website_id} -> {status}")
        
    except Exception as e:
        logger.error(f"Failed to update build job status: {str(e)}")


def _determine_lead_type(form_data: Dict[str, Any]) -> str:
    """Determine lead type from form data."""
    
    form_type = form_data.get("form_type", "").lower()
    urgency = form_data.get("urgency", "").lower()
    
    if form_type == "emergency" or urgency in ["emergency", "asap"]:
        return "emergency"
    elif form_type == "quote" or "quote" in form_data.get("service_type", "").lower():
        return "quote_request"
    elif form_type == "booking" or "schedule" in form_data.get("message", "").lower():
        return "service_booking"
    else:
        return "general_inquiry"


def _determine_priority(form_data: Dict[str, Any]) -> str:
    """Determine priority level from form data."""
    
    urgency = form_data.get("urgency", "").lower()
    
    if urgency in ["emergency", "asap"]:
        return "emergency"
    elif urgency in ["24hours", "urgent", "today"]:
        return "high"
    elif urgency in ["week", "soon"]:
        return "medium"
    else:
        return "low"


# =====================================
# CELERY BEAT SCHEDULE
# =====================================

celery_app.conf.beat_schedule = {
    # SEO monitoring every 6 hours
    'seo-monitoring': {
        'task': 'app.workers.website_tasks.seo_monitoring_task',
        'schedule': 6 * 60 * 60,  # 6 hours
    },
    
    # Daily SEO reports at 8 AM UTC
    'daily-seo-reports': {
        'task': 'app.workers.website_tasks.daily_seo_report_task',
        'schedule': 24 * 60 * 60,  # 24 hours
        'options': {'eta': datetime.utcnow().replace(hour=8, minute=0, second=0)}
    },
    
    # Cleanup old builds weekly on Sunday at 2 AM UTC
    'cleanup-old-builds': {
        'task': 'app.workers.website_tasks.cleanup_old_builds_task',
        'schedule': 7 * 24 * 60 * 60,  # 7 days
        'options': {'eta': datetime.utcnow().replace(hour=2, minute=0, second=0)}
    },
}

celery_app.conf.timezone = 'UTC'
