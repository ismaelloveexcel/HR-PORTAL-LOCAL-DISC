#!/bin/bash
set -e

# PostgreSQL High Availability Configuration Script
# Addresses Azure Advisor recommendations for production workloads

RESOURCE_GROUP="BaynunahHR"
SERVER_NAME="baynunahhrportal-server"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     PostgreSQL High Availability Configuration                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check current configuration
echo "📋 Current Configuration:"
az postgres flexible-server show \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --query "{Name:name, Tier:sku.tier, Compute:sku.name, Location:location, HAEnabled:highAvailability.mode, BackupRetention:backup.backupRetentionDays, GeoRedundant:backup.geoRedundantBackup}" \
  --output table

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Azure Advisor Recommendations:"
echo ""
echo "1. ⚡ Enable Zone-Redundant High Availability"
echo "   - Provides automatic failover to standby server in different zone"
echo "   - 99.99% SLA (vs 99.9% without HA)"
echo "   - Zero data loss during failover"
echo "   - Cost: Doubles compute costs (2x server instances)"
echo "   - Recommended for: Production workloads requiring minimal downtime"
echo ""
echo "2. 🌍 Enable Geo-Redundant Backup Storage"
echo "   - Backups replicated to paired Azure region"
echo "   - Disaster recovery capability (restore in different region)"
echo "   - Cost: ~2x backup storage costs"
echo "   - Recommended for: Critical data requiring regional disaster recovery"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cost estimation
echo "💰 Estimated Additional Monthly Costs (UAE North region):"
echo ""
echo "Current (Burstable B1ms - 1 vCore, 2GB RAM):"
echo "  - Compute: ~$15-20/month"
echo "  - Storage (32GB): ~$5/month"
echo "  - Backup: ~$2/month"
echo "  - TOTAL: ~$22-27/month"
echo ""
echo "With High Availability (Zone Redundant):"
echo "  - Compute: ~$30-40/month (2x instances)"
echo "  - Storage: ~$5/month (shared)"
echo "  - Backup: ~$2/month"
echo "  - TOTAL: ~$37-47/month (+$15-20/month)"
echo ""
echo "With Geo-Redundant Backup (add-on):"
echo "  - Additional backup cost: ~$2-4/month"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Recommendations based on workload
echo "📊 Recommendation for HR Portal (Startup/Solo HR):"
echo ""
echo "✅ START WITH (Minimal Cost):"
echo "   - Current setup is sufficient for development/testing"
echo "   - 7-day backup retention (already configured)"
echo "   - Regular point-in-time recovery available"
echo "   - Cost: Current (~$25/month)"
echo ""
echo "⚠️  CONSIDER FOR PRODUCTION:"
echo "   - Enable Geo-Redundant Backup ONLY (if multi-country operations)"
echo "   - Cost: +$2-4/month"
echo "   - Provides disaster recovery without doubling compute costs"
echo ""
echo "🚀 RECOMMENDED FOR CRITICAL PRODUCTION:"
echo "   - Enable Zone-Redundant HA + Geo-Redundant Backup"
echo "   - Cost: +$17-24/month"
echo "   - 99.99% SLA with regional disaster recovery"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ask user what to do
echo "What would you like to do?"
echo ""
echo "1) Keep current setup (no changes, dismiss recommendations)"
echo "2) Enable Geo-Redundant Backup only (+$2-4/month)"
echo "3) Enable Zone-Redundant HA only (+$15-20/month)"
echo "4) Enable BOTH HA + Geo-Redundant Backup (+$17-24/month)"
echo "5) Exit without changes"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
  1)
    echo ""
    echo "✅ Keeping current configuration (cost-optimized for startup)"
    echo "   Dismiss Azure Advisor recommendations in Azure Portal"
    ;;
    
  2)
    echo ""
    echo "⏳ Enabling Geo-Redundant Backup..."
    az postgres flexible-server update \
      --resource-group $RESOURCE_GROUP \
      --name $SERVER_NAME \
      --geo-redundant-backup Enabled \
      --output none
    echo "✅ Geo-Redundant Backup enabled"
    echo "   Backups will now replicate to paired region"
    ;;
    
  3)
    echo ""
    echo "⏳ Enabling Zone-Redundant High Availability..."
    echo "   This will create a standby server in a different zone..."
    echo "   ⚠️  Operation takes 10-15 minutes and may cause brief downtime"
    read -p "Continue? (y/n): " confirm
    if [[ $confirm == "y" ]]; then
      az postgres flexible-server update \
        --resource-group $RESOURCE_GROUP \
        --name $SERVER_NAME \
        --high-availability ZoneRedundant \
        --output none
      echo "✅ High Availability enabled"
      echo "   SLA upgraded to 99.99%"
    else
      echo "❌ Operation cancelled"
    fi
    ;;
    
  4)
    echo ""
    echo "⏳ Enabling BOTH High Availability + Geo-Redundant Backup..."
    echo "   ⚠️  Operation takes 10-15 minutes and may cause brief downtime"
    read -p "Continue? (y/n): " confirm
    if [[ $confirm == "y" ]]; then
      # Enable HA first
      az postgres flexible-server update \
        --resource-group $RESOURCE_GROUP \
        --name $SERVER_NAME \
        --high-availability ZoneRedundant \
        --output none
      
      # Then enable geo-redundant backup
      az postgres flexible-server update \
        --resource-group $RESOURCE_GROUP \
        --name $SERVER_NAME \
        --geo-redundant-backup Enabled \
        --output none
        
      echo "✅ High Availability + Geo-Redundant Backup enabled"
      echo "   99.99% SLA with regional disaster recovery"
    else
      echo "❌ Operation cancelled"
    fi
    ;;
    
  5)
    echo ""
    echo "❌ Exiting without changes"
    exit 0
    ;;
    
  *)
    echo ""
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Updated Configuration:"
az postgres flexible-server show \
  --resource-group $RESOURCE_GROUP \
  --name $SERVER_NAME \
  --query "{Name:name, HAMode:highAvailability.mode, HAState:highAvailability.state, GeoRedundantBackup:backup.geoRedundantBackup, BackupRetention:backup.backupRetentionDays}" \
  --output table

echo ""
echo "✅ Configuration complete!"
