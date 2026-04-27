import pytest
from datetime import datetime, timezone, timedelta
from power_style.core.models import MemoryItem
from power_style.core.memory_manager import MemoryManager
from power_style.core.config import default_config

def test_tier_calculation():
    manager = MemoryManager(default_config)
    
    # 0.95 should be Tier 1 (threshold 0.8)
    assert manager.calculate_tier(0.95) == 1
    
    # 0.5 should be Tier 2 (threshold 0.3)
    assert manager.calculate_tier(0.5) == 2
    
    # 0.1 should be Tier 3 (threshold 0.0)
    assert manager.calculate_tier(0.1) == 3

def test_promote():
    manager = MemoryManager(default_config)
    item = MemoryItem(id="test_1", content="Hello", strength=0.5)
    
    # Promote boosts strength
    promoted = manager.promote(item)
    assert promoted.strength > 0.5
    assert promoted.tier_level in [1, 2] # Depends on boost value, default is 0.1, so 0.6 -> tier 2

def test_demote_decay():
    manager = MemoryManager(default_config)
    
    # Create an item accessed 10 days ago
    past_date = datetime.now(timezone.utc) - timedelta(days=10)
    item = MemoryItem(id="test_2", content="World", strength=0.9, last_accessed=past_date)
    
    # Demote should reduce strength
    demoted = manager.demote(item)
    assert demoted.strength < 0.9
    # If decay is 0.05 per day, 10 days = 0.5 decay. Strength becomes 0.4 -> Tier 2
    assert demoted.tier_level >= 2
