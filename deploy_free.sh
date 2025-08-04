#!/bin/bash
# Chicago Taxi Fare API - FREE Deployment Selector

set -e

echo "🆓 CHICAGO TAXI FARE API - FREE DEPLOYMENT SELECTOR"
echo "=================================================="
echo "Choose your FREE deployment platform:"
echo ""

# Color codes for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏆 OPTION 1: RENDER (RECOMMENDED FOR BEGINNERS)${NC}"
echo "   ✅ 100% FREE forever (no credit card!)"
echo "   ✅ 750 hours/month (24/7 possible)" 
echo "   ✅ Automatic HTTPS & GitHub integration"
echo "   ⚠️  15-min sleep (30s cold start)"
echo "   🎯 Perfect for: Learning, MVPs, personal projects"
echo ""

echo -e "${BLUE}🥈 OPTION 2: GOOGLE CLOUD RUN (BEST PERFORMANCE)${NC}"
echo "   ✅ \$300 free credit + 2M requests/month always free"
echo "   ✅ Enterprise performance & global deployment"
echo "   ✅ Auto-scale to zero, no cold start penalties"
echo "   ⚠️  Credit card required (but never charged in free tier)"
echo "   🎯 Perfect for: Production apps, high traffic, enterprise"
echo ""

echo -e "${PURPLE}🥉 OPTION 3: FLY.IO (NO COLD STARTS)${NC}"
echo "   ✅ \$5 monthly credit (covers 3 small apps)"
echo "   ✅ No cold starts, global edge network"
echo "   ✅ Docker-native, great developer tools"
echo "   ⚠️  256MB RAM limit, credit monitoring needed"
echo "   🎯 Perfect for: Always-on APIs, performance-sensitive"
echo ""

echo -e "${CYAN}🚂 OPTION 4: RAILWAY (EASIEST SETUP)${NC}"
echo "   ✅ \$5 monthly credit, 3-click deployment"
echo "   ✅ Auto-deploy on git push, perfect for beginners"
echo "   ✅ Great dashboard and monitoring"
echo "   ⚠️  Credit card required, limited free resources"
echo "   🎯 Perfect for: Absolute beginners, quick prototypes"
echo ""

echo -e "${YELLOW}📊 OPTION 5: VIEW DETAILED COMPARISON${NC}"
echo "   📋 See complete feature comparison"
echo "   💰 Cost breakdown and resource limits"
echo "   🎯 Help choose the best option for your needs"
echo ""

echo "Please choose an option (1-5):"
read -p "Enter your choice: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}🚀 DEPLOYING TO RENDER (FOREVER FREE)${NC}"
        echo "============================================="
        echo "You chose the best option for beginners!"
        echo "No credit card required, completely free forever!"
        echo ""
        ./deploy_render_free.sh
        ;;
    2)
        echo ""
        echo -e "${BLUE}☁️ DEPLOYING TO GOOGLE CLOUD RUN${NC}"
        echo "=================================="
        echo "You chose the enterprise-grade option!"
        echo "Best performance with generous free tier!"
        echo ""
        ./deploy_gcp_free.sh
        ;;
    3)
        echo ""
        echo -e "${PURPLE}🛩️ DEPLOYING TO FLY.IO${NC}"
        echo "========================"
        echo "You chose the no-cold-start option!"
        echo "Perfect for always-on performance!"
        echo ""
        ./deploy_fly_free.sh
        ;;
    4)
        echo ""
        echo -e "${CYAN}🚂 DEPLOYING TO RAILWAY${NC}"
        echo "========================"
        echo "You chose the easiest deployment option!"
        echo "Perfect for beginners with simple setup!"
        echo ""
        ./deploy_railway_free.sh
        ;;
    5)
        echo ""
        echo -e "${YELLOW}📊 VIEWING DETAILED COMPARISON${NC}"
        echo "==============================="
        echo "Opening comprehensive comparison guide..."
        echo ""
        if command -v bat &> /dev/null; then
            bat FREE_COMPARISON.md
        elif command -v less &> /dev/null; then
            less FREE_COMPARISON.md
        else
            cat FREE_COMPARISON.md
        fi
        echo ""
        echo "After reviewing the comparison, run this script again to deploy!"
        echo "Command: ./deploy_free.sh"
        ;;
    *)
        echo ""
        echo -e "${RED}❌ Invalid option. Please choose 1-5.${NC}"
        echo "Run the script again: ./deploy_free.sh"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 DEPLOYMENT SCRIPT COMPLETED!${NC}"
echo "================================"
echo ""
echo "📋 What happens next:"
echo "1. Follow the instructions from the deployment script"
echo "2. Test your API once it's deployed"
echo "3. Monitor your usage to stay in free tier"
echo "4. Enjoy your free, production-ready API!"
echo ""
echo "🧪 Test your deployed API with:"
echo "   python test_production_api.py YOUR_DEPLOYED_URL"
echo ""
echo "📚 Need help? Check the guides:"
echo "   - FREE_COMPARISON.md (detailed comparison)"
echo "   - FREE_DEPLOYMENT_GUIDE.md (comprehensive guide)"
echo "   - DEPLOYMENT_GUIDE.md (all deployment options)"
echo ""
echo -e "${GREEN}Happy deploying! 🚀${NC}"