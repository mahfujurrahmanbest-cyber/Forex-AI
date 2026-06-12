// Instant Forex Execution Engine - JavaScript

// Update current time
function updateTime() {
    const now = new Date();
    const utcTime = now.toUTCString().split(' ')[4];
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = utcTime + ' UTC';
    }
}

// Update session info
async function updateSession() {
    try {
        const response = await fetch('/api/session');
        const result = await response.json();
        
        if (result.success) {
            const data = result.data;
            
            // Update sidebar session
            const sessionElement = document.getElementById('current-session');
            if (sessionElement) {
                if (data.is_overlap) {
                    sessionElement.textContent = 'OVERLAP';
                    sessionElement.style.color = '#1E8449';
                } else if (data.active_sessions.length > 0) {
                    sessionElement.textContent = data.active_sessions.join(' / ');
                } else {
                    sessionElement.textContent = 'OFF HOURS';
                    sessionElement.style.color = '#E67E22';
                }
            }
            
            // Update session grid if exists
            updateSessionGrid(data);
            
            // Update kill zone status if exists
            updateKillZoneStatus(data);
        }
    } catch (error) {
        console.error('Error updating session:', error);
    }
}

// Update session grid on dashboard
function updateSessionGrid(data) {
    const sessions = ['sydney', 'tokyo', 'london', 'newyork'];
    const sessionNames = ['SYDNEY', 'TOKYO', 'LONDON', 'NEW_YORK'];
    
    sessions.forEach((session, index) => {
        const element = document.getElementById(`session-${session}`);
        if (element) {
            const isActive = data.active_sessions.includes(sessionNames[index]);
            element.classList.toggle('active', isActive);
            
            const statusElement = element.querySelector('.session-status');
            if (statusElement) {
                statusElement.textContent = isActive ? 'ACTIVE' : 'CLOSED';
            }
        }
    });
}

// Update kill zone status
function updateKillZoneStatus(data) {
    const kzElement = document.getElementById('kill-zone-status');
    if (kzElement) {
        const kzValue = kzElement.querySelector('.kz-value');
        if (kzValue) {
            if (data.kill_zone.overlap_kz) {
                kzValue.textContent = '✅ OVERLAP ACTIVE';
                kzValue.style.color = '#1E8449';
            } else if (data.kill_zone.london_kz) {
                kzValue.textContent = '✅ LONDON KZ';
                kzValue.style.color = '#1E8449';
            } else if (data.kill_zone.ny_kz) {
                kzValue.textContent = '✅ NEW YORK KZ';
                kzValue.style.color = '#1E8449';
            } else {
                kzValue.textContent = '❌ NOT ACTIVE';
                kzValue.style.color = '#C9A84C';
            }
        }
    }
}

// Fetch live price for a pair
async function fetchLivePrice(pair) {
    try {
        const response = await fetch(`/api/live-price/${pair}`);
        const result = await response.json();
        
        if (result.success) {
            return result.data;
        }
    } catch (error) {
        console.error('Error fetching price:', error);
    }
    return null;
}

// Format number with appropriate decimals
function formatPrice(price, pair) {
    if (!price) return '--';
    
    if (pair && (pair.includes('XAU') || pair.includes('JPY'))) {
        return price.toFixed(2);
    }
    return price.toFixed(5);
}

// Format percentage
function formatPercent(value) {
    if (value === null || value === undefined) return '--%';
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(2) + '%';
}

// Get color class based on value
function getChangeClass(value) {
    if (value > 0) return 'positive';
    if (value < 0) return 'negative';
    return '';
}

// Initialize dashboard market overview
async function initMarketOverview() {
    const pairs = [
        { id: 'dxy', pair: 'DXY' },
        { id: 'us10y', pair: 'US10Y' },
        { id: 'vix', pair: 'VIX' },
        { id: 'gold', pair: 'XAUUSD' }
    ];
    
    // This would fetch real data in production
    // For now, we'll use placeholder updates
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Calculate risk reward
function calculateRR(entry, sl, tp) {
    const risk = Math.abs(entry - sl);
    const reward = Math.abs(tp - entry);
    return (reward / risk).toFixed(2);
}

// Validate form inputs
function validateForm(formData) {
    const errors = [];
    
    if (!formData.get('pair')) {
        errors.push('Please select a currency pair');
    }
    
    const accountSize = parseFloat(formData.get('account_size'));
    if (isNaN(accountSize) || accountSize < 100) {
        errors.push('Account size must be at least $100');
    }
    
    const maxRisk = parseFloat(formData.get('max_risk'));
    if (isNaN(maxRisk) || maxRisk < 0.1 || maxRisk > 5) {
        errors.push('Max risk must be between 0.1% and 5%');
    }
    
    return errors;
}

// Export functions for use in templates
window.updateTime = updateTime;
window.updateSession = updateSession;
window.fetchLivePrice = fetchLivePrice;
window.formatPrice = formatPrice;
window.formatPercent = formatPercent;
window.showNotification = showNotification;
window.copyToClipboard = copyToClipboard;
