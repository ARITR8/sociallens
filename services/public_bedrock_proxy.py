import json
import boto3
import os

def lambda_handler(event, context):
    # Extract message from API Gateway event
    try:
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '')
    except:
        message = event.get('queryStringParameters', {}).get('message', '')
    
    if not message:
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({'error': 'Message is required'})
        }
    
    try:
        # Initialize Bedrock Agent Runtime client
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # Call Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId='IINTVS4ZZT',
            agentAliasId='TSTALIASID',
            sessionId='hackathon-demo-session',
            inputText=message
        )
        
        # Process the response
        output_text = ""
        for event in response['completion']:
            if 'chunk' in event:
                output_text += event['chunk']['bytes'].decode('utf-8')
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': output_text,
                'source': 'AWS Bedrock Agent'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'error': str(e),
                'source': 'AWS Bedrock Agent'
            })
        }
