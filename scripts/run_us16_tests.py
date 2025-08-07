#!/usr/bin/env python3
"""
Script d'exécution automatisé des tests US1.6 - Semaines Lundi-Dimanche
Orchestrateur de tests complet avec reporting et validation des seuils qualité

Usage:
    python scripts/run_us16_tests.py [options]
    
Options:
    --level [unit|integration|e2e|all]  Niveau de tests à exécuter
    --coverage                         Générer rapport de couverture
    --performance                      Exécuter benchmarks performance
    --report                          Générer rapport HTML détaillé
    --fail-fast                       Arrêter à la première erreur
    --parallel                        Exécuter tests en parallèle
"""

import subprocess
import sys
import os
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from dataclasses import dataclass


@dataclass
class TestResult:
    """Résultat d'exécution de test"""
    name: str
    status: str  # 'passed', 'failed', 'skipped'
    duration: float
    coverage: Optional[float] = None
    details: Optional[str] = None
    errors: List[str] = None


class US16TestRunner:
    """Orchestrateur de tests pour US1.6"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        
        # Configuration des seuils qualité
        self.quality_thresholds = {
            'coverage_minimum': 90.0,
            'performance_max_degradation': 2.0,  # 2x plus lent que baseline
            'max_memory_increase_mb': 200,
            'api_response_time_max_ms': 200,
            'migration_time_max_s': 30
        }
        
        # Configuration des suites de tests
        self.test_suites = {
            'unit': [
                'tests/backend/test_date_utils_us16.py',
                'tests/frontend/test_calendar_components_us16.jsx'
            ],
            'integration': [
                'tests/backend/test_meal_plans_api_us16.py',
                'tests/backend/test_migration_us16.py'
            ],
            'performance': [
                'tests/backend/test_performance_us16.py'
            ],
            'e2e': [
                'tests/e2e/test_calendar_workflows_us16.py'
            ]
        }
    
    def run_backend_tests(self, test_file: str, with_coverage: bool = False) -> TestResult:
        """Exécuter tests backend Python avec pytest"""
        print(f"🧪 Exécution tests backend: {test_file}")
        
        cmd = ['python', '-m', 'pytest', test_file, '-v', '--tb=short']
        
        if with_coverage:
            cmd.extend(['--cov=src/backend', '--cov-report=json', '--cov-report=term'])
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            duration = time.time() - start_time
            
            # Parser les résultats pytest
            if result.returncode == 0:
                status = 'passed'
                print(f"✅ {test_file} - PASSED ({duration:.2f}s)")
            else:
                status = 'failed'
                print(f"❌ {test_file} - FAILED ({duration:.2f}s)")
                print(f"   Stderr: {result.stderr}")
            
            # Extraire coverage si disponible
            coverage = None
            if with_coverage and os.path.exists('coverage.json'):
                try:
                    with open('coverage.json', 'r') as f:
                        cov_data = json.load(f)
                        coverage = cov_data.get('totals', {}).get('percent_covered', 0)
                except Exception as e:
                    print(f"⚠️ Erreur lecture coverage: {e}")
            
            return TestResult(
                name=test_file,
                status=status,
                duration=duration,
                coverage=coverage,
                details=result.stdout,
                errors=[result.stderr] if result.stderr else []
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"⏱️ {test_file} - TIMEOUT ({duration:.2f}s)")
            return TestResult(
                name=test_file,
                status='failed',
                duration=duration,
                errors=['Test timeout after 5 minutes']
            )
        
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {test_file} - ERROR ({duration:.2f}s): {e}")
            return TestResult(
                name=test_file,
                status='failed',
                duration=duration,
                errors=[str(e)]
            )
    
    def run_frontend_tests(self, test_file: str, with_coverage: bool = False) -> TestResult:
        """Exécuter tests frontend React avec Jest"""
        print(f"🎨 Exécution tests frontend: {test_file}")
        
        cmd = ['npm', 'test', '--', test_file, '--watchAll=false']
        
        if with_coverage:
            cmd.append('--coverage')
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=180  # 3 minutes timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                status = 'passed'
                print(f"✅ {test_file} - PASSED ({duration:.2f}s)")
            else:
                status = 'failed'
                print(f"❌ {test_file} - FAILED ({duration:.2f}s)")
            
            return TestResult(
                name=test_file,
                status=status,
                duration=duration,
                details=result.stdout,
                errors=[result.stderr] if result.stderr else []
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"💥 {test_file} - ERROR ({duration:.2f}s): {e}")
            return TestResult(
                name=test_file,
                status='failed',
                duration=duration,
                errors=[str(e)]
            )
    
    def run_performance_benchmarks(self) -> TestResult:
        """Exécuter benchmarks de performance avec métriques détaillées"""
        print("🚀 Exécution benchmarks performance US1.6...")
        
        start_time = time.time()
        
        # Commande pytest avec options performance
        cmd = [
            'python', '-m', 'pytest', 
            'tests/backend/test_performance_us16.py',
            '-v', '-s',  # -s pour voir les prints de performance
            '--tb=short'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes pour performance tests
            )
            
            duration = time.time() - start_time
            
            # Parser les métriques de performance depuis stdout
            performance_metrics = self._parse_performance_metrics(result.stdout)
            
            if result.returncode == 0:
                status = 'passed'
                print(f"✅ Performance benchmarks - PASSED ({duration:.2f}s)")
                
                # Vérifier les seuils de performance
                degradation_warnings = self._check_performance_thresholds(performance_metrics)
                if degradation_warnings:
                    print("⚠️ Avertissements performance:")
                    for warning in degradation_warnings:
                        print(f"   {warning}")
            else:
                status = 'failed'
                print(f"❌ Performance benchmarks - FAILED ({duration:.2f}s)")
            
            return TestResult(
                name='performance_benchmarks',
                status=status,
                duration=duration,
                details=result.stdout,
                errors=[result.stderr] if result.stderr else []
            )
            
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name='performance_benchmarks',
                status='failed',
                duration=duration,
                errors=[str(e)]
            )
    
    def _parse_performance_metrics(self, stdout: str) -> Dict[str, float]:
        """Parser les métriques de performance depuis la sortie des tests"""
        metrics = {}
        
        for line in stdout.split('\n'):
            # Rechercher patterns de métriques
            if '10k calculs get_monday_of_week:' in line:
                # Extraire le temps d'exécution
                try:
                    time_str = line.split(':')[1].strip().split('s')[0]
                    metrics['date_calc_10k_time'] = float(time_str)
                except:
                    pass
            
            elif 'Formatage' in line and 'semaines' in line:
                # Métriques de formatage
                try:
                    parts = line.split('-')[1].strip()
                    fr_time = float(parts.split('FR:')[1].split('s')[0].strip())
                    metrics['formatting_time'] = fr_time
                except:
                    pass
            
            elif 'Migration completed in' in line:
                # Temps de migration
                try:
                    time_str = line.split('in')[1].strip().split('s')[0]
                    metrics['migration_time'] = float(time_str)
                except:
                    pass
            
            elif 'Memory usage:' in line:
                # Utilisation mémoire
                try:
                    parts = line.split('+')[1].strip()
                    memory_mb = float(parts.split('MB')[0])
                    metrics['memory_increase_mb'] = memory_mb
                except:
                    pass
        
        return metrics
    
    def _check_performance_thresholds(self, metrics: Dict[str, float]) -> List[str]:
        """Vérifier les seuils de performance et retourner les avertissements"""
        warnings = []
        
        # Baselines de référence (à ajuster selon environnement)
        baselines = {
            'date_calc_10k_time': 1.0,      # 1 seconde baseline
            'formatting_time': 0.5,         # 0.5 seconde baseline  
            'migration_time': 10.0,         # 10 secondes baseline
            'memory_increase_mb': 100.0     # 100MB baseline
        }
        
        for metric, value in metrics.items():
            if metric in baselines:
                baseline = baselines[metric]
                if value > baseline * self.quality_thresholds['performance_max_degradation']:
                    ratio = value / baseline
                    warnings.append(f"Performance dégradée {metric}: {ratio:.2f}x plus lent que baseline")
        
        return warnings
    
    def run_test_suite(self, suite_name: str, options: Dict) -> List[TestResult]:
        """Exécuter une suite complète de tests"""
        print(f"🎯 Exécution suite de tests: {suite_name.upper()}")
        
        if suite_name not in self.test_suites:
            raise ValueError(f"Suite inconnue: {suite_name}")
        
        results = []
        test_files = self.test_suites[suite_name]
        
        if options.get('parallel') and len(test_files) > 1:
            # Exécution parallèle
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_to_test = {}
                
                for test_file in test_files:
                    if test_file.endswith('.py'):
                        future = executor.submit(
                            self.run_backend_tests, 
                            test_file, 
                            options.get('coverage', False)
                        )
                    elif test_file.endswith('.jsx'):
                        future = executor.submit(
                            self.run_frontend_tests, 
                            test_file, 
                            options.get('coverage', False)
                        )
                    
                    future_to_test[future] = test_file
                
                for future in concurrent.futures.as_completed(future_to_test):
                    result = future.result()
                    results.append(result)
                    
                    if options.get('fail_fast') and result.status == 'failed':
                        print(f"🛑 Arrêt prématuré (fail-fast): {result.name}")
                        break
        else:
            # Exécution séquentielle
            for test_file in test_files:
                if test_file.endswith('.py'):
                    result = self.run_backend_tests(
                        test_file, 
                        options.get('coverage', False)
                    )
                elif test_file.endswith('.jsx'):
                    result = self.run_frontend_tests(
                        test_file, 
                        options.get('coverage', False)
                    )
                
                results.append(result)
                
                if options.get('fail_fast') and result.status == 'failed':
                    print(f"🛑 Arrêt prématuré (fail-fast): {result.name}")
                    break
        
        return results
    
    def generate_html_report(self, output_path: Path) -> None:
        """Générer rapport HTML détaillé"""
        print(f"📊 Génération rapport HTML: {output_path}")
        
        total_duration = time.time() - self.start_time
        passed_tests = [r for r in self.test_results if r.status == 'passed']
        failed_tests = [r for r in self.test_results if r.status == 'failed']
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>US1.6 Test Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; gap: 20px; margin: 20px 0; }}
                .metric {{ background: white; border: 1px solid #ddd; padding: 15px; border-radius: 5px; text-align: center; }}
                .passed {{ border-color: #28a745; color: #28a745; }}
                .failed {{ border-color: #dc3545; color: #dc3545; }}
                .test-list {{ margin: 20px 0; }}
                .test-item {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
                .test-item.passed {{ border-left-color: #28a745; }}
                .test-item.failed {{ border-left-color: #dc3545; }}
                .details {{ background: #f8f9fa; padding: 10px; margin: 10px 0; font-family: monospace; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🧪 US1.6 Test Report - Semaines Lundi-Dimanche</h1>
                <p>Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Durée totale: {total_duration:.2f}s</p>
            </div>
            
            <div class="summary">
                <div class="metric passed">
                    <h3>{len(passed_tests)}</h3>
                    <p>Tests Réussis</p>
                </div>
                <div class="metric failed">
                    <h3>{len(failed_tests)}</h3>
                    <p>Tests Échoués</p>
                </div>
                <div class="metric">
                    <h3>{len(self.test_results)}</h3>
                    <p>Total Tests</p>
                </div>
                <div class="metric">
                    <h3>{(len(passed_tests) / len(self.test_results) * 100):.1f}%</h3>
                    <p>Taux Réussite</p>
                </div>
            </div>
            
            <div class="test-list">
                <h2>📋 Détail des Tests</h2>
        """
        
        for result in self.test_results:
            status_class = result.status
            status_icon = "✅" if result.status == 'passed' else "❌"
            
            html_content += f"""
                <div class="test-item {status_class}">
                    <h3>{status_icon} {result.name}</h3>
                    <p>Status: {result.status.upper()} | Durée: {result.duration:.2f}s</p>
            """
            
            if result.coverage:
                html_content += f"<p>Coverage: {result.coverage:.1f}%</p>"
            
            if result.errors:
                html_content += "<div class=\"details\">"
                for error in result.errors:
                    html_content += f"<p>❌ {error}</p>"
                html_content += "</div>"
            
            html_content += "</div>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Rapport généré: {output_path}")
    
    def validate_quality_gates(self) -> Tuple[bool, List[str]]:
        """Valider les quality gates du projet"""
        print("🔍 Validation des quality gates...")
        
        violations = []
        
        # Gate 1: Tous les tests doivent passer
        failed_tests = [r for r in self.test_results if r.status == 'failed']
        if failed_tests:
            violations.append(f"{len(failed_tests)} test(s) échoué(s)")
        
        # Gate 2: Coverage minimum
        coverage_results = [r for r in self.test_results if r.coverage is not None]
        if coverage_results:
            avg_coverage = sum(r.coverage for r in coverage_results) / len(coverage_results)
            if avg_coverage < self.quality_thresholds['coverage_minimum']:
                violations.append(f"Coverage {avg_coverage:.1f}% < {self.quality_thresholds['coverage_minimum']}%")
        
        # Gate 3: Performance acceptable
        performance_result = next((r for r in self.test_results if r.name == 'performance_benchmarks'), None)
        if performance_result and performance_result.status == 'failed':
            violations.append("Benchmarks performance échoués")
        
        is_valid = len(violations) == 0
        
        if is_valid:
            print("✅ Tous les quality gates validés")
        else:
            print("❌ Quality gates violés:")
            for violation in violations:
                print(f"   - {violation}")
        
        return is_valid, violations


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description='Exécuteur de tests US1.6')
    parser.add_argument('--level', choices=['unit', 'integration', 'performance', 'e2e', 'all'], 
                       default='all', help='Niveau de tests à exécuter')
    parser.add_argument('--coverage', action='store_true', help='Générer rapport de couverture')
    parser.add_argument('--performance', action='store_true', help='Inclure benchmarks performance')
    parser.add_argument('--report', action='store_true', help='Générer rapport HTML')
    parser.add_argument('--fail-fast', action='store_true', help='Arrêter à la première erreur')
    parser.add_argument('--parallel', action='store_true', help='Exécuter tests en parallèle')
    
    args = parser.parse_args()
    
    # Initialisation
    project_root = Path(__file__).parent.parent
    runner = US16TestRunner(project_root)
    
    print("🚀 Démarrage des tests US1.6 - Semaines Lundi-Dimanche")
    print(f"   Niveau: {args.level}")
    print(f"   Coverage: {args.coverage}")
    print(f"   Performance: {args.performance}")
    print(f"   Parallèle: {args.parallel}")
    print()
    
    # Configuration des options
    options = {
        'coverage': args.coverage,
        'fail_fast': args.fail_fast,
        'parallel': args.parallel
    }
    
    # Exécution des tests selon le niveau
    if args.level == 'all':
        test_levels = ['unit', 'integration', 'e2e']
        if args.performance:
            test_levels.append('performance')
    else:
        test_levels = [args.level]
    
    # Exécuter chaque niveau de test
    for level in test_levels:
        if level == 'performance':
            result = runner.run_performance_benchmarks()
            runner.test_results.append(result)
        else:
            results = runner.run_test_suite(level, options)
            runner.test_results.extend(results)
    
    print()
    print("📊 Résumé de l'exécution:")
    
    passed = len([r for r in runner.test_results if r.status == 'passed'])
    failed = len([r for r in runner.test_results if r.status == 'failed'])
    total = len(runner.test_results)
    
    print(f"   ✅ Réussis: {passed}")
    print(f"   ❌ Échoués: {failed}")
    print(f"   📝 Total: {total}")
    print(f"   ⏱️ Durée: {time.time() - runner.start_time:.2f}s")
    
    # Validation quality gates
    print()
    gates_valid, violations = runner.validate_quality_gates()
    
    # Génération du rapport si demandé
    if args.report:
        report_path = project_root / 'test-reports' / f'us16-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.html'
        report_path.parent.mkdir(exist_ok=True)
        runner.generate_html_report(report_path)
    
    # Code de sortie
    if failed > 0 or not gates_valid:
        print("\n❌ Tests US1.6 - ÉCHEC")
        sys.exit(1)
    else:
        print("\n✅ Tests US1.6 - SUCCÈS")
        sys.exit(0)


if __name__ == '__main__':
    main()