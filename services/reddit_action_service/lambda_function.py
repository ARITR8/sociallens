import json
import requests
import os

def lambda_handler(event, context):
    # Log the incoming event
    print(f"=== INCOMING EVENT ===")
    print(json.dumps(event, indent=2))
    
    # Extract API path and method from the event
    api_path = event.get("apiPath", "/getPosts")
    http_method = event.get("httpMethod", "POST")
    
    # Extract subreddit correctly from bedrock request
    subreddit = "Python"  # Default
    
    try:
        properties = event.get("requestBody", {}).get("content", {}).get("application/json", {}).get("properties", [])
        print(f"=== PROPERTIES ===")
        print(json.dumps(properties, indent=2))
        
        for prop in properties:
            if prop.get("name") == "subreddit":
                subreddit = prop.get("value", "Python")
                print(f"=== FOUND SUBREDDIT ===")
                print(f"Subreddit: {subreddit}")
                break
    except Exception as e:
        print(f"=== ERROR EXTRACTING SUBREDDIT ===")
        print(f"Error: {str(e)}")
        subreddit = "Python"  # Fallback

    limit = 1
    mode = "hot"

    reddit_url = f"https://wzlvrmaf3d.execute-api.us-east-1.amazonaws.com/prod/api/v1/fetcher/posts/{subreddit}?limit={limit}&mode={mode}"
    print(f"=== REDDIT URL ===")
    print(f"URL: {reddit_url}")

    try:
        response = requests.get(reddit_url, timeout=30)
        print(f"=== REDDIT API RESPONSE ===")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            posts = response.json()
            print(f"=== POSTS DATA ===")
            print(f"Posts count: {len(posts) if posts else 0}")
            
            if posts and len(posts) > 0:
                post = posts[0]
                
                # Create detailed summary with post text and comments (same format as before)
                summary = f"Top post from r/{subreddit}:\n\n"
                summary += f"📝 {post.get('title', 'No title')}\n"
                summary += f"👤 Author: {post.get('author', 'Unknown')}\n"
                summary += f"⭐ Score: {post.get('score', 0)}\n"
                summary += f"💬 Comments: {post.get('comments', 0)}\n"
                summary += f"🔗 {post.get('url', 'No URL')}\n\n"
                
                # Add post text if available
                if post.get('post_text'):
                    summary += f"📄 Post Content:\n{post.get('post_text', '')[:300]}{'...' if len(post.get('post_text', '')) > 300 else ''}\n\n"
                
                # Add top comments if available
                if post.get('top_comments') and len(post.get('top_comments', [])) > 0:
                    summary += f"💬 Top Comments:\n"
                    for i, comment in enumerate(post.get('top_comments', [])[:2], 1):
                        comment_text = comment.get('body', '')[:150]
                        if len(comment.get('body', '')) > 150:
                            comment_text += '...'
                        summary += f"{i}. {comment.get('author', 'Unknown')}: {comment_text}\n"
            else:
                summary = f"No posts found in r/{subreddit}"
        else:
            summary = f"Error: Reddit API returned {response.status_code}"

        print(f"=== FINAL SUMMARY ===")
        print(f"Summary: {summary}")

        # Return EXACT same format as before (this is what Bedrock Agent expects)
        result = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "getRedditPost",
                "apiPath": api_path,
                "httpMethod": http_method,
                "httpStatusCode": 200,
                "responseBody": {
                    "application/json": {
                        "body": summary
                    }
                }
            }
        }
        
        print(f"=== RETURNING RESULT ===")
        print(json.dumps(result, indent=2))
        
        return result

    except Exception as e:
        error_msg = f"Error fetching subreddit {subreddit}: {str(e)}"
        print(f"=== EXCEPTION ===")
        print(f"Error: {error_msg}")
        
        result = {
            "messageVersion": "1.0",
            "response": {
                "actionGroup": "getRedditPost",
                "apiPath": api_path,
                "httpMethod": http_method,
                "httpStatusCode": 500,
                "responseBody": {
                    "application/json": {
                        "body": error_msg
                    }
                }
            }
        }
        
        print(f"=== RETURNING ERROR RESULT ===")
        print(json.dumps(result, indent=2))
        
        return result
