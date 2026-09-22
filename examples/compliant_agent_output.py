"""
==============================================================================
Compliant AI Agent Code Example - 100% Engineering Standards Compliant
==============================================================================
@spec RF01 - Token Bucket Rate Limiter Implementation
==============================================================================
"""

import time
from typing import Dict, Optional, Tuple

class RateLimiter:
    """Deterministic rate limiter based on the Token Bucket algorithm.
    
    Traceability: @spec RF01
    """

    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self.capacity: int = capacity
        self.refill_rate: float = refill_rate_per_sec
        self.buckets: Dict[str, Tuple[float, float]] = {}

    def allow_request(self, client_id: str, tokens: int = 1) -> bool:
        """Determines if the client request can proceed under rate limits."""
        now: float = time.time()
        
        if client_id not in self.buckets:
            self.buckets[client_id] = (float(self.capacity) - float(tokens), now)
            return True

        current_tokens, last_refill = self.buckets[client_id]
        elapsed = now - last_refill
        refilled_tokens = min(float(self.capacity), current_tokens + (elapsed * self.refill_rate))

        if refilled_tokens >= float(tokens):
            self.buckets[client_id] = (refilled_tokens - float(tokens), now)
            return True

        self.buckets[client_id] = (refilled_tokens, now)
        return False
