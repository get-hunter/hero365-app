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
        """Deploy website to a hero365.ai subdomain using dedicated S3 bucket."""
        
        try:
            if not subdomain:
                subdomain = website.subdomain
                
            if not subdomain:
                raise ValueError("Subdomain is required for deployment")
            
            full_domain = f"{subdomain}.{self.main_domain}"
            bucket_name = full_domain  # Use exact domain name as bucket name
            
            logger.info(f"Deploying website to {full_domain} using dedicated S3 bucket")
            
            # 1. Create and configure dedicated S3 bucket
            bucket_result = await self.create_subdomain_bucket(bucket_name)
            
            # 2. Upload website files to dedicated bucket
            upload_result = await self.upload_files_to_dedicated_bucket(build_path, bucket_name)
            
            # 3. Configure DNS to point to S3 website endpoint
            dns_result = await self.configure_subdomain_dns(subdomain)
            
            # 4. Verify deployment (optional, since no cache to invalidate)
            verification_result = await self.verify_subdomain_deployment(full_domain)
            
            return DeploymentResult(
                success=True,
                subdomain=subdomain,
                full_domain=full_domain,
                website_url=f"http://{full_domain}",  # S3 website hosting uses HTTP
                upload_result=upload_result,
                dns_configured=dns_result["success"],
                cache_invalidated=True,  # No cache to invalidate with direct S3
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
                relative_path_str = str(relative_path).replace('\\', '/')
                s3_key = f"{subdomain}/{relative_path_str}"
                
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
            # Create CNAME record pointing to dedicated S3 bucket website endpoint
            s3_website_endpoint = f"{subdomain}.{self.main_domain}.s3-website-us-east-1.amazonaws.com"
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
                                {'Value': s3_website_endpoint}
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
    
    async def create_subdomain_bucket(self, bucket_name: str) -> Dict[str, Any]:
        """Create and configure a dedicated S3 bucket for subdomain website hosting."""
        
        try:
            # Check if bucket already exists
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                logger.info(f"Bucket {bucket_name} already exists")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    # Create bucket
                    logger.info(f"Creating S3 bucket: {bucket_name}")
                    if settings.AWS_REGION == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': settings.AWS_REGION}
                        )
                else:
                    raise e
            
            # Configure bucket for website hosting
            self.s3_client.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': '404.html'}
                }
            )
            
            # Disable public access block
            self.s3_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )
            
            # Set bucket policy for public read access
            import json
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            
            self.s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            
            logger.info(f"Successfully configured bucket {bucket_name} for website hosting")
            return {"success": True, "bucket_name": bucket_name}
            
        except Exception as e:
            logger.error(f"Failed to create/configure bucket {bucket_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def upload_files_to_dedicated_bucket(self, build_path: str, bucket_name: str) -> Dict[str, Any]:
        """Upload website files to dedicated S3 bucket."""
        
        try:
            build_dir = Path(build_path)
            if not build_dir.exists():
                raise FileNotFoundError(f"Build directory not found: {build_path}")
            
            files_uploaded = 0
            total_size = 0
            
            # Upload all files from build directory
            for file_path in build_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path (no subdomain prefix needed)
                    relative_path = file_path.relative_to(build_dir)
                    s3_key = str(relative_path).replace('\\', '/')
                    
                    # Determine content type
                    content_type, _ = mimetypes.guess_type(str(file_path))
                    if not content_type:
                        content_type = 'application/octet-stream'
                    
                    # Upload file
                    self.s3_client.upload_file(
                        str(file_path),
                        bucket_name,
                        s3_key,
                        ExtraArgs={'ContentType': content_type}
                    )
                    
                    files_uploaded += 1
                    total_size += file_path.stat().st_size
                    
                    if files_uploaded % 10 == 0:
                        logger.info(f"Uploaded {files_uploaded} files...")
            
            total_size_mb = total_size / (1024 * 1024)
            logger.info(f"Successfully uploaded {files_uploaded} files ({total_size_mb:.2f} MB) to {bucket_name}")
            
            return {
                "success": True,
                "files_uploaded": files_uploaded,
                "total_size_mb": total_size_mb,
                "bucket_name": bucket_name
            }
            
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}")
            return {"success": False, "error": str(e)}
