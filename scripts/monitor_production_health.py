#!/usr/bin/env python3
"""
Production Health Monitoring Script for US1.6
Monitors system health after deployment with specific focus on calendar features
"""

import requests
import time
import json
import argparse
import logging
import sys
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionHealthMonitor:
    """Monitors production health with US1.6 specific checks"""
    
    def __init__(self, base_url: str = "https://diettracker-app.herokuapp.com"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Health check thresholds
        self.thresholds = {
            'response_time_ms': 500,
            'success_rate_percent': 95,
            'max_consecutive_failures': 3
        }
        
        # Monitoring results
        self.results = {
            'start_time': datetime.now().isoformat(),
            'checks': [],
            'summary': {},
            'alerts': []
        }
    
    def get_current_monday(self) -> date:
        """Get current Monday for US1.6 testing"""
        today = date.today()
        return today - timedelta(days=today.weekday())
    
    def check_basic_health(self) -> Dict[str, Any]:
        """Basic health endpoint check"""
        logger.info("Checking basic health endpoint...")
        
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            result = {
                'endpoint': '/health',
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2),
                'success': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['health_data'] = data
                except json.JSONDecodeError:
                    result['health_data'] = {'status': 'ok'}
            
            logger.info(f"Health check: {response.status_code} ({response_time_ms:.2f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'endpoint': '/health',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_us16_meal_plans_api(self) -> Dict[str, Any]:
        """Check US1.6 meal plans API with week_start parameter"""
        logger.info("Checking US1.6 meal plans API...")
        
        monday = self.get_current_monday()
        endpoint = f"{self.api_url}/meal-plans"
        params = {'week_start': monday.isoformat()}
        
        try:
            start_time = time.time()
            response = self.session.get(endpoint, params=params)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            result = {
                'endpoint': '/api/meal-plans',
                'params': params,
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2),
                'success': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['data_structure_valid'] = 'meal_plans' in data
                    result['week_start_correct'] = monday.isoformat() in str(data)
                except json.JSONDecodeError:
                    result['data_structure_valid'] = False
            
            logger.info(f"Meal plans API: {response.status_code} ({response_time_ms:.2f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Meal plans API check failed: {e}")
            return {
                'endpoint': '/api/meal-plans',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_us16_calendar_navigation(self) -> Dict[str, Any]:
        """Check US1.6 calendar navigation functionality"""
        logger.info("Checking US1.6 calendar navigation...")
        
        monday = self.get_current_monday()
        next_monday = monday + timedelta(days=7)
        endpoint = f"{self.api_url}/meal-plans"
        
        navigation_results = []
        
        # Test current week and next week
        for week_date, week_name in [(monday, 'current'), (next_monday, 'next')]:
            try:
                start_time = time.time()
                response = self.session.get(endpoint, params={'week_start': week_date.isoformat()})
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                
                week_result = {
                    'week': week_name,
                    'week_start': week_date.isoformat(),
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time_ms, 2),
                    'success': response.status_code == 200
                }
                
                navigation_results.append(week_result)
                logger.info(f"Calendar navigation ({week_name}): {response.status_code} ({response_time_ms:.2f}ms)")
                
            except Exception as e:
                logger.error(f"Calendar navigation check failed for {week_name}: {e}")
                navigation_results.append({
                    'week': week_name,
                    'success': False,
                    'error': str(e)
                })
        
        return {
            'endpoint': '/api/meal-plans (navigation)',
            'navigation_results': navigation_results,
            'overall_success': all(r.get('success', False) for r in navigation_results),
            'timestamp': datetime.now().isoformat()
        }
    
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity via recipes endpoint"""
        logger.info("Checking database connectivity...")
        
        endpoint = f"{self.api_url}/recipes"
        
        try:
            start_time = time.time()
            response = self.session.get(endpoint)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            result = {
                'endpoint': '/api/recipes',
                'status_code': response.status_code,
                'response_time_ms': round(response_time_ms, 2),
                'success': response.status_code == 200,
                'timestamp': datetime.now().isoformat()
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['database_accessible'] = 'recipes' in data
                    result['data_count'] = len(data.get('recipes', []))
                except json.JSONDecodeError:
                    result['database_accessible'] = False
            
            logger.info(f"Database connectivity: {response.status_code} ({response_time_ms:.2f}ms)")
            return result
            
        except Exception as e:
            logger.error(f"Database connectivity check failed: {e}")
            return {
                'endpoint': '/api/recipes',
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_health_check_cycle(self) -> Dict[str, Any]:
        """Run a complete health check cycle"""
        cycle_results = {
            'timestamp': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Run all health checks
        checks = [
            ('basic_health', self.check_basic_health),
            ('us16_meal_plans', self.check_us16_meal_plans_api),
            ('us16_navigation', self.check_us16_calendar_navigation),
            ('database_connectivity', self.check_database_connectivity)
        ]
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                cycle_results['checks'][check_name] = result
            except Exception as e:
                logger.error(f"Check {check_name} failed with exception: {e}")
                cycle_results['checks'][check_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Calculate cycle success
        successful_checks = sum(1 for check in cycle_results['checks'].values() 
                              if check.get('success', False))
        total_checks = len(cycle_results['checks'])
        
        cycle_results['success_rate'] = (successful_checks / total_checks) * 100 if total_checks > 0 else 0
        cycle_results['successful_checks'] = successful_checks
        cycle_results['total_checks'] = total_checks
        
        return cycle_results
    
    def monitor_continuous(self, duration_minutes: int = 60, check_interval_seconds: int = 30) -> None:
        """Run continuous monitoring for specified duration"""
        logger.info(f"Starting continuous monitoring for {duration_minutes} minutes...")
        
        end_time = time.time() + (duration_minutes * 60)
        consecutive_failures = 0
        
        while time.time() < end_time:
            cycle_result = self.run_health_check_cycle()
            self.results['checks'].append(cycle_result)
            
            # Check for alerts
            if cycle_result['success_rate'] < self.thresholds['success_rate_percent']:
                consecutive_failures += 1
                
                if consecutive_failures >= self.thresholds['max_consecutive_failures']:
                    alert = {
                        'type': 'consecutive_failures',
                        'message': f"Health check failures: {consecutive_failures} consecutive cycles below {self.thresholds['success_rate_percent']}% success rate",
                        'timestamp': datetime.now().isoformat(),
                        'cycle_result': cycle_result
                    }
                    self.results['alerts'].append(alert)
                    logger.warning(f"ALERT: {alert['message']}")
            else:
                consecutive_failures = 0
            
            # Log cycle summary
            logger.info(f"Cycle complete: {cycle_result['success_rate']:.1f}% success rate "
                       f"({cycle_result['successful_checks']}/{cycle_result['total_checks']} checks passed)")
            
            # Wait for next cycle
            remaining_time = end_time - time.time()
            if remaining_time > check_interval_seconds:
                time.sleep(check_interval_seconds)
            elif remaining_time > 0:
                time.sleep(remaining_time)
                break
    
    def generate_summary(self) -> None:
        """Generate monitoring summary"""
        if not self.results['checks']:
            logger.warning("No monitoring data to summarize")
            return
        
        total_cycles = len(self.results['checks'])
        successful_cycles = sum(1 for cycle in self.results['checks'] 
                               if cycle['success_rate'] == 100)
        
        avg_success_rate = sum(cycle['success_rate'] for cycle in self.results['checks']) / total_cycles
        
        # Calculate response time statistics
        response_times = []
        for cycle in self.results['checks']:
            for check in cycle['checks'].values():
                if 'response_time_ms' in check:
                    response_times.append(check['response_time_ms'])
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        self.results['summary'] = {
            'total_cycles': total_cycles,
            'successful_cycles': successful_cycles,
            'avg_success_rate': round(avg_success_rate, 2),
            'avg_response_time_ms': round(avg_response_time, 2),
            'max_response_time_ms': round(max_response_time, 2),
            'total_alerts': len(self.results['alerts']),
            'monitoring_duration': datetime.now().isoformat(),
            'overall_health': 'HEALTHY' if avg_success_rate >= 95 and len(self.results['alerts']) == 0 else 'DEGRADED'
        }
        
        logger.info("=== MONITORING SUMMARY ===")
        logger.info(f"Total Cycles: {total_cycles}")
        logger.info(f"Successful Cycles: {successful_cycles}/{total_cycles}")
        logger.info(f"Average Success Rate: {avg_success_rate:.2f}%")
        logger.info(f"Average Response Time: {avg_response_time:.2f}ms")
        logger.info(f"Max Response Time: {max_response_time:.2f}ms")
        logger.info(f"Total Alerts: {len(self.results['alerts'])}")
        logger.info(f"Overall Health: {self.results['summary']['overall_health']}")
    
    def save_results(self, filename: Optional[str] = None) -> None:
        """Save monitoring results to file"""
        if filename is None:
            filename = f"health_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        self.results['end_time'] = datetime.now().isoformat()
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Production Health Monitor for US1.6')
    parser.add_argument('--url', default='https://diettracker-app.herokuapp.com',
                       help='Base URL to monitor')
    parser.add_argument('--duration', type=int, default=60,
                       help='Monitoring duration in minutes')
    parser.add_argument('--interval', type=int, default=30,
                       help='Check interval in seconds')
    parser.add_argument('--single-check', action='store_true',
                       help='Run single health check cycle only')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    monitor = ProductionHealthMonitor(args.url)
    
    try:
        if args.single_check:
            logger.info("Running single health check cycle...")
            result = monitor.run_health_check_cycle()
            monitor.results['checks'].append(result)
            
            logger.info("=== SINGLE CHECK RESULTS ===")
            logger.info(f"Success Rate: {result['success_rate']:.1f}%")
            logger.info(f"Successful Checks: {result['successful_checks']}/{result['total_checks']}")
        else:
            monitor.monitor_continuous(args.duration, args.interval)
        
        monitor.generate_summary()
        
        # Save results
        monitor.save_results(args.output)
        
        # Exit with appropriate code
        if monitor.results['summary'].get('overall_health') == 'HEALTHY':
            logger.info("✅ Monitoring completed - System is HEALTHY")
            sys.exit(0)
        else:
            logger.error("❌ Monitoring completed - System is DEGRADED")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        monitor.generate_summary()
        monitor.save_results(args.output)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()