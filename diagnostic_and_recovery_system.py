import numpy as np
import torch
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum, auto
import time
import logging
import json

class SystemState(Enum):
    NORMAL = auto()
    WARNING = auto()
    CRITICAL = auto()
    RECOVERY = auto()
    DIAGNOSTIC = auto()

@dataclass
class DiagnosticResult:
    """System diagnostic results"""
    status: SystemState
    issues: List[str]
    metrics: Dict[str, float]
    timestamp: float
    recovery_needed: bool

class DiagnosticAndRecoverySystem:
    """Comprehensive diagnostic and recovery system"""
    
    def __init__(self):
        # Initialize logging
        self.logger = self._setup_logger()
        
        # System components
        self.components = {
            'motors': {},
            'sensors': {},
            'power': {},
            'communication': {},
            'processing': {}
        }
        
        # Diagnostic thresholds
        self.thresholds = {
            'response_time': 0.001,  # 1ms
            'temperature': 60.0,     # 60°C
            'voltage': 22.0,         # 22V minimum
            'current': 20.0,         # 20A maximum
            'packet_loss': 0.01      # 1% maximum
        }
        
        # Recovery procedures
        self.recovery_procedures = self._initialize_recovery()
        
        # System state
        self.state = SystemState.NORMAL
        self.diagnostic_history = []
        self.recovery_history = []
        
    def _setup_logger(self) -> logging.Logger:
        """Setup system logger"""
        logger = logging.getLogger('DiagnosticSystem')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('system_diagnostics.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _initialize_recovery(self) -> Dict:
        """Initialize recovery procedures"""
        return {
            'motor_failure': self._recover_motor,
            'sensor_failure': self._recover_sensor,
            'communication_failure': self._recover_communication,
            'power_failure': self._recover_power,
            'software_failure': self._recover_software
        }
    
    async def run_diagnostics(self) -> DiagnosticResult:
        """Run comprehensive system diagnostics"""
        self.state = SystemState.DIAGNOSTIC
        issues = []
        metrics = {}
        
        try:
            # Check hardware components
            motor_status = await self._check_motors()
            sensor_status = await self._check_sensors()
            power_status = await self._check_power()
            
            # Check software components
            comm_status = await self._check_communication()
            proc_status = await self._check_processing()
            
            # Combine results
            all_status = [
                motor_status,
                sensor_status,
                power_status,
                comm_status,
                proc_status
            ]
            
            # Collect issues and metrics
            for status in all_status:
                issues.extend(status.get('issues', []))
                metrics.update(status.get('metrics', {}))
            
            # Determine system state
            if any(issue.startswith('CRITICAL:') for issue in issues):
                self.state = SystemState.CRITICAL
            elif issues:
                self.state = SystemState.WARNING
            else:
                self.state = SystemState.NORMAL
            
            # Create diagnostic result
            result = DiagnosticResult(
                status=self.state,
                issues=issues,
                metrics=metrics,
                timestamp=time.time(),
                recovery_needed=self.state in [SystemState.WARNING, SystemState.CRITICAL]
            )
            
            # Store diagnostic history
            self.diagnostic_history.append(result)
            
            # Log results
            self._log_diagnostic_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Diagnostic error: {str(e)}")
            return DiagnosticResult(
                status=SystemState.CRITICAL,
                issues=[f"CRITICAL: Diagnostic failure - {str(e)}"],
                metrics={},
                timestamp=time.time(),
                recovery_needed=True
            )
    
    async def _check_motors(self) -> Dict:
        """Check motor status"""
        issues = []
        metrics = {}
        
        for motor_id, motor in self.components['motors'].items():
            # Check temperature
            temp = await self._get_motor_temperature(motor_id)
            metrics[f"motor_{motor_id}_temp"] = temp
            if temp > self.thresholds['temperature']:
                issues.append(f"CRITICAL: Motor {motor_id} overheating: {temp}°C")
            
            # Check current
            current = await self._get_motor_current(motor_id)
            metrics[f"motor_{motor_id}_current"] = current
            if current > self.thresholds['current']:
                issues.append(f"CRITICAL: Motor {motor_id} overcurrent: {current}A")
            
            # Check response time
            response_time = await self._check_motor_response(motor_id)
            metrics[f"motor_{motor_id}_response"] = response_time
            if response_time > self.thresholds['response_time']:
                issues.append(f"WARNING: Motor {motor_id} slow response: {response_time*1000}ms")
        
        return {'issues': issues, 'metrics': metrics}
    
    async def _check_sensors(self) -> Dict:
        """Check sensor status"""
        issues = []
        metrics = {}
        
        for sensor_id, sensor in self.components['sensors'].items():
            # Check data validity
            data_valid = await self._verify_sensor_data(sensor_id)
            metrics[f"sensor_{sensor_id}_valid"] = float(data_valid)
            if not data_valid:
                issues.append(f"WARNING: Sensor {sensor_id} data invalid")
            
            # Check update rate
            update_rate = await self._check_sensor_rate(sensor_id)
            metrics[f"sensor_{sensor_id}_rate"] = update_rate
            if update_rate < 100:  # 100Hz minimum
                issues.append(f"WARNING: Sensor {sensor_id} slow update: {update_rate}Hz")
        
        return {'issues': issues, 'metrics': metrics}
    
    async def _check_power(self) -> Dict:
        """Check power system"""
        issues = []
        metrics = {}
        
        # Check voltage
        voltage = await self._get_system_voltage()
        metrics['system_voltage'] = voltage
        if voltage < self.thresholds['voltage']:
            issues.append(f"CRITICAL: Low system voltage: {voltage}V")
        
        # Check current draw
        current = await self._get_system_current()
        metrics['system_current'] = current
        if current > self.thresholds['current']:
            issues.append(f"CRITICAL: High system current: {current}A")
        
        return {'issues': issues, 'metrics': metrics}
    
    async def _check_communication(self) -> Dict:
        """Check communication system"""
        issues = []
        metrics = {}
        
        # Check packet loss
        packet_loss = await self._measure_packet_loss()
        metrics['packet_loss'] = packet_loss
        if packet_loss > self.thresholds['packet_loss']:
            issues.append(f"WARNING: High packet loss: {packet_loss*100}%")
        
        # Check latency
        latency = await self._measure_latency()
        metrics['communication_latency'] = latency
        if latency > self.thresholds['response_time']:
            issues.append(f"WARNING: High latency: {latency*1000}ms")
        
        return {'issues': issues, 'metrics': metrics}
    
    async def recover_system(self, diagnostic_result: DiagnosticResult) -> bool:
        """Attempt system recovery"""
        if not diagnostic_result.recovery_needed:
            return True
            
        self.state = SystemState.RECOVERY
        recovery_successful = True
        
        try:
            # Handle each issue
            for issue in diagnostic_result.issues:
                if issue.startswith("CRITICAL:"):
                    # Critical issues need immediate attention
                    await self._handle_critical_issue(issue)
                else:
                    # Warning issues can be handled more gradually
                    await self._handle_warning_issue(issue)
            
            # Verify recovery
            verification = await self.run_diagnostics()
            recovery_successful = verification.status == SystemState.NORMAL
            
            # Record recovery attempt
            self.recovery_history.append({
                'timestamp': time.time(),
                'issues': diagnostic_result.issues,
                'success': recovery_successful,
                'new_state': verification.status
            })
            
            # Log recovery results
            self._log_recovery_result(recovery_successful)
            
            return recovery_successful
            
        except Exception as e:
            self.logger.error(f"Recovery error: {str(e)}")
            return False
    
    async def _handle_critical_issue(self, issue: str):
        """Handle critical system issue"""
        if "Motor" in issue:
            motor_id = issue.split()[1]
            await self.recovery_procedures['motor_failure'](motor_id)
        elif "voltage" in issue.lower():
            await self.recovery_procedures['power_failure']()
        elif "current" in issue.lower():
            await self._handle_overcurrent()
    
    async def _handle_warning_issue(self, issue: str):
        """Handle warning level issue"""
        if "Sensor" in issue:
            sensor_id = issue.split()[1]
            await self.recovery_procedures['sensor_failure'](sensor_id)
        elif "packet loss" in issue.lower():
            await self.recovery_procedures['communication_failure']()
        elif "latency" in issue.lower():
            await self._optimize_communication()
    
    async def _recover_motor(self, motor_id: str):
        """Recover failed motor"""
        # Emergency stop
        await self._emergency_stop_motor(motor_id)
        
        # Reset controller
        await self._reset_motor_controller(motor_id)
        
        # Recalibrate
        await self._recalibrate_motor(motor_id)
        
        # Test operation
        await self._test_motor_operation(motor_id)
    
    async def _recover_sensor(self, sensor_id: str):
        """Recover failed sensor"""
        # Reset sensor
        await self._reset_sensor(sensor_id)
        
        # Recalibrate
        await self._recalibrate_sensor(sensor_id)
        
        # Verify data
        await self._verify_sensor_operation(sensor_id)
    
    def _log_diagnostic_result(self, result: DiagnosticResult):
        """Log diagnostic results"""
        self.logger.info(
            f"Diagnostic completed - Status: {result.status.name}\n"
            f"Issues: {len(result.issues)}\n"
            f"Metrics: {json.dumps(result.metrics, indent=2)}"
        )
        
        if result.issues:
            for issue in result.issues:
                self.logger.warning(f"Issue detected: {issue}")
    
    def _log_recovery_result(self, success: bool):
        """Log recovery results"""
        if success:
            self.logger.info("System recovery successful")
        else:
            self.logger.error("System recovery failed")

async def main():
    """Test diagnostic and recovery system"""
    system = DiagnosticAndRecoverySystem()
    
    # Run diagnostics
    print("Running system diagnostics...")
    result = await system.run_diagnostics()
    
    print(f"\nDiagnostic Results:")
    print(f"Status: {result.status.name}")
    print(f"Issues Found: {len(result.issues)}")
    if result.issues:
        print("\nIssues:")
        for issue in result.issues:
            print(f"- {issue}")
    
    if result.recovery_needed:
        print("\nAttempting system recovery...")
        success = await system.recover_system(result)
        print(f"Recovery {'successful' if success else 'failed'}")

if __name__ == "__main__":
    asyncio.run(main())
