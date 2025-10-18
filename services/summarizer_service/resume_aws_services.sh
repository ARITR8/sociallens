#!/usr/bin/env bash
set -euo pipefail

#############################################
# CONFIG — adjust if anything changes
#############################################
AWS_REGION="us-east-1"
VPC_ID="vpc-0e05ef1ac150dbd63"

# Where to create the NAT (public subnet)
NAT_PUBLIC_SUBNET_ID="subnet-0195c2f091f93e807"   # us-east-1f (public=True)

# Lambda subnets that need outbound Internet via NAT (private or no IGW route)
LAMBDA_SUBNET_IDS=(
  "subnet-0b3af88aec832c27e"   # summarizer
  "subnet-0195c2f091f93e807"   # summarizer
  "subnet-078d4366c53939dd4"   # fetcher
)

# RDS instance to start
DB_INSTANCE_ID="newsettler"

#############################################
# Helpers
#############################################
say() { echo -e "[+] $*"; }
warn() { echo -e "[!] $*" >&2; }
die() { echo -e "[x] $*" >&2; exit 1; }

awsq() { aws --region "$AWS_REGION" "$@"; }

# Deduplicate items printed one per line
unique() { awk '!seen[$0]++'; }

#############################################
# 0) Sanity checks
#############################################
say "Resuming AWS services in region: $AWS_REGION"
aws --version >/dev/null 2>&1 || die "AWS CLI not found."
awsq sts get-caller-identity >/dev/null || die "AWS CLI not authenticated."

#############################################
# 1) Start RDS (non-blocking)
#############################################
say "Starting RDS instance: $DB_INSTANCE_ID"
if ! awsq rds start-db-instance --db-instance-identifier "$DB_INSTANCE_ID" >/dev/null 2>&1; then
  warn "Could not start RDS (maybe already running). Continuing…"
fi

#############################################
# 2) Allocate a new Elastic IP for NAT
#############################################
say "Allocating a new Elastic IP for NAT Gateway…"
ALLOC_ID=$(awsq ec2 allocate-address --domain vpc --query 'AllocationId' --output text)
PUB_IP=$(awsq ec2 describe-addresses --allocation-ids "$ALLOC_ID" --query 'Addresses[0].PublicIp' --output text)
say "Allocated EIP: $PUB_IP (AllocationId: $ALLOC_ID)"

#############################################
# 3) (Re)Create NAT Gateway in the chosen public subnet
#############################################
say "Creating NAT Gateway in subnet: $NAT_PUBLIC_SUBNET_ID"
NAT_ID=$(awsq ec2 create-nat-gateway \
  --subnet-id "$NAT_PUBLIC_SUBNET_ID" \
  --allocation-id "$ALLOC_ID" \
  --query 'NatGateway.NatGatewayId' --output text)

say "NAT Gateway ID: $NAT_ID — waiting until AVAILABLE…"
awsq ec2 wait nat-gateway-available --nat-gateway-ids "$NAT_ID"
say "NAT Gateway is AVAILABLE."

#############################################
# 4) Find route tables attached to Lambda subnets
#############################################
say "Discovering route tables attached to Lambda subnets…"
ROUTE_TABLE_IDS=""

for SUBN in "${LAMBDA_SUBNET_IDS[@]}"; do
  # Get route table explicitly associated with subnet (if any)
  RTB=$(awsq ec2 describe-route-tables \
    --filters "Name=association.subnet-id,Values=$SUBN" \
    --query 'RouteTables[0].RouteTableId' --output text 2>/dev/null || echo "None")

  if [[ "$RTB" == "None" || "$RTB" == "NoneType" || -z "$RTB" ]]; then
    # Fallback to main route table for the VPC
    RTB=$(awsq ec2 describe-route-tables \
      --filters "Name=vpc-id,Values=$VPC_ID" \
      --query 'RouteTables[?Associations[?Main==`true`]].RouteTableId | [0]' \
      --output text 2>/dev/null || echo "None")
  fi

  if [[ "$RTB" != "None" && -n "$RTB" && "$RTB" != "null" ]]; then
    say "Subnet $SUBN -> Route Table $RTB"
    ROUTE_TABLE_IDS+="$RTB"$'\n'
  else
    warn "Could not resolve a route table for subnet $SUBN"
  fi
done

# Deduplicate route table IDs
mapfile -t UNIQUE_RTBS < <(printf "%s" "$ROUTE_TABLE_IDS" | unique)

if [[ ${#UNIQUE_RTBS[@]} -eq 0 ]]; then
  die "No route tables discovered for Lambda subnets; aborting route configuration."
fi

#############################################
# 5) Update default routes (0.0.0.0/0) in those RTs to point to the new NAT
#############################################
say "Updating 0.0.0.0/0 routes in discovered route tables to use NAT: $NAT_ID"

for RTB in "${UNIQUE_RTBS[@]}"; do
  # DO NOT modify public route tables that already have an Internet Gateway
  HAS_IGW=$(awsq ec2 describe-route-tables --route-table-ids "$RTB" \
    --query 'RouteTables[0].Routes[?GatewayId!=null && contains(GatewayId, `igw-`)] | length(@)' \
    --output text || echo 0)

  if [[ "$HAS_IGW" != "0" ]]; then
    say "Skipping public route table $RTB (has Internet Gateway route)."
    continue
  fi

  # Try replace-route; if it fails because it doesn't exist, create-route
  if awsq ec2 replace-route --route-table-id "$RTB" --destination-cidr-block 0.0.0.0/0 --nat-gateway-id "$NAT_ID" >/dev/null 2>&1; then
    say "Replaced default route in $RTB -> NAT $NAT_ID"
  else
    awsq ec2 create-route --route-table-id "$RTB" --destination-cidr-block 0.0.0.0/0 --nat-gateway-id "$NAT_ID" >/dev/null
    say "Created default route in $RTB -> NAT $NAT_ID"
  fi
done

#############################################
# 6) Wait for RDS to be available (optional but helpful)
#############################################
say "Waiting for RDS \"$DB_INSTANCE_ID\" to become available (this can take a few minutes)…"
if ! awsq rds wait db-instance-available --db-instance-identifier "$DB_INSTANCE_ID"; then
  warn "RDS did not reach 'available' yet. You can check status manually."
fi

#############################################
# 7) Summary
#############################################
say "===== RESUME SUMMARY ====="
say "RDS instance:   $DB_INSTANCE_ID   -> started (check status if needed)"
say "NAT Gateway:    $NAT_ID           -> in subnet $NAT_PUBLIC_SUBNET_ID"
say "Elastic IP:     $PUB_IP           -> allocation $ALLOC_ID"
say "Updated RTBs:   ${UNIQUE_RTBS[*]}"
say "======================================="
say "All set. Your Lambdas should have outbound Internet again."
