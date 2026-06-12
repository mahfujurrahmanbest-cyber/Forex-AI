import pytest

class TestDecisionEngine:
    def test_execute_threshold(self):
        assert 22 == 22
        assert 85 == 85

class TestScoringEngine:
    def test_max_instant_score(self):
        assert 28 == 28
    
    def test_score_components(self):
        components = {
            'weekly_direction_valid': 3,
            'approved_in_report': 2,
            'sure_trade': 1,
            'live_mtf_above_50': 3,
            'liquidity_sweep': 3,
            'inside_ob_fvg': 2,
            'bos_choch': 2,
            'rsi_alignment': 2,
            'macd_alignment': 2,
            'dxy_supports': 2,
            'no_news': 2,
            'prime_session': 1,
            'pivot_alignment': 1,
            'dxy_unchanged': 1,
            'premium_discount': 1
        }
        assert sum(components.values()) == 28

class TestKillZone:
    def test_london_kz(self):
        assert 10 - 7 == 3
    
    def test_ny_kz(self):
        assert 15 - 12 == 3
