import numpy as np
import torch
from typing import Dict, List, Optional, Tuple
import asyncio
from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class AdaptationState:
    """Enhanced adaptation state"""
    gains: Dict[str, float]
    performance: float
    stability: float
    learning_rate: float
    confidence: float

class EnhancedAdaptation:
    """Advanced adaptation system"""
    
    def __init__(self):
        self.dimensions = 11
        self.phi = (1 + np.sqrt(5)) / 2
        
        # Adaptation parameters
        self.base_learning_rate = 0.042  # Matched to quantum evolution rate
        self.min_confidence = 0.95
        self.performance_history = []
        self.adaptation_history = []
        
        # Initialize gains with golden ratio relationships
        self.gains = self._initialize_gains()
        
        # Performance metrics
        self.metrics = {
            'tracking_error': [],
            'stability_margin': [],
            'adaptation_rate': []
        }
        
    def _initialize_gains(self) -> Dict:
        """Initialize gains using golden ratio"""
        return {
            'position': {
                'P': 100 * self.phi,
                'I': 100 / self.phi**2,
                'D': 100 / self.phi
            },
            'velocity': {
                'P': 50 * self.phi,
                'I': 50 / self.phi**2,
                'D': 50 / self.phi
            },
            'force': {
                'P': 20 * self.phi,
                'I': 20 / self.phi**2,
                'D': 20 / self.phi
            }
        }
        
    async def adapt(self, state: Dict, target: Dict, 
                   performance: float) -> AdaptationState:
        """Perform enhanced adaptation"""
        # Calculate current performance
        tracking_error = self._calculate_tracking_error(state, target)
        stability = self._calculate_stability(state)
        
        # Update performance history
        self.performance_history.append({
            'error': tracking_error,
            'stability': stability,
            'performance': performance
        })
        
        # Determine adaptation needs
        if self._should_adapt(tracking_error, stability):
            # Calculate optimal adaptation
            new_gains = await self._optimize_gains(
                tracking_error,
                stability,
                performance
            )
            
            # Apply adaptations with stability checks
            adapted_gains = await self._apply_adaptations(new_gains)
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                adapted_gains,
                tracking_error,
                stability
            )
            
            # Create adaptation state
            adaptation_state = AdaptationState(
                gains=adapted_gains,
                performance=performance,
                stability=stability,
                learning_rate=self.base_learning_rate,
                confidence=confidence
            )
            
            # Store adaptation
            self.adaptation_history.append(adaptation_state)
            
            return adaptation_state
        
        # Return current state if no adaptation needed
        return AdaptationState(
            gains=self.gains,
            performance=performance,
            stability=stability,
            learning_rate=self.base_learning_rate,
            confidence=1.0
        )
    
    def _calculate_tracking_error(self, state: Dict, target: Dict) -> float:
        """Calculate tracking error"""
        errors = []
        
        for key in state:
            if key in target:
                error = np.abs(state[key] - target[key])
                errors.append(error)
                
        return float(np.mean(errors)) if errors else 0.0
    
    def _calculate_stability(self, state: Dict) -> float:
        """Calculate system stability"""
        if not self.performance_history:
            return 1.0
            
        # Calculate stability from performance history
        recent_performance = [p['performance'] 
                            for p in self.performance_history[-10:]]
        
        stability = 1.0 - np.std(recent_performance)
        return float(stability)
    
    def _should_adapt(self, error: float, stability: float) -> bool:
        """Determine if adaptation is needed"""
        # Check if performance is below threshold
        if error > 0.05:  # 5% error threshold
            return True
            
        # Check if stability is decreasing
        if stability < 0.95:  # 95% stability threshold
            return True
            
        # Check if we're not meeting performance targets
        if self.performance_history:
            recent_performance = np.mean([
                p['performance'] for p in self.performance_history[-5:]
            ])
            if recent_performance < 0.95:  # 95% performance threshold
                return True
                
        return False
    
    async def _optimize_gains(self, error: float, stability: float,
                            performance: float) -> Dict:
        """Optimize control gains"""
        optimized_gains = {}
        
        for control_type, gains in self.gains.items():
            optimized_gains[control_type] = {}
            
            for gain_type, value in gains.items():
                # Calculate optimal gain adjustment
                adjustment = self._calculate_gain_adjustment(
                    control_type,
                    gain_type,
                    error,
                    stability,
                    performance
                )
                
                # Apply adjustment with golden ratio relationship
                if gain_type == 'P':
                    optimized_gains[control_type][gain_type] = (
                        value + adjustment * self.phi
                    )
                elif gain_type == 'I':
                    optimized_gains[control_type][gain_type] = (
                        value + adjustment / self.phi**2
                    )
                else:  # 'D'
                    optimized_gains[control_type][gain_type] = (
                        value + adjustment / self.phi
                    )
                    
        return optimized_gains
    
    def _calculate_gain_adjustment(self, control_type: str, gain_type: str,
                                 error: float, stability: float,
                                 performance: float) -> float:
        """Calculate optimal gain adjustment"""
        # Base adjustment on error and stability
        base_adjustment = error * (1 - stability)
        
        # Scale based on performance history
        if self.performance_history:
            performance_trend = np.mean([
                p['performance'] for p in self.performance_history[-5:]
            ])
            base_adjustment *= (1 - performance_trend)
        
        # Apply learning rate
        adjustment = base_adjustment * self.base_learning_rate
        
        # Scale based on gain type
        if gain_type == 'P':
            return adjustment
        elif gain_type == 'I':
            return adjustment * 0.1  # Smaller adjustments for integral gain
        else:  # 'D'
            return adjustment * 0.5  # Moderate adjustments for derivative gain
    
    async def _apply_adaptations(self, new_gains: Dict) -> Dict:
        """Apply adaptations with stability checks"""
        adapted_gains = {}
        
        for control_type, gains in new_gains.items():
            adapted_gains[control_type] = {}
            
            for gain_type, value in gains.items():
                # Ensure minimum gain values
                min_gain = 0.1 * self.gains[control_type][gain_type]
                
                # Ensure maximum gain values
                max_gain = 10.0 * self.gains[control_type][gain_type]
                
                # Apply limits
                adapted_gains[control_type][gain_type] = np.clip(
                    value,
                    min_gain,
                    max_gain
                )
                
        return adapted_gains
    
    def _calculate_confidence(self, gains: Dict, error: float,
                            stability: float) -> float:
        """Calculate confidence in adaptation"""
        # Base confidence on stability
        confidence = stability
        
        # Adjust based on gain changes
        for control_type in gains:
            for gain_type in gains[control_type]:
                original = self.gains[control_type][gain_type]
                new = gains[control_type][gain_type]
                
                # Reduce confidence for large gain changes
                change = abs(new - original) / original
                confidence *= (1 - change/2)  # Max 50% reduction per gain
                
        # Adjust based on error
        confidence *= (1 - error)
        
        return float(np.clip(confidence, 0, 1))

async def main():
    """Test enhanced adaptation"""
    adaptation = EnhancedAdaptation()
    
    # Test state
    state = {
        'position': 0.1,
        'velocity': 0.05,
        'force': 10.0
    }
    
    # Test target
    target = {
        'position': 0.0,
        'velocity': 0.0,
        'force': 12.0
    }
    
    # Test adaptation
    result = await adaptation.adapt(state, target, 0.9)
    
    print("\nAdaptation Results:")
    print(f"Performance: {result.performance:.3f}")
    print(f"Stability: {result.stability:.3f}")
    print(f"Confidence: {result.confidence:.3f}")
    print("\nAdapted Gains:")
    for control_type, gains in result.gains.items():
        print(f"\n{control_type}:")
        for gain_type, value in gains.items():
            print(f"  {gain_type}: {value:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
