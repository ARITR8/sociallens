# app/health/routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text  # Add this import
from app.core.database import get_db
import logging
import requests
import socket

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])

@router.get(
    "/",
    summary="Basic health check",
    description="Check if the service is running"
)
async def health_check():
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": "reddit-fetcher"
    }

@router.get(
    "/db",
    summary="Database health check",
    description="Check if database connection is working"
)
async def check_database(db: AsyncSession = Depends(get_db)):
    """Check database connectivity."""
    try:
        # Try a simple query using text()
        await db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "component": "database"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "component": "database",
            "error": str(e)
        }

@router.get(
    "/google-test",
    summary="Google connectivity test",
    description="Test if Lambda can reach Google"
)
async def test_google_connectivity():
    """Test if Lambda can reach Google."""
    logger.info("=== TESTING GOOGLE CONNECTIVITY ===")
    
    results = {
        "dns_resolution": False,
        "http_connectivity": False,
        "https_connectivity": False,
        "errors": []
    }
    
    try:
        # Test DNS resolution
        logger.info("Test 1: DNS Resolution for google.com")
        try:
            ip = socket.gethostbyname('google.com')
            results["dns_resolution"] = True
            results["google_ip"] = ip
            logger.info(f"✅ DNS Resolution: google.com -> {ip}")
        except Exception as e:
            logger.error(f"❌ DNS Resolution failed: {str(e)}")
            results["errors"].append(f"DNS: {str(e)}")
        
        # Test HTTP connectivity
        logger.info("Test 2: HTTP Connectivity to google.com")
        try:
            response = requests.get('http://google.com', timeout=10)
            results["http_connectivity"] = True
            results["http_status"] = response.status_code
            logger.info(f"✅ HTTP Connectivity: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ HTTP Connectivity failed: {str(e)}")
            results["errors"].append(f"HTTP: {str(e)}")
        
        # Test HTTPS connectivity
        logger.info("Test 3: HTTPS Connectivity to google.com")
        try:
            response = requests.get('https://google.com', timeout=10)
            results["https_connectivity"] = True
            results["https_status"] = response.status_code
            logger.info(f"✅ HTTPS Connectivity: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ HTTPS Connectivity failed: {str(e)}")
            results["errors"].append(f"HTTPS: {str(e)}")
            
    except Exception as e:
        logger.error(f"❌ Google connectivity test failed: {str(e)}")
        results["errors"].append(f"General: {str(e)}")
    
    logger.info(f"=== GOOGLE CONNECTIVITY TEST RESULTS ===")
    logger.info(f"DNS Resolution: {results['dns_resolution']}")
    logger.info(f"HTTP Connectivity: {results['http_connectivity']}")
    logger.info(f"HTTPS Connectivity: {results['https_connectivity']}")
    if results['errors']:
        logger.error(f"Errors: {results['errors']}")
    
    return results