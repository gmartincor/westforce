#!/bin/bash
set -e

echo "==================================="
echo "Westforce SEO & Analytics Deployment"
echo "==================================="
echo ""

check_env_var() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo "❌ Missing: $var_name"
        return 1
    else
        echo "✅ Set: $var_name"
        return 0
    fi
}

echo "📋 Checking Required Environment Variables..."
echo ""

REQUIRED_VARS=(
    "SECRET_KEY"
    "DB_NAME"
    "DB_USER"
    "DB_PASSWORD"
    "DB_HOST"
    "ALLOWED_HOSTS"
)

ANALYTICS_VARS=(
    "GOOGLE_ANALYTICS_ID"
    "GOOGLE_TAG_MANAGER_ID"
    "GOOGLE_ADS_ID"
    "GOOGLE_ADS_CONVERSION_ID"
)

MISSING_REQUIRED=0
MISSING_ANALYTICS=0

echo "Required Variables:"
for var in "${REQUIRED_VARS[@]}"; do
    if ! check_env_var "$var"; then
        MISSING_REQUIRED=1
    fi
done

echo ""
echo "Analytics Variables (Recommended):"
for var in "${ANALYTICS_VARS[@]}"; do
    if ! check_env_var "$var"; then
        MISSING_ANALYTICS=1
    fi
done

echo ""

if [ $MISSING_REQUIRED -eq 1 ]; then
    echo "❌ Missing required environment variables. Please configure them before deployment."
    exit 1
fi

if [ $MISSING_ANALYTICS -eq 1 ]; then
    echo "⚠️  Some analytics variables are missing. Tracking features will be disabled."
    echo "   Configure them to enable Google Analytics and Ads tracking."
    echo ""
fi

echo "🔧 Running Django checks..."
python manage.py check --deploy

echo ""
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "🗃️  Running migrations..."
python manage.py migrate --noinput

echo ""
echo "🔍 Verifying SEO configuration..."

echo "  Checking robots.txt endpoint..."
if python manage.py shell -c "from django.test import Client; c = Client(); r = c.get('/robots.txt'); print('✅ robots.txt accessible' if r.status_code == 200 else '❌ robots.txt not accessible')" | grep -q "✅"; then
    echo "  ✅ robots.txt is accessible"
else
    echo "  ❌ robots.txt endpoint error"
fi

echo "  Checking sitemap.xml endpoint..."
if python manage.py shell -c "from django.test import Client; c = Client(); r = c.get('/sitemap.xml'); print('✅ sitemap.xml accessible' if r.status_code == 200 else '❌ sitemap.xml not accessible')" | grep -q "✅"; then
    echo "  ✅ sitemap.xml is accessible"
else
    echo "  ❌ sitemap.xml endpoint error"
fi

echo ""
echo "✅ Deployment checks complete!"
echo ""
echo "📝 Next Steps:"
echo "  1. Verify Google Analytics is receiving data"
echo "  2. Test Google Ads conversion tracking"
echo "  3. Submit sitemap to Google Search Console"
echo "  4. Verify structured data with Google Rich Results Test"
echo "  5. Test all CTAs (phone, email) for conversion tracking"
echo ""
echo "📖 See docs/SEO_ANALYTICS_GUIDE.md for detailed setup instructions"
echo ""
