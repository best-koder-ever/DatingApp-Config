#!/bin/bash
# Start Grafana + Prometheus for monitoring

echo "🚀 Starting Monitoring Stack..."

# Start infrastructure (includes Prometheus)
cd infrastructure && ./start.sh

echo "📊 Grafana will be available at: http://localhost:3000"
echo "   Username: admin"
echo "   Password: admin"
echo ""
echo "📈 Prometheus at: http://localhost:9090"
echo ""
echo "Dashboard: Import monitoring/grafana/dashboards/mvp-overview.json"
