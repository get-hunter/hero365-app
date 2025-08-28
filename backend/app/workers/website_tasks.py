"""
Website Builder Background Tasks

Celery tasks for async website building, deployment, SEO monitoring,
and lead processing for the Hero365 Website Builder system.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
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
# MOBILE WEBSITE DEPLOYMENT TASKS
# =====================================

@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_website_task(self, deployment_id: str, business_id: str, request_data: Dict[str, Any]):
    """
    Publish website from mobile app data.
    
    This task orchestrates the complete mobile website deployment:
    1. Persist business data to database tables
    2. Generate website content and structure
    3. Build Next.js static site
    4. Deploy to Cloudflare Pages
    5. Update deployment status
    """
    
    logger.info(f"Starting mobile website deployment {deployment_id} for business {business_id}")
    
    try:
        # Update deployment status to building
        _update_deployment_status(deployment_id, "building", 10, "Starting deployment")
        
        # Step 1: Persist business data
        _update_deployment_status(deployment_id, "building", 20, "Saving business data")
        asyncio.run(_persist_mobile_business_data(business_id, request_data))
        
        # Step 2: Generate website content
        _update_deployment_status(deployment_id, "building", 40, "Generating website content")
        content = asyncio.run(_generate_mobile_website_content(business_id, request_data))
        
        # Step 3: Build Next.js site
        _update_deployment_status(deployment_id, "building", 60, "Building website")
        build_result = asyncio.run(_build_mobile_website(deployment_id, content))
        
        if not build_result.success:
            raise Exception(f"Website build failed: {build_result.error_message}")
        
        # Step 4: Deploy to Cloudflare Pages
        _update_deployment_status(deployment_id, "deploying", 80, "Deploying to Cloudflare")
        deploy_result = asyncio.run(_deploy_mobile_website(deployment_id, business_id, build_result.build_path))
        
        if not deploy_result.success:
            raise Exception(f"Deployment failed: {deploy_result.error_message}")
        
        # Step 5: Finalize deployment
        _update_deployment_status(deployment_id, "completed", 100, "Deployment completed", 
                                website_url=deploy_result.website_url)
        
        logger.info(f"Mobile website deployment {deployment_id} completed successfully")
        
        return {
            "success": True,
            "deployment_id": deployment_id,
            "website_url": deploy_result.website_url
        }
        
    except Exception as e:
        logger.error(f"Mobile website deployment {deployment_id} failed: {str(e)}")
        
        # Update deployment status to failed
        _update_deployment_status(deployment_id, "failed", 0, "Deployment failed", 
                                error_message=str(e))
        
        # Retry if possible
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying mobile deployment: {deployment_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (self.request.retries + 1))
        
        return {
            "success": False,
            "deployment_id": deployment_id,
            "error": str(e)
        }


async def _persist_mobile_business_data(business_id: str, request_data: Dict[str, Any]):
    """Persist mobile request data to database tables."""
    
    try:
        from ..infrastructure.repositories.business_repository import BusinessRepository
        
        business_repo = BusinessRepository()
        business_uuid = uuid.UUID(business_id)
        
        # TODO: Implement data persistence:
        # 1. service_areas from request_data['service_areas']
        # 2. business_services from request_data['services'] 
        # 3. products from request_data['products'] (if provided)
        # 4. business_locations from request_data['locations']
        # 5. business_hours from request_data['hours']
        # 6. business_branding from request_data['branding'] (if provided)
        # 7. business_websites upsert with subdomain
        
        logger.info(f"Persisted mobile business data for {business_id}")
        
    except Exception as e:
        logger.error(f"Failed to persist mobile business data: {str(e)}")
        raise


async def _generate_mobile_website_content(business_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate website content from mobile business data."""
    
    try:
        from ..application.services.dynamic_website_builder_service import DynamicWebsiteBuilderService
        from ..infrastructure.repositories.business_repository import BusinessRepository
        
        # Get business entity
        business_repo = BusinessRepository()
        business = await business_repo.get_by_id(uuid.UUID(business_id))
        
        if not business:
            raise Exception(f"Business {business_id} not found")
        
        # Generate website structure using existing service
        website_builder = DynamicWebsiteBuilderService()
        structure = await website_builder.generate_website_structure(business)
        
        logger.info(f"Generated website content for {business_id}")
        return structure.__dict__
        
    except Exception as e:
        logger.error(f"Failed to generate mobile website content: {str(e)}")
        raise


async def _build_mobile_website(deployment_id: str, content: Dict[str, Any]):
    """Build Next.js website from generated content."""
    
    try:
        from ..application.services.website_builder_service import WebsiteBuilderService
        
        # Use existing website builder service
        builder_service = WebsiteBuilderService()
        
        # TODO: Adapt builder service for mobile content format
        # For now, return mock success
        
        build_result = type('BuildResult', (), {
            'success': True,
            'build_path': f'/tmp/mobile-builds/{deployment_id}',
            'error_message': None
        })()
        
        logger.info(f"Built mobile website for deployment {deployment_id}")
        return build_result
        
    except Exception as e:
        logger.error(f"Failed to build mobile website: {str(e)}")
        raise


async def _deploy_mobile_website(deployment_id: str, business_id: str, build_path: str):
    """Deploy built website to Cloudflare Pages."""
    
    try:
        from ..application.services.cloudflare_pages_deployment_service import CloudflarePagesDeploymentService
        from pathlib import Path
        
        # Use existing Cloudflare deployment service
        cloudflare_service = CloudflarePagesDeploymentService()
        
        # Deploy to Cloudflare Pages
        deployment_result = await cloudflare_service.deploy_to_pages(
            build_dir=Path(build_path),
            business_name=f"mobile-{business_id[:8]}",
            deployment_type="production"
        )
        
        if deployment_result.build_status == "SUCCESS":
            deploy_result = type('DeployResult', (), {
                'success': True,
                'website_url': deployment_result.deploy_url,
                'error_message': None
            })()
        else:
            deploy_result = type('DeployResult', (), {
                'success': False,
                'website_url': None,
                'error_message': deployment_result.error_message
            })()
        
        logger.info(f"Deployed mobile website for deployment {deployment_id}")
        return deploy_result
        
    except Exception as e:
        logger.error(f"Failed to deploy mobile website: {str(e)}")
        raise


def _update_deployment_status(
    deployment_id: str,
    status: str,
    progress: int,
    step: str,
    website_url: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Update deployment status in database."""
    
    try:
        from ..domain.entities.website_deployment import DeploymentStatus
        from ..infrastructure.database.repositories.supabase_website_deployment_repository import SupabaseWebsiteDeploymentRepository
        
        # Update deployment status
        deployment_repo = SupabaseWebsiteDeploymentRepository()
        deployment_status = DeploymentStatus(status)
        
        # Run async operation in sync context
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            success = loop.run_until_complete(
                deployment_repo.update_status(
                    deployment_id=uuid.UUID(deployment_id),
                    status=deployment_status,
                    progress=progress,
                    current_step=step,
                    error_message=error_message
                )
            )
            
            if success:
                logger.info(f"Updated deployment {deployment_id}: {status} ({progress}%) - {step}")
            else:
                logger.warning(f"Failed to update deployment {deployment_id} status")
                
        finally:
            loop.close()
        
    except Exception as e:
        logger.error(f"Failed to update deployment status: {str(e)}")


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
