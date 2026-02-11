import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Trend, Rate } from 'k6/metrics';

// Custom metrics
const candidateGenerationTime = new Trend('candidate_generation_time', true);
const swipeProcessingTime = new Trend('swipe_processing_time', true);
const matchesRetrievalTime = new Trend('matches_retrieval_time', true);
const errorRate = new Rate('error_rate');
const cacheHitRate = new Rate('cache_hit_rate');

// Test configuration
export const options = {
  scenarios: {
    // Scenario 1: Baseline load (20 VUs simulating normal usage)
    baseline: {
      executor: 'constant-vus',
      vus: 20,
      duration: '2m',
      startTime: '0s',
      tags: { scenario: 'baseline' },
    },
    // Scenario 2: Ramp-up test (gradually increase to 100 VUs)
    rampup: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },
        { duration: '2m', target: 100 },
        { duration: '1m', target: 100 },
        { duration: '1m', target: 0 },
      ],
      startTime: '2m',
      tags: { scenario: 'rampup' },
    },
    // Scenario 3: Spike test (sudden traffic spike)
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '10s', target: 200 },
        { duration: '30s', target: 200 },
        { duration: '10s', target: 0 },
      ],
      startTime: '7m',
      tags: { scenario: 'spike' },
    },
  },
  thresholds: {
    // Success criteria from MVP constitution
    'http_req_duration{endpoint:candidates}': ['p(95)<2000'], // 2s for cache miss
    'http_req_duration{endpoint:swipe}': ['p(95)<200'],       // 200ms for swipe
    'http_req_duration{endpoint:matches}': ['p(95)<500'],     // 500ms for matches
    'error_rate': ['rate<0.01'],                              // <1% error rate
    'cache_hit_rate{endpoint:candidates}': ['rate>0.90'],     // >90% cache hit
    'http_req_failed': ['rate<0.05'],                         // <5% failed requests
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8083';
const YARP_URL = __ENV.YARP_URL || 'http://localhost:8080';

// Test data - realistic user pool
const testUsers = Array.from({ length: 100 }, (_, i) => ({
  userId: i + 1,
  token: `test-token-${i + 1}`,
}));

export default function() {
  // Select a random user for this VU iteration
  const user = testUsers[Math.floor(Math.random() * testUsers.length)];
  const headers = {
    'Authorization': `Bearer ${user.token}`,
    'Content-Type': 'application/json',
  };

  // User journey: Get candidates → Swipe → Check matches
  
  group('Get Match Candidates', () => {
    const startTime = Date.now();
    const res = http.get(`${BASE_URL}/matches/candidates`, {
      headers,
      tags: { endpoint: 'candidates' },
    });

    candidateGenerationTime.add(Date.now() - startTime);
    
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'has candidates array': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || Array.isArray(body.candidates);
        } catch {
          return false;
        }
      },
      'response time <2s': (r) => r.timings.duration < 2000,
    });

    if (!success) {
      errorRate.add(1);
    } else {
      errorRate.add(0);
      
      // Check if response came from cache (custom header from service)
      const isCached = res.headers['X-Cache-Hit'] === 'true' || 
                       res.timings.duration < 200;
      cacheHitRate.add(isCached ? 1 : 0, { endpoint: 'candidates' });
    }
  });

  sleep(1); // User reviews candidates

  // Simulate swiping on 3-5 candidates
  const swipeCount = Math.floor(Math.random() * 3) + 3;
  
  group('Swipe on Candidates', () => {
    for (let i = 0; i < swipeCount; i++) {
      const targetUserId = Math.floor(Math.random() * 100) + 1;
      const direction = Math.random() > 0.35 ? 'right' : 'left'; // 65% like rate
      
      const startTime = Date.now();
      const res = http.post(
        `${BASE_URL}/matches/swipe`,
        JSON.stringify({
          targetUserId,
          direction,
        }),
        {
          headers,
          tags: { endpoint: 'swipe' },
        }
      );

      swipeProcessingTime.add(Date.now() - startTime);

      const success = check(res, {
        'swipe status is 200 or 201': (r) => r.status === 200 || r.status === 201,
        'swipe response time <200ms': (r) => r.timings.duration < 200,
      });

      if (!success) {
        errorRate.add(1);
      } else {
        errorRate.add(0);
      }

      sleep(0.5); // Time between swipes
    }
  });

  sleep(2); // User pauses

  group('Check Matches', () => {
    const startTime = Date.now();
    const res = http.get(`${BASE_URL}/matches`, {
      headers,
      tags: { endpoint: 'matches' },
    });

    matchesRetrievalTime.add(Date.now() - startTime);

    const success = check(res, {
      'matches status is 200': (r) => r.status === 200,
      'has matches data': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || body.matches !== undefined;
        } catch {
          return false;
        }
      },
      'matches response time <500ms': (r) => r.timings.duration < 500,
    });

    if (!success) {
      errorRate.add(1);
    } else {
      errorRate.add(0);
    }
  });

  sleep(3); // Think time before next iteration
}

// Setup function - runs once per VU
export function setup() {
  console.log('🚀 Starting Matchmaking Load Test');
  console.log(`📍 Base URL: ${BASE_URL}`);
  console.log(`👥 Test Users: ${testUsers.length}`);
  
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  if (healthRes.status !== 200) {
    throw new Error(`Service not healthy: ${healthRes.status}`);
  }
  
  console.log('✅ Service health check passed');
  return { startTime: new Date().toISOString() };
}

// Teardown function - runs once after all VUs finish
export function teardown(data) {
  console.log('📊 Load test completed');
  console.log(`Started at: ${data.startTime}`);
  console.log(`Ended at: ${new Date().toISOString()}`);
}
