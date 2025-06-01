# core/config/validator.py
"""
Sistema di validazione per le configurazioni di gioco
Garantisce la coerenza e correttezza dei valori in tutti i moduli
"""

import sys
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

from .time_config import MXY, DXM, DXW
from .social_config import AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS
from npc_config import MAX_TRAITS_PER_NPC

# Struttura per memorizzare i risultati della validazione
@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class ConfigValidator:
    def __init__(self):
        self.rules = self._build_validation_rules()
        self.results: Dict[str, ValidationResult] = {}
    
    def _build_validation_rules(self) -> Dict[str, List[Tuple]]:
        """Definisce le regole di validazione per ogni modulo"""
        return {
            'time_config': [
                ('HXD', self._check_positive_int, "Ore per giorno deve essere intero positivo"),
                ('DXM', self._check_positive_int, "Giorni per mese deve essere intero positivo"),
                ('MXY', self._check_positive_int, "Mesi per anno deve essere intero positivo"),
                ('DXY', lambda v: v == MXY * DXM, "DXY deve essere MXY * DXM"),
                ('MONTH_NAMES', lambda v: len(v) == MXY, f"Deve esserci {MXY} nomi di mesi"),
                ('DAY_NAMES', lambda v: len(v) == DXW, f"Deve esserci {DXW} nomi di giorni"),
            ],
            'npc_config': [
                ('MIN_TRAITS_PER_NPC', lambda v: 1 <= v <= MAX_TRAITS_PER_NPC, 
                 "MIN_TRAITS_PER_NPC deve essere <= MAX_TRAITS_PER_NPC"),
                ('LIFE_STAGE_AGE_THRESHOLDS_DAYS', self._check_ascending_thresholds,
                 "Soglie età devono essere in ordine crescente"),
                ('NEED_DECAY_RATES', self._check_negative_values,
                 "Tassi decadimento bisogni devono essere negativi"),
                ('NEED_CRITICAL_THRESHOLD', lambda v: 0 <= v <= 100,
                 "Soglia critica bisogni deve essere tra 0 e 100"),
            ],
            'school_config': [
                ('SCHOOL_LEVELS', self._check_school_levels,
                 "Livelli scolastici devono avere età di inizio e durata coerenti"),
                ('PERFORMANCE_THRESHOLDS', self._check_performance_thresholds,
                 "Soglie prestazioni devono essere in ordine decrescente"),
            ],
            'economy_config': [
                ('TAX_BRACKETS_CSC_R', self._check_tax_brackets,
                 "Scaglioni fiscali devono essere ordinati e con aliquote crescenti"),
                ('SALARY_RANGES_ATHEL_ANNUAL', self._check_salary_ranges,
                 "Range salariali devono avere min <= max"),
            ],
            'social_config': [
                ('DATING_CANDIDATE_MIN_AGE_DAYS', 
                 lambda v: v >= AMORI_CURATI_PHASE1_ACCESS_MIN_AGE_DAYS,
                 "Età minima appuntamenti deve essere >= età minima servizio Amori Curati"),
            ],
            'environment_config': [
                ('PLANET_AXIAL_TILT_DEGREES', lambda v: -90 <= v <= 90,
                 "Inclinazione assiale deve essere tra -90 e 90 gradi"),
                ('PLANET_ORBITAL_ECCENTRICITY', lambda v: 0 <= v < 1,
                 "Eccentricità orbitale deve essere tra 0 e 1"),
            ]
        }
    
    def validate_all(self, config_modules: Dict[str, Any]):
        """Esegue la validazione su tutti i moduli"""
        for module_name, module in config_modules.items():
            result = ValidationResult(is_valid=True, errors=[], warnings=[])
            
            if module_name in self.rules:
                for const_name, validation_func, error_msg in self.rules[module_name]:
                    try:
                        value = getattr(module, const_name)
                        if not validation_func(value):
                            result.is_valid = False
                            result.errors.append(f"{const_name}: {error_msg}")
                    except AttributeError:
                        result.is_valid = False
                        result.errors.append(f"Costante mancante: {const_name}")
            
            # Validazioni incrociate tra moduli
            if module_name == 'npc_config':
                self._validate_npc_cross_module(module, result)
            
            self.results[module_name] = result
        
        return self.results
    
    def _validate_npc_cross_module(self, module, result):
        """Validazioni specifiche per NPC che coinvolgono altri moduli"""
        try:
            max_age = module.MAX_AGE_FOR_INTIMACY_DAYS
            min_age = module.MIN_AGE_FOR_INTIMACY_DAYS
            if min_age >= max_age:
                result.is_valid = False
                result.errors.append(
                    f"MIN_AGE_FOR_INTIMACY_DAYS ({min_age}) deve essere < "
                    f"MAX_AGE_FOR_INTIMACY_DAYS ({max_age})"
                )
                
            # Verifica coerenza con le fasi di vita
            elder_start = module.LIFE_STAGE_AGE_THRESHOLDS_DAYS["ELDERLY"]
            if max_age < elder_start:
                result.warnings.append(
                    "MAX_AGE_FOR_INTIMACY_DAYS è inferiore all'inizio della fase ELDERLY. "
                    "Gli anziani non potranno avere relazioni intime."
                )
        except AttributeError as e:
            result.is_valid = False
            result.errors.append(f"Errore validazione incrociata: {str(e)}")

    # --- Funzioni di validazione generiche ---
    def _check_positive_int(self, value) -> bool:
        return isinstance(value, int) and value > 0
    
    def _check_negative_values(self, values: Dict) -> bool:
        return all(v < 0 for v in values.values())
    
    def _check_ascending_thresholds(self, thresholds: Dict) -> bool:
        values = list(thresholds.values())
        return all(values[i] <= values[i+1] for i in range(len(values)-1))
    
    def _check_performance_thresholds(self, thresholds: Dict) -> bool:
        values = list(thresholds.values())
        return all(values[i] >= values[i+1] for i in range(len(values)-1))
    
    def _check_tax_brackets(self, brackets: List[Tuple]) -> bool:
        prev_upper = -float('inf')
        prev_rate = -float('inf')
        
        for upper, rate in brackets:
            if upper <= prev_upper:
                return False
            if rate < prev_rate:
                return False
            prev_upper = upper
            prev_rate = rate
        return True
    
    def _check_salary_ranges(self, ranges: Dict) -> bool:
        return all(min_val <= max_val for min_val, max_val in ranges.values())
    
    def _check_school_levels(self, levels: Dict) -> bool:
        prev_end = 0
        for name, data in levels.items():
            start = data["start_age"]
            duration = data["duration"]
            
            if start < prev_end:
                return False
            if duration <= 0:
                return False
            prev_end = start + duration
        return True

    # --- Funzioni di reporting ---
    def generate_report(self) -> str:
        """Genera un report di validazione in formato Markdown"""
        report = ["# Config Validation Report\n"]
        total_errors = 0
        total_warnings = 0
        
        for module_name, result in self.results.items():
            status = "✅ VALID" if result.is_valid else "❌ INVALID"
            report.append(f"## {module_name} - {status}\n")
            
            if result.errors:
                report.append("### Errors")
                for error in result.errors:
                    report.append(f"- {error}")
                    total_errors += 1
            
            if result.warnings:
                report.append("\n### Warnings")
                for warning in result.warnings:
                    report.append(f"- ⚠️ {warning}")
                    total_warnings += 1
            
            if not result.errors and not result.warnings:
                report.append("No issues found\n")
            
            report.append("\n---\n")
        
        summary = (
            f"\n## Summary\n"
            f"- Total Modules: {len(self.results)}\n"
            f"- Total Errors: {total_errors}\n"
            f"- Total Warnings: {total_warnings}\n"
            f"- Validation Status: {'PASS' if total_errors == 0 else 'FAIL'}"
        )
        report.append(summary)
        
        return "\n".join(report)
    
    def exit_on_critical_errors(self):
        """Esce dal programma se ci sono errori critici"""
        critical_errors = any(not result.is_valid for result in self.results.values())
        
        if critical_errors:
            print("\n🚨 CRITICAL CONFIGURATION ERRORS DETECTED!")
            print(self.generate_report())
            sys.exit(1)

# Funzione di utilità per l'integrazione
def validate_config_system(config_proxy):
    """Funzione principale per la validazione dell'intero sistema"""
    validator = ConfigValidator()
    
    # Estrae i moduli effettivi dal proxy
    config_modules = {
        name: module 
        for name, module in config_proxy._ConfigProxy__config_modules__.items()
    }
    
    results = validator.validate_all(config_modules)
    
    print("Config Validation Completed")
    print(validator.generate_report())
    
    validator.exit_on_critical_errors()
    return results