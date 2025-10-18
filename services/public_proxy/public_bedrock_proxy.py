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
        bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime', 
            region_name='us-east-1',
            config=boto3.session.Config(
                read_timeout=50,
                connect_timeout=10
            )
        )
        
        # Call Bedrock Agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId='IINTVS4ZZT',
            agentAliasId='TSTALIASID',
            sessionId='hackathon-demo-session',
            inputText=message
        )
        
        # Extract the AI-generated response from Bedrock Agent
        output_text = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    output_text += chunk['bytes'].decode('utf-8')
                elif 'text' in chunk:
                    output_text += chunk['text']
        
        # If still no output, try alternative extraction
        if not output_text.strip():
            # Try to get the final response from the completion
            for event in response['completion']:
                if 'trace' in event and 'trace' in event['trace']:
                    trace = event['trace']
                    if 'orchestrationTrace' in trace:
                        orchestration = trace['orchestrationTrace']
                        if 'modelInvocationInput' in orchestration:
                            model_input = orchestration['modelInvocationInput']
                            if 'text' in model_input:
                                output_text += model_input['text']
        
        # Fallback if still no output
        if not output_text.strip():
            output_text = "I received your request but couldn't generate a response. Please try again."
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
            },
            'body': json.dumps({
                'message': output_text,
                'source': 'AWS Bedrock Agent AI Response'
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
