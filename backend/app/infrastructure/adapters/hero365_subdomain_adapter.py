"""
Hero365 Subdomain Infrastructure Adapter

Pure infrastructure implementation for Hero365 subdomain deployment.
Contains only external service communication - no business logic.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import mimetypes

import httpx
import boto3
from botocore.exceptions import ClientError

from ...core.config import settings
from ...domain.entities.website import BusinessWebsite
from ...application.ports.subdomain_hosting_port import (
    SubdomainHostingPort, SubdomainInfo, DeploymentResult, SubdomainAnalytics
)

logger = logging.getLogger(__name__)


class Hero365SubdomainAdapter(SubdomainHostingPort):
    """
    Infrastructure adapter for Hero365 subdomain deployment.
    
    Pure infrastructure implementation - only handles external service communication.
    All business logic is delegated to domain services.
    """
    
    def __init__(self):
        # Initialize AWS clients
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        self.route53_client = boto3.client(
            'route53',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        
        # Hero365 configuration
        self.main_domain = "hero365.ai"
        self.main_bucket = "hero365-websites"
        self.cloudfront_distribution_id = settings.HERO365_CLOUDFRONT_DISTRIBUTION_ID
        self.route53_hosted_zone_id = settings.HERO365_ROUTE53_ZONE_ID
        self.cloudfront_domain = settings.HERO365_CLOUDFRONT_DOMAIN
    
    async def deploy_to_subdomain(
        self,
        website: BusinessWebsite,
        build_path: str,
        subdomain: Optional[str] = None
    ) -> DeploymentResult:
        """Deploy website to a hero365.ai subdomain via AWS services."""
        
        try:
            if not subdomain:
                subdomain = website.subdomain
                
            if not subdomain:
                raise ValueError("Subdomain is required for deployment")
            
            full_domain = f"{subdomain}.{self.main_domain}"
            
            logger.info(f"Deploying website to {full_domain}")
            
            # 1. Upload website files to S3
            upload_result = await self.upload_files_to_subdomain(build_path, subdomain)
            
            # 2. Configure DNS
            dns_result = await self.configure_subdomain_dns(subdomain)
            
            # 3. Invalidate cache
            invalidation_result = await self.invalidate_subdomain_cache(subdomain)
            
            # 4. Verify deployment
            verification_result = await self.verify_subdomain_deployment(full_domain)
            
            return DeploymentResult(
                success=True,
                subdomain=subdomain,
                full_domain=full_domain,
                website_url=f"https://{full_domain}",
                upload_result=upload_result,
                dns_configured=dns_result["success"],
                cache_invalidated=invalidation_result["success"],
                deployment_verified=verification_result["success"],
                deployed_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ Subdomain deployment failed: {str(e)}")
            return DeploymentResult(
                success=False,
                error=str(e),
                subdomain=subdomain
            )
    
    async def list_subdomains(self) -> Dict[str, Any]:
        """List all active subdomains from S3."""
        
        try:
            # API call to list S3 prefixes
            response = self.s3_client.list_objects_v2(
                Bucket=self.main_bucket,
                Delimiter='/',
                MaxKeys=1000
            )
            
            subdomains = []
            
            for prefix in response.get('CommonPrefixes', []):
                subdomain = prefix['Prefix'].rstrip('/')
                
                # Get subdomain info via API
                subdomain_info = await self.get_subdomain_info(subdomain)
                subdomains.append(subdomain_info.dict())
            
            return {
                "success": True,
                "total_subdomains": len(subdomains),
                "subdomains": subdomains
            }
            
        except Exception as e:
            logger.error(f"Failed to list subdomains: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_subdomain(self, subdomain: str) -> Dict[str, Any]:
        """Delete a subdomain and all its files via AWS APIs."""
        
        try:
            logger.info(f"Deleting subdomain: {subdomain}")
            
            # 1. Delete files from S3
            delete_result = await self._delete_subdomain_files(subdomain)
            
            # 2. Remove DNS record
            dns_result = await self._delete_subdomain_dns(subdomain)
            
            # 3. Invalidate cache
            invalidation_result = await self.invalidate_subdomain_cache(subdomain)
            
            return {
                "success": True,
                "subdomain": subdomain,
                "files_deleted": delete_result["files_deleted"],
                "dns_removed": dns_result["success"],
                "cache_invalidated": invalidation_result["success"],
                "deleted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to delete subdomain {subdomain}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subdomain": subdomain
            }
    
    async def update_subdomain(
        self,
        subdomain: str,
        build_path: str
    ) -> Dict[str, Any]:
        """Update an existing subdomain with new content via AWS APIs."""
        
        try:
            logger.info(f"Updating subdomain: {subdomain}")
            
            # 1. Upload new files
            upload_result = await self.upload_files_to_subdomain(build_path, subdomain)
            
            # 2. Invalidate cache
            invalidation_result = await self.invalidate_subdomain_cache(subdomain)
            
            return {
                "success": True,
                "subdomain": subdomain,
                "files_updated": upload_result["files_uploaded"],
                "cache_invalidated": invalidation_result["success"],
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to update subdomain {subdomain}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subdomain": subdomain
            }
    
    async def get_subdomain_info(self, subdomain: str) -> SubdomainInfo:
        """Get information about a subdomain from S3."""
        
        try:
            # API call to get S3 objects
            response = self.s3_client.list_objects_v2(
                Bucket=self.main_bucket,
                Prefix=f"{subdomain}/",
                MaxKeys=1000
            )
            
            files = response.get('Contents', [])
            total_size = sum(obj['Size'] for obj in files)
            last_modified = max(obj['LastModified'] for obj in files) if files else None
            
            return SubdomainInfo(
                subdomain=subdomain,
                full_domain=f"{subdomain}.{self.main_domain}",
                website_url=f"https://{subdomain}.{self.main_domain}",
                file_count=len(files),
                total_size_mb=total_size / 1024 / 1024,
                last_modified=last_modified.isoformat() if last_modified else None,
                status="active"
            )
            
        except Exception as e:
            return SubdomainInfo(
                subdomain=subdomain,
                full_domain=f"{subdomain}.{self.main_domain}",
                website_url=f"https://{subdomain}.{self.main_domain}",
                file_count=0,
                total_size_mb=0.0,
                status="error",
                error=str(e)
            )
    
    async def get_subdomain_analytics(self, subdomain: str) -> SubdomainAnalytics:
        """Get analytics data for a subdomain (mock implementation)."""
        
        try:
            # TODO: Integrate with CloudWatch or analytics service
            # For now, return mock data structure
            
            return SubdomainAnalytics(
                subdomain=subdomain,
                period="last_7_days",
                page_views=156,
                unique_visitors=89,
                bounce_rate=42.3,
                avg_session_duration=125,
                top_pages=[
                    {"path": "/", "views": 89},
                    {"path": "/services", "views": 34},
                    {"path": "/contact", "views": 23}
                ],
                traffic_sources={
                    "direct": 45,
                    "search": 67,
                    "social": 12,
                    "referral": 32
                }
            )
            
        except Exception as e:
            logger.error(f"Analytics fetch failed: {str(e)}")
            return SubdomainAnalytics(
                subdomain=subdomain,
                period="last_7_days",
                error=str(e)
            )
    
    async def verify_subdomain_deployment(self, full_domain: str) -> Dict[str, Any]:
        """Verify that subdomain is accessible via HTTP request."""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://{full_domain}",
                    timeout=10.0,
                    follow_redirects=True
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "content_length": len(response.content)
                }
                
        except Exception as e:
            logger.error(f"Deployment verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def upload_files_to_subdomain(
        self,
        build_path: str,
        subdomain: str
    ) -> Dict[str, Any]:
        """Upload website files to S3 with subdomain prefix."""
        
        try:
            build_dir = Path(build_path)
            if not build_dir.exists():
                raise Exception(f"Build directory not found: {build_path}")
            
            files_uploaded = 0
            total_size = 0
            
            # Get all files to upload
            files_to_upload = list(build_dir.rglob('*'))
            files_to_upload = [f for f in files_to_upload if f.is_file()]
            
            logger.info(f"Uploading {len(files_to_upload)} files for subdomain {subdomain}")
            
            for file_path in files_to_upload:
                # Calculate S3 key with subdomain prefix
                relative_path = file_path.relative_to(build_dir)
                s3_key = f"{subdomain}/{str(relative_path).replace('\\', '/')}"
                
                # Determine content type
                content_type, _ = mimetypes.guess_type(str(file_path))
                if not content_type:
                    content_type = 'application/octet-stream'
                
                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                total_size += len(file_content)
                
                # API call to upload to S3
                self.s3_client.put_object(
                    Bucket=self.main_bucket,
                    Key=s3_key,
                    Body=file_content,
                    ContentType=content_type,
                    CacheControl='max-age=86400'  # 24 hours
                )
                
                files_uploaded += 1
                
                if files_uploaded % 10 == 0:
                    logger.info(f"Uploaded {files_uploaded}/{len(files_to_upload)} files...")
            
            logger.info(f"Successfully uploaded {files_uploaded} files ({total_size / 1024 / 1024:.2f} MB)")
            
            return {
                "success": True,
                "files_uploaded": files_uploaded,
                "total_size_mb": total_size / 1024 / 1024,
                "s3_prefix": subdomain
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def configure_subdomain_dns(self, subdomain: str) -> Dict[str, Any]:
        """Create DNS record for subdomain via Route53 API."""
        
        try:
            # Create CNAME record pointing to CloudFront distribution
            change_batch = {
                'Comment': f'Hero365 subdomain: {subdomain}',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': f'{subdomain}.{self.main_domain}',
                            'Type': 'CNAME',
                            'TTL': 300,
                            'ResourceRecords': [
                                {'Value': self.cloudfront_domain}
                            ]
                        }
                    }
                ]
            }
            
            # API call to Route53
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=self.route53_hosted_zone_id,
                ChangeBatch=change_batch
            )
            
            change_id = response['ChangeInfo']['Id']
            logger.info(f"DNS record created for {subdomain}: {change_id}")
            
            return {
                "success": True,
                "change_id": change_id,
                "dns_name": f'{subdomain}.{self.main_domain}'
            }
            
        except ClientError as e:
            logger.error(f"DNS creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def invalidate_subdomain_cache(self, subdomain: str) -> Dict[str, Any]:
        """Invalidate CloudFront cache for subdomain path via API."""
        
        try:
            # API call to CloudFront
            response = self.cloudfront_client.create_invalidation(
                DistributionId=self.cloudfront_distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': 1,
                        'Items': [f'/{subdomain}/*']
                    },
                    'CallerReference': f'hero365-{subdomain}-{int(datetime.utcnow().timestamp())}'
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            logger.info(f"Cache invalidation created for {subdomain}: {invalidation_id}")
            
            return {
                "success": True,
                "invalidation_id": invalidation_id
            }
            
        except ClientError as e:
            logger.error(f"Cache invalidation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # =====================================
    # HELPER METHODS (Infrastructure Only)
    # =====================================
    
    async def _delete_subdomain_files(self, subdomain: str) -> Dict[str, Any]:
        """Delete all files for a subdomain from S3."""
        
        try:
            # API call to list objects
            response = self.s3_client.list_objects_v2(
                Bucket=self.main_bucket,
                Prefix=f"{subdomain}/",
                MaxKeys=1000
            )
            
            objects = response.get('Contents', [])
            
            if objects:
                # API call to delete objects in batches
                delete_keys = [{'Key': obj['Key']} for obj in objects]
                
                self.s3_client.delete_objects(
                    Bucket=self.main_bucket,
                    Delete={'Objects': delete_keys}
                )
                
                logger.info(f"Deleted {len(delete_keys)} files for subdomain {subdomain}")
            
            return {
                "success": True,
                "files_deleted": len(objects)
            }
            
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "files_deleted": 0
            }
    
    async def _delete_subdomain_dns(self, subdomain: str) -> Dict[str, Any]:
        """Delete DNS record for subdomain via Route53 API."""
        
        try:
            # API call to delete CNAME record
            change_batch = {
                'Comment': f'Delete Hero365 subdomain: {subdomain}',
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': f'{subdomain}.{self.main_domain}',
                            'Type': 'CNAME',
                            'TTL': 300,
                            'ResourceRecords': [
                                {'Value': self.cloudfront_domain}
                            ]
                        }
                    }
                ]
            }
            
            response = self.route53_client.change_resource_record_sets(
                HostedZoneId=self.route53_hosted_zone_id,
                ChangeBatch=change_batch
            )
            
            return {
                "success": True,
                "change_id": response['ChangeInfo']['Id']
            }
            
        except ClientError as e:
            # DNS record might not exist, which is fine
            logger.warning(f"DNS deletion warning: {str(e)}")
            return {
                "success": True,
                "warning": str(e)
            }
