# DatingApp - Development & Testing Automation
# Professional task runner for consistent workflows

.PHONY: help test test-clean test-e2e dev-start dev-stop reset seed-minimal seed-standard seed-load

# Default target
help:
	@echo "=========================================="
	@echo "DatingApp Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run tests with current data"
	@echo "  make test-clean        - Reset DB + seed + run tests"
	@echo "  make test-e2e          - Run full end-to-end test suite"
	@echo ""
	@echo "Development:"
	@echo "  make dev-start         - Start all services"
	@echo "  make dev-stop          - Stop all services"
	@echo "  make reset             - Reset databases (clean slate)"
	@echo ""
	@echo "Data Seeding:"
	@echo "  make seed-minimal      - Load minimal fixtures (5 users)"
	@echo "  make seed-standard     - Load standard fixtures (50 users)"
	@echo "  make seed-load         - Load load test fixtures (500 users)"
	@echo ""
	@echo "Visual QA:"
	@echo "  make visual-qa-build   - Build Flutter APK + Docker image"
	@echo "  make visual-qa-up      - Start emulator + backend services"
	@echo "  make visual-qa-run     - Run visual QA automation (all use cases)"
	@echo "  make visual-qa-baseline- Capture + store regression baselines"
	@echo "  make visual-qa-down    - Stop emulator + visual-qa services"
	@echo ""

# Start development environment
dev-start:
	@echo "🚀 Starting development environment..."
	./infrastructure/start.sh
	@echo "✅ Services started!"

# Stop development environment
dev-stop:
	@echo "🛑 Stopping development environment..."
	./infrastructure/stop.sh
	@echo "✅ Services stopped!"

# Reset databases (clean slate)
reset:
	@echo "🔄 Resetting databases..."
	./infrastructure/stop.sh
	@docker volume prune -f
	@echo "✅ Databases reset! Run 'make dev-start' to restart."

# Seed minimal fixtures
seed-minimal:
	@echo "📦 Loading minimal fixtures..."
	./scripts/seed-test-data.sh minimal
	@echo "✅ Minimal fixtures loaded!"

# Seed standard fixtures (when implemented)
seed-standard:
	@echo "📦 Loading standard fixtures..."
	@if [ -d "infrastructure/test-fixtures/standard" ]; then \
		./scripts/seed-test-data.sh standard; \
	else \
		echo "⚠️  Standard fixtures not yet created. Creating from minimal..."; \
		echo "TODO: Create infrastructure/test-fixtures/standard/"; \
	fi

# Seed load test fixtures (when implemented)
seed-load:
	@echo "📦 Loading load test fixtures..."
	@if [ -d "infrastructure/test-fixtures/load" ]; then \
		./scripts/seed-test-data.sh load; \
	else \
		echo "⚠️  Load fixtures not yet created."; \
		echo "TODO: Create infrastructure/test-fixtures/load/"; \
	fi

# Run tests with current data
test:
	@echo "🧪 Running tests..."
	cd mobile-apps/flutter/dejtingapp && flutter test integration_test/

# Clean slate test run (recommended for CI)
test-clean: reset dev-start
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@$(MAKE) seed-minimal
	@echo "🧪 Running tests with clean data..."
	cd mobile-apps/flutter/dejtingapp && flutter test integration_test/
	@echo "✅ Clean test run complete!"

# End-to-end test suite
test-e2e: test-clean
	@echo "🏁 Full E2E test suite complete!"

# Quick reset + seed for development
quick-reset:
	@echo "⚡ Quick reset (truncate tables)..."
	@docker exec swipe-service-db mysql -uroot -proot_password SwipeServiceDb \
		-e "SET FOREIGN_KEY_CHECKS=0; TRUNCATE Swipes; TRUNCATE Matches; TRUNCATE UserProfileMappings; SET FOREIGN_KEY_CHECKS=1;" 2>/dev/null || true
	@docker exec UserService-db mysql -uroot -proot_password UserServiceDb \
		-e "SET FOREIGN_KEY_CHECKS=0; TRUNCATE UserProfiles; TRUNCATE MatchPreferences; SET FOREIGN_KEY_CHECKS=1;" 2>/dev/null || true
	@docker exec messaging-service-db mysql -uroot -proot_password MessagingDb \
		-e "SET FOREIGN_KEY_CHECKS=0; TRUNCATE Messages; SET FOREIGN_KEY_CHECKS=1;" 2>/dev/null || true
	@echo "✅ Tables truncated!"
	@$(MAKE) seed-minimal

# API smoke tests (fast)
test-api:
	@echo "🔥 Running API smoke tests..."
	python3 api_tests.py
	@echo "✅ API tests passed!"

# Check service health
health-check:
	@echo "🏥 Checking service health..."
	@./scripts/seed-test-data.sh minimal 2>&1 | grep -A 20 "Checking service health" | head -20



# ============================================================================
# AI Helper Commands (Fast State Inspection)
# ============================================================================

.PHONY: ai-state ai-state-verbose ai-verify-fixtures

ai-state: ## Quick state check (AI debugging)
	@python3 scripts/ai-verify-state.py

ai-state-verbose: ## Detailed state dump (AI debugging)
	@python3 scripts/ai-verify-state.py --verbose

ai-verify-fixtures: ## Assert minimal fixtures loaded (AI testing)
	@python3 scripts/ai-verify-state.py --assert-minimal



# ============================================================================
# Visual QA Automation (Emulator-based E2E)
# ============================================================================

.PHONY: visual-qa-build visual-qa-up visual-qa-run visual-qa-down visual-qa-logs visual-qa-baseline

visual-qa-build: ## Build Flutter APK + visual-qa Docker image
	@echo "Building Flutter APK..."
	cd mobile-apps/flutter/dejtingapp && flutter build apk --release
	@echo "Building visual-qa runner image..."
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml build visual-qa
	@echo "Visual QA images ready!"

visual-qa-up: ## Start emulator + backend services
	@echo "Starting emulator + services..."
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml up -d
	@echo "Waiting for emulator boot (this may take 2-3 minutes)..."
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml exec -T android-emulator adb wait-for-device
	@echo "Emulator + services running"

visual-qa-run: ## Run visual QA tests (starts everything if needed)
	@echo "Running Visual QA automation..."
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml run --rm visual-qa python run_visual_qa.py --use-case all
	@echo "Results in visual-qa/test-results/"

visual-qa-down: ## Stop emulator + visual-qa services
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml down

visual-qa-logs: ## Tail visual-qa runner logs
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml logs -f visual-qa

visual-qa-baseline: visual-qa-up ## Capture + store baseline screenshots and XML dumps
	@echo "📸 Capturing visual QA baselines (all use cases)..."
	docker compose -f docker-compose.yml -f docker-compose.visual-qa.yml run --rm visual-qa \
		python run_visual_qa.py --use-case all --update-baselines \
		--output-dir /app/test-results
	@echo "✅ Baselines stored in visual-qa/baselines/"
