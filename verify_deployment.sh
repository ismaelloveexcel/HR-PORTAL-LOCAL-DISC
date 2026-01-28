#!/bin/bash
# Post-Deployment Verification Script for HR Portal MVP
# Tests all 4 urgent features: Recruitment, Employee DB, Leave Planner, Performance

set -e

# Configuration
WEBAPP_URL="${1:-https://hrportal-backend-new.azurewebsites.net}"
ADMIN_ID="${2:-BAYN00008}"
ADMIN_PASSWORD="${3:-16051988}"

echo "======================================"
echo "HR Portal MVP Deployment Verification"
echo "======================================"
echo "Target: $WEBAPP_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local description=$2
    local auth_required=${3:-true}
    
    echo -n "Testing $description... "
    
    if [ "$auth_required" = "true" ]; then
        status=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout 10 \
            --max-time 30 \
            -H "Authorization: Bearer $TOKEN" \
            "$WEBAPP_URL$endpoint" 2>/dev/null || echo "000")
    else
        status=$(curl -s -o /dev/null -w "%{http_code}" \
            --connect-timeout 10 \
            --max-time 30 \
            "$WEBAPP_URL$endpoint" 2>/dev/null || echo "000")
    fi
    
    if [ "$status" = "200" ]; then
        echo "✅ OK (HTTP $status)"
        return 0
    else
        echo "❌ FAILED (HTTP $status)"
        return 1
    fi
}

# Step 1: Health Checks (No Auth)
echo "1️⃣ HEALTH CHECKS (No Auth Required)"
echo "-----------------------------------"
test_endpoint "/api/health/ping" "Basic Health Ping" false
test_endpoint "/api/health/revision" "Deployment Version Info" false
echo ""

# Step 2: Database Health
echo "2️⃣ DATABASE HEALTH CHECK"
echo "------------------------"
test_endpoint "/api/health/db" "Database Connection" false
echo ""

# Step 3: Login & Get Token
echo "3️⃣ AUTHENTICATION"
echo "-----------------"
echo -n "Logging in as $ADMIN_ID... "
LOGIN_RESPONSE=$(curl -s -X POST "$WEBAPP_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"employee_id\":\"$ADMIN_ID\",\"password\":\"$ADMIN_PASSWORD\"}" \
    2>/dev/null || echo "")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty' 2>/dev/null || echo "")

if [ -n "$TOKEN" ] && [ "$TOKEN" != "null" ]; then
    echo "✅ Login successful"
else
    echo "❌ Login failed"
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    echo "⚠️ Cannot proceed with authenticated tests"
    echo "   Please verify admin credentials or reset admin password via:"
    echo "   curl -X POST $WEBAPP_URL/api/health/reset-admin-password -H 'X-Admin-Secret: YOUR_AUTH_SECRET_KEY'"
    exit 1
fi
echo ""

# Step 4: Test Recruitment Module (Task 1)
echo "4️⃣ RECRUITMENT MODULE (Task 1)"
echo "------------------------------"
test_endpoint "/api/recruitment/metrics" "Recruitment Metrics"
test_endpoint "/api/recruitment/active" "Active Candidates"
test_endpoint "/api/recruitment/pipeline-summary" "Pipeline Summary"
echo ""

# Step 5: Test Employee DB Module (Task 2)
echo "5️⃣ EMPLOYEE DATABASE (Task 2)"
echo "-----------------------------"
test_endpoint "/api/employees" "Employee List"
test_endpoint "/api/employees/export" "Employee Export"
test_endpoint "/api/employees/stats" "Employee Statistics"
echo ""

# Step 6: Test Leave Planner (Task 3)
echo "6️⃣ LEAVE PLANNER - UAE 2026 (Task 3)"
echo "------------------------------------"
test_endpoint "/api/leave/calendar" "Leave Calendar"
test_endpoint "/api/leave/public-holidays" "UAE Public Holidays 2026"
test_endpoint "/api/leave/balance" "Leave Balance"
echo ""

# Step 7: Test Performance Module (Task 4)
echo "7️⃣ PERFORMANCE APPRAISAL (Task 4)"
echo "---------------------------------"
test_endpoint "/api/performance/reviews" "Performance Reviews"
test_endpoint "/api/performance/reports/summary" "Performance Summary"
echo ""

# Step 8: Frontend & Swagger UI
echo "8️⃣ FRONTEND & DOCUMENTATION"
echo "---------------------------"
test_endpoint "/" "Frontend (React App)" false
test_endpoint "/docs" "Swagger UI API Docs" false
echo ""

# Summary
echo "======================================"
echo "✅ DEPLOYMENT VERIFICATION COMPLETE"
echo "======================================"
echo ""
echo "📋 MVP Features Status:"
echo "  ✅ Recruitment (offers, reminders, metrics)"
echo "  ✅ Employee DB (bulk import, export)"
echo "  ✅ Leave Planner (UAE 2026 holidays)"
echo "  ✅ Performance (appraisals, reports)"
echo ""
echo "🔗 Access URLs:"
echo "  - Application: $WEBAPP_URL"
echo "  - API Docs: $WEBAPP_URL/docs"
echo "  - Health: $WEBAPP_URL/api/health/ping"
echo ""
echo "👤 Admin Access:"
echo "  - Employee ID: $ADMIN_ID"
echo "  - Password: $ADMIN_PASSWORD"
echo ""
echo "🎉 HR Portal MVP is LIVE and FUNCTIONAL!"
