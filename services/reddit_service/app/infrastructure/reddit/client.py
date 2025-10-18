# app/infrastructure/reddit/client.py
from datetime import datetime
from typing import List, Dict, Optional
import requests
import asyncio
import logging
import time
import socket
from app.core.config import Settings
from app.core.exceptions import RedditFetchError

logger = logging.getLogger(__name__)

class RedditClient:
    """Client for interacting with Reddit API."""

    def __init__(self):
        """Initialize Reddit client with credentials from settings."""
        settings = Settings()
        self.settings = settings
        
        # Force IPv4 connections
        self._setup_ipv4_only()
        
        # Prepare headers for Reddit API calls with proper formatting
        self.headers = {
            "Authorization": f"Bearer {settings.REDDIT_ACCESS_TOKEN}",
            "User-Agent": settings.REDDIT_USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }
        
        # Retry configuration
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.timeout = 60  # seconds
        
        logger.info("=== REDDIT CLIENT INITIALIZATION ===")
        logger.info(f"Access Token (first 20 chars): {settings.REDDIT_ACCESS_TOKEN[:20]}...")
        logger.info(f"User Agent: {settings.REDDIT_USER_AGENT}")
        logger.info(f"Headers: {self.headers}")
        logger.info(f"Max retries: {self.max_retries}, Timeout: {self.timeout}s")
        logger.info("Reddit client initialized with IPv4-only connections and retry logic")

    def _setup_ipv4_only(self):
        """Force IPv4 connections to avoid Reddit's IPv6 blocking."""
        try:
            # Monkey patch socket to force IPv4
            original_getaddrinfo = socket.getaddrinfo
            
            def ipv4_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
                # Force IPv4 (AF_INET = 2)
                return original_getaddrinfo(host, port, 2, type, proto, flags)
            
            socket.getaddrinfo = ipv4_getaddrinfo
            logger.info("✅ Forced IPv4-only connections")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not force IPv4: {str(e)}")

    def test_internet_connectivity(self) -> Dict:
        """Test basic internet connectivity from Lambda."""
        logger.info("=== TESTING INTERNET CONNECTIVITY ===")
        
        test_results = {
            "dns_resolution": False,
            "http_connectivity": False,
            "https_connectivity": False,
            "reddit_dns": False,
            "reddit_connectivity": False,
            "errors": []
        }
        
        try:
            # Test 1: DNS Resolution
            logger.info("Test 1: DNS Resolution")
            try:
                ip = socket.gethostbyname('google.com')
                logger.info(f"✅ DNS Resolution: google.com -> {ip}")
                test_results["dns_resolution"] = True
            except Exception as e:
                logger.error(f"❌ DNS Resolution failed: {str(e)}")
                test_results["errors"].append(f"DNS: {str(e)}")
            
            # Test 2: HTTP Connectivity
            logger.info("Test 2: HTTP Connectivity")
            try:
                response = requests.get('http://httpbin.org/get', timeout=10)
                logger.info(f"✅ HTTP Connectivity: {response.status_code}")
                test_results["http_connectivity"] = True
            except Exception as e:
                logger.error(f"❌ HTTP Connectivity failed: {str(e)}")
                test_results["errors"].append(f"HTTP: {str(e)}")
            
            # Test 3: HTTPS Connectivity
            logger.info("Test 3: HTTPS Connectivity")
            try:
                response = requests.get('https://httpbin.org/get', timeout=10)
                logger.info(f"✅ HTTPS Connectivity: {response.status_code}")
                test_results["https_connectivity"] = True
            except Exception as e:
                logger.error(f"❌ HTTPS Connectivity failed: {str(e)}")
                test_results["errors"].append(f"HTTPS: {str(e)}")
            
            # Test 4: Reddit DNS Resolution
            logger.info("Test 4: Reddit DNS Resolution")
            try:
                ip = socket.gethostbyname('oauth.reddit.com')
                logger.info(f"✅ Reddit DNS: oauth.reddit.com -> {ip}")
                test_results["reddit_dns"] = True
            except Exception as e:
                logger.error(f"❌ Reddit DNS failed: {str(e)}")
                test_results["errors"].append(f"Reddit DNS: {str(e)}")
            
            # Test 5: Reddit Connectivity (without auth)
            logger.info("Test 5: Reddit Connectivity")
            try:
                response = requests.get('https://oauth.reddit.com', timeout=10)
                logger.info(f"✅ Reddit Connectivity: {response.status_code}")
                test_results["reddit_connectivity"] = True
            except Exception as e:
                logger.error(f"❌ Reddit Connectivity failed: {str(e)}")
                test_results["errors"].append(f"Reddit: {str(e)}")
            
        except Exception as e:
            logger.error(f"❌ Connectivity test failed: {str(e)}")
            test_results["errors"].append(f"General: {str(e)}")
        
        logger.info(f"=== CONNECTIVITY TEST RESULTS ===")
        logger.info(f"DNS Resolution: {test_results['dns_resolution']}")
        logger.info(f"HTTP Connectivity: {test_results['http_connectivity']}")
        logger.info(f"HTTPS Connectivity: {test_results['https_connectivity']}")
        logger.info(f"Reddit DNS: {test_results['reddit_dns']}")
        logger.info(f"Reddit Connectivity: {test_results['reddit_connectivity']}")
        if test_results['errors']:
            logger.error(f"Errors: {test_results['errors']}")
        
        return test_results

    async def get_posts(
        self,
        subreddit: str,
        limit: int = 5,
        mode: str = "top",
        before: Optional[datetime] = None,
        fetch_comments: bool = True,
        comment_limit: int = 10
    ) -> List[Dict]:
        """
        Get posts from a subreddit with their top comments.
        
        Args:
            subreddit: Subreddit name
            limit: Maximum number of posts to fetch
            mode: Sorting mode (hot/new/top)
            before: Optional timestamp to fetch posts before
            fetch_comments: Whether to fetch comments
            comment_limit: Number of top comments to fetch per post
        """
        try:
            logger.info(f"=== GET_POSTS CALLED ===")
            logger.info(f"Subreddit: {subreddit}, Limit: {limit}, Mode: {mode}")
            
            # Run HTTP requests in a thread pool
            return await asyncio.get_event_loop().run_in_executor(
                None,
                self._fetch_posts_with_comments,
                subreddit,
                limit,
                mode,
                before,
                fetch_comments,
                comment_limit
            )
        except Exception as e:
            logger.error(f"Failed to fetch posts from r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to fetch posts: {str(e)}")

    def _make_request_with_retry(self, url: str, description: str = "API request") -> requests.Response:
        """Make HTTP request with retry logic for unstable networks."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"=== {description.upper()} (Attempt {attempt + 1}/{self.max_retries + 1}) ===")
                logger.info(f"URL: {url}")
                logger.info(f"Headers: {self.headers}")
                logger.info(f"Timeout: {self.timeout} seconds")
                logger.info(f"Force IPv4: Enabled")
                
                # Create session with IPv4-only configuration
                session = requests.Session()
                
                # Force IPv4 in the session
                adapter = requests.adapters.HTTPAdapter()
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                
                # Make the request with IPv4-only session
                response = session.get(
                    url, 
                    headers=self.headers, 
                    timeout=self.timeout,
                    allow_redirects=True
                )
                
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Check for rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                
                # Check for server errors that might be temporary
                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code}. Retrying...")
                    if attempt < self.max_retries:
                        delay = self.base_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Waiting {delay} seconds before retry...")
                        time.sleep(delay)
                        continue
                
                # Success or client error (don't retry client errors)
                response.raise_for_status()
                logger.info(f"✅ {description} successful on attempt {attempt + 1}")
                return response
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.error(f"❌ CONNECTION ERROR (Attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached for connection error")
                    
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.error(f"❌ TIMEOUT ERROR (Attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached for timeout error")
                    
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.error(f"❌ HTTP REQUEST ERROR (Attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached for HTTP error")
                    
            except Exception as e:
                last_exception = e
                logger.error(f"❌ UNEXPECTED ERROR (Attempt {attempt + 1}): {str(e)}")
                if attempt < self.max_retries:
                    delay = self.base_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached for unexpected error")
        
        # If we get here, all retries failed
        logger.error(f"❌ All {self.max_retries + 1} attempts failed for {description}")
        raise last_exception

    def _fetch_posts_with_comments(
        self,
        subreddit: str,
        limit: int,
        mode: str,
        before: Optional[datetime],
        fetch_comments: bool,
        comment_limit: int
    ) -> List[Dict]:
        """Synchronous method to fetch posts and comments using direct HTTP requests."""
        try:
            # TEMPORARY: Test internet connectivity first
            logger.info("=== RUNNING CONNECTIVITY TEST ===")
            connectivity_results = self.test_internet_connectivity()
            
            # If basic connectivity fails, return early with error info
            if not connectivity_results["dns_resolution"]:
                logger.error("❌ CRITICAL: DNS resolution failed - Lambda cannot resolve domain names")
                raise RedditFetchError("DNS resolution failed - check VPC DNS settings")
            
            if not connectivity_results["https_connectivity"]:
                logger.error("❌ CRITICAL: HTTPS connectivity failed - Lambda cannot reach external HTTPS sites")
                raise RedditFetchError("HTTPS connectivity failed - check network configuration")
            
            # Continue with existing code...
            # Test basic connectivity first
            logger.info("=== TESTING BASIC CONNECTIVITY ===")
            try:
                test_response = self._make_request_with_retry("https://httpbin.org/get", "Connectivity test")
                logger.info(f"✅ Basic connectivity test passed: {test_response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Basic connectivity test failed: {str(e)}")
                logger.info("Continuing with Reddit API call anyway...")
            
            # Fetch posts from Reddit API
            url = f"https://oauth.reddit.com/r/{subreddit}/{mode}?limit={limit}"
            
            logger.info("=== FETCHING REDDIT POSTS ===")
            response = self._make_request_with_retry(url, f"Reddit posts from r/{subreddit}")
            
            data = response.json()
            posts_data = data.get('data', {}).get('children', [])
            
            logger.info(f"✅ Successfully received {len(posts_data)} posts from Reddit API")
            
            if not posts_data:
                logger.warning(f"No posts found for r/{subreddit}")
                return []
            
            # Convert to our format
            post_list = []
            for i, post_wrapper in enumerate(posts_data):
                post = post_wrapper['data']
                
                logger.info(f"Processing post {i+1}: {post.get('title', 'No title')[:50]}...")
                
                # Skip if before timestamp provided and post is newer
                if before and post.get('created_utc', 0) >= before.timestamp():
                    continue

                post_data = {
                    "subreddit": post.get('subreddit'),
                    "title": post.get('title'),
                    "url": post.get('url'),
                    "author": post.get('author'),
                    "score": post.get('score', 0),
                    "num_comments": post.get('num_comments', 0),
                    "created_utc": post.get('created_utc', 0),
                    "is_self": post.get('is_self', False),
                    "over_18": post.get('over_18', False),
                    "post_text": post.get('selftext', ''),
                    "link_flair_text": post.get('link_flair_text'),
                    "post_type": "self" if post.get('is_self', False) else "link",
                    "domain": post.get('domain'),
                    "id": post.get('id'),
                    "permalink": post.get('permalink')
                }
                
                logger.debug(f"Post: {post_data['title']} - Score: {post_data['score']}")

                # Fetch top comments if requested
                if fetch_comments and post_data.get('id'):
                    try:
                        logger.info(f"Fetching comments for post {post_data['id']}...")
                        comments = self._fetch_post_comments(post_data['id'], comment_limit)
                        post_data["top_comments"] = comments
                        logger.info(f"✅ Fetched {len(comments)} comments for post {post_data['id']}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to fetch comments for post {post_data['id']}: {str(e)}")
                        post_data["top_comments"] = []
                else:
                    post_data["top_comments"] = []
                
                post_list.append(post_data)

            logger.info(f"✅ Successfully processed {len(post_list)} posts from r/{subreddit}")
            return post_list
            
        except Exception as e:
            logger.error(f"❌ CRITICAL ERROR in _fetch_posts_with_comments: {str(e)}")
            raise RedditFetchError(f"Failed to fetch posts: {str(e)}")

    def _fetch_post_comments(self, post_id: str, comment_limit: int) -> List[Dict]:
        """Fetch comments for a specific post with retry logic."""
        try:
            url = f"https://oauth.reddit.com/comments/{post_id}.json?limit={comment_limit}&sort=top"
            logger.info(f"=== FETCHING COMMENTS FOR POST {post_id} ===")
            
            response = self._make_request_with_retry(url, f"Comments for post {post_id}")
            
            data = response.json()
            comments_data = data[1]['data']['children'] if len(data) > 1 else []
            
            comments = []
            for comment_wrapper in comments_data[:comment_limit]:
                comment = comment_wrapper['data']
                
                # Skip deleted/removed comments
                if comment.get('body') in ['[deleted]', '[removed]']:
                    continue
                
                comment_data = {
                    "id": comment.get('id'),
                    "author": comment.get('author'),
                    "body": comment.get('body', ''),
                    "score": comment.get('score', 0),
                    "created_at": datetime.fromtimestamp(comment.get('created_utc', 0)).isoformat(),
                    "is_submitter": comment.get('is_submitter', False)
                }
                comments.append(comment_data)
            
            logger.info(f"✅ Successfully fetched {len(comments)} comments")
            return comments
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to fetch comments for post {post_id}: {str(e)}")
            return []

    async def get_subreddit_info(self, subreddit: str) -> Dict:
        """Get information about a subreddit."""
        try:
            logger.info(f"=== GET_SUBREDDIT_INFO ===")
            logger.info(f"Subreddit: {subreddit}")
            
            return await asyncio.get_event_loop().run_in_executor(
                None,
                self._fetch_subreddit_info,
                subreddit
            )
        except Exception as e:
            logger.error(f"Failed to fetch info for r/{subreddit}: {str(e)}")
            raise RedditFetchError(f"Failed to fetch subreddit info: {str(e)}")

    def _fetch_subreddit_info(self, subreddit: str) -> Dict:
        """Synchronous method to fetch subreddit information."""
        try:
            url = f"https://oauth.reddit.com/r/{subreddit}/about.json"
            logger.info(f"=== FETCHING SUBREDDIT INFO ===")
            
            response = self._make_request_with_retry(url, f"Subreddit info for r/{subreddit}")
            
            data = response.json()
            subreddit_data = data.get('data', {})
            
            return {
                "display_name": subreddit_data.get('display_name'),
                "title": subreddit_data.get('title'),
                "description": subreddit_data.get('description'),
                "subscribers": subreddit_data.get('subscribers', 0),
                "created_utc": subreddit_data.get('created_utc', 0),
                "over18": subreddit_data.get('over18', False),
                "public": subreddit_data.get('subreddit_type') == "public"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch subreddit info: {str(e)}")
            raise RedditFetchError(f"Failed to fetch subreddit info: {str(e)}")