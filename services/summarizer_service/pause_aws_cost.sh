#!/bin/bash
echo "🚨 Pausing expensive AWS services to save cost..."

AWS_REGION="us-east-1"
DB_INSTANCE_ID="newsettler"
NAT_GATEWAY_ID="nat-07ebb61bce5627ab5"
ELASTIC_IP_ALLOC_ID="eipalloc-0a8a352a6c7d96d80"

echo "⏸️ Stopping RDS Instance: $DB_INSTANCE_ID ..."
aws rds stop-db-instance --db-instance-identifier $DB_INSTANCE_ID --region $AWS_REGION

echo "🧨 Deleting NAT Gateway: $NAT_GATEWAY_ID ..."
aws ec2 delete-nat-gateway --nat-gateway-id $NAT_GATEWAY_ID --region $AWS_REGION

echo "⏳ Waiting 30 seconds for NAT Gateway deletion..."
sleep 30

echo "💡 Releasing Elastic IP: $ELASTIC_IP_ALLOC_ID ..."
aws ec2 release-address --allocation-id $ELASTIC_IP_ALLOC_ID --region $AWS_REGION

echo "✅ COST PAUSE COMPLETE – You are no longer being charged for NAT or RDS."
