"""
==============================================================================
Unit Tests for Compliant Rate Limiter
==============================================================================
@spec RF01 - Rate Limiter Test Suite Validation
==============================================================================
"""

import time
from examples.compliant_agent_output import RateLimiter

def test_rate_limiter_allows_initial_burst() -> None:
    limiter = RateLimiter(capacity=5, refill_rate_per_sec=1.0)
    client: str = "client_1"
    
    # Should allow the initial 5 tokens
    for _ in range(5):
        assert limiter.allow_request(client) is True

    # 6th request should be blocked
    assert limiter.allow_request(client) is False

def test_rate_limiter_refills_over_time() -> None:
    limiter = RateLimiter(capacity=2, refill_rate_per_sec=10.0)
    client: str = "client_2"
    
    assert limiter.allow_request(client, tokens=2) is True
    assert limiter.allow_request(client, tokens=1) is False
    
    # Wait for token refill
    time.sleep(0.15)
    assert limiter.allow_request(client, tokens=1) is True

if __name__ == "__main__":
    test_rate_limiter_allows_initial_burst()
    test_rate_limiter_refills_over_time()
    print("All unit tests in compliant example passed successfully!")
