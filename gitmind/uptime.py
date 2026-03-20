import requests
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from threading import Lock


class UptimeMonitor:
    def __init__(self):
        self.checks: List[Dict] = []
        self.lock = Lock()
        self.max_history = 1000
    
    def add_check(self, endpoint: str, success: bool, response_time: float, status_code: int = None, error: str = None):
        check = {
            'endpoint': endpoint,
            'success': success,
            'response_time': response_time,
            'status_code': status_code,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        with self.lock:
            self.checks.append(check)
            if len(self.checks) > self.max_history:
                self.checks = self.checks[-self.max_history:]
    
    def get_status(self, hours: int = 1) -> Dict:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent_checks = [
                c for c in self.checks
                if datetime.fromisoformat(c['timestamp']) >= cutoff
            ]
        
        if not recent_checks:
            return {
                'status': 'unknown',
                'uptime_percentage': None,
                'total_checks': 0,
                'avg_response_time': None
            }
        
        successful = sum(1 for c in recent_checks if c['success'])
        total = len(recent_checks)
        uptime = (successful / total * 100) if total > 0 else 0
        
        response_times = [c['response_time'] for c in recent_checks if c['response_time'] is not None]
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        status = 'healthy' if uptime >= 99 else ('degraded' if uptime >= 95 else 'down')
        
        return {
            'status': status,
            'uptime_percentage': round(uptime, 2),
            'total_checks': total,
            'successful_checks': successful,
            'failed_checks': total - successful,
            'avg_response_time': round(avg_response, 3),
            'period_hours': hours
        }
    
    def get_recent_failures(self, limit: int = 10) -> List[Dict]:
        with self.lock:
            failures = [c for c in self.checks if not c['success']]
            return failures[-limit:]
    
    def get_incidents(self, hours: int = 24) -> List[Dict]:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent = [
                c for c in self.checks
                if datetime.fromisoformat(c['timestamp']) >= cutoff
            ]
        
        incidents = []
        current_incident = None
        
        for check in recent:
            if not check['success']:
                if current_incident is None:
                    current_incident = {
                        'start': check['timestamp'],
                        'errors': [],
                        'count': 0
                    }
                current_incident['errors'].append(check.get('error', 'Unknown'))
                current_incident['count'] += 1
            else:
                if current_incident:
                    current_incident['end'] = check['timestamp']
                    incidents.append(current_incident)
                    current_incident = None
        
        if current_incident:
            current_incident['end'] = datetime.utcnow().isoformat()
            incidents.append(current_incident)
        
        return incidents
    
    def get_metrics(self, hours: int = 1) -> Dict:
        status = self.get_status(hours)
        incidents = self.get_incidents(hours)
        failures = self.get_recent_failures()
        
        return {
            'current_status': status,
            'incidents': incidents,
            'recent_failures': failures,
            'generated_at': datetime.utcnow().isoformat()
        }


uptime_monitor = UptimeMonitor()


def check_endpoint(url: str, timeout: float = 5.0) -> Dict:
    start = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start
        
        success = response.status_code < 400
        
        uptime_monitor.add_check(
            endpoint=url,
            success=success,
            response_time=response_time,
            status_code=response.status_code
        )
        
        return {
            'success': success,
            'status_code': response.status_code,
            'response_time': response_time
        }
    except requests.exceptions.Timeout:
        response_time = time.time() - start
        uptime_monitor.add_check(
            endpoint=url,
            success=False,
            response_time=response_time,
            error='Timeout'
        )
        return {
            'success': False,
            'error': 'Timeout',
            'response_time': response_time
        }
    except Exception as e:
        response_time = time.time() - start
        uptime_monitor.add_check(
            endpoint=url,
            success=False,
            response_time=response_time,
            error=str(e)
        )
        return {
            'success': False,
            'error': str(e),
            'response_time': response_time
        }


def check_own_health() -> Dict:
    return check_endpoint('http://localhost:8000/health')


def get_uptime_status() -> Dict:
    return uptime_monitor.get_metrics(hours=1)
