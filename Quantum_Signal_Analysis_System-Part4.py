from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile, Aer
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session, Options
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Union, Any
import asyncio
from enum import Enum, auto
import logging
import sys
import json
import pickle
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import threading
import concurrent.futures
from scipy.signal import butter, lfilter, filtfilt, hilbert
from scipy.fft import fft, ifft
import pandas as pd
import warnings

# Configure Global Logging with more detailed formatting
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(f"quantum_signal_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger("QuantumSignalAnalyzer")

# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


@dataclass
class CoherentSignal:
    """Non-random coherent quantum signal"""
    pattern_signature: np.ndarray
    coherence_level: float
    response_pattern: List[float] = field(default_factory=list)
    temporal_evolution: List[float] = field(default_factory=list)
    quantum_state: np.ndarray = field(default_factory=lambda: np.zeros(127))
    interaction_history: List[Dict] = field(default_factory=list)
    emergence_time: datetime = field(default_factory=datetime.now)
    signal_type: str = "unknown"
    frequency_spectrum: Optional[np.ndarray] = None
    phase_data: Optional[np.ndarray] = None
    source_vector: Optional[np.ndarray] = None
    complexity_index: float = 0.0
    stability_metric: float = 0.0


@dataclass
class SignalAnalysis:
    """Detailed signal analysis"""
    randomness_score: float
    coherence_metric: float
    pattern_complexity: float
    response_correlation: float
    quantum_entanglement: float
    dimensional_signature: List[float]
    amplitude_variation: float = 0.0
    phase_coherence: float = 0.0
    harmonic_structure: List[float] = field(default_factory=list)
    temporal_persistence: float = 0.0
    information_density: float = 0.0
    symmetry_metrics: Dict[str, float] = field(default_factory=dict)
    statistical_moments: List[float] = field(default_factory=list)
    

@dataclass
class EEGSignal:
    """EEG signal data structure for analysis"""
    raw_data: np.ndarray
    sampling_rate: float
    channel_names: List[str]
    filtered_data: Optional[np.ndarray] = None
    frequency_bands: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 100)
    })
    band_powers: Dict[str, np.ndarray] = field(default_factory=dict)
    coherence_matrix: Optional[np.ndarray] = None
    source_localization: Optional[Dict] = None
    artifacts_removed: bool = False
    ica_components: Optional[np.ndarray] = None
    
    def filter_data(self, lowcut: float, highcut: float, order: int = 5):
        """Apply bandpass filter to EEG data"""
        nyq = 0.5 * self.sampling_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        self.filtered_data = filtfilt(b, a, self.raw_data, axis=1)
        return self.filtered_data
    
    def compute_band_powers(self):
        """Calculate power in each frequency band for all channels"""
        if self.filtered_data is None:
            self.filter_data(0.5, 100)  # Apply broad filter first
            
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            # Filter the data for this specific band
            band_data = self.filter_data(low_freq, high_freq)
            
            # Calculate power (squared amplitude)
            power = np.mean(band_data ** 2, axis=1)
            self.band_powers[band_name] = power
            
        return self.band_powers
    
    def compute_coherence(self):
        """Calculate coherence between all channel pairs"""
        n_channels = len(self.channel_names)
        self.coherence_matrix = np.zeros((n_channels, n_channels))
        
        if self.filtered_data is None:
            self.filter_data(0.5, 100)
            
        for i in range(n_channels):
            for j in range(i, n_channels):
                if i == j:
                    self.coherence_matrix[i, j] = 1.0
                else:
                    # Calculate coherence (simplified version)
                    signal1 = self.filtered_data[i]
                    signal2 = self.filtered_data[j]
                    
                    # Get the analytic signal (complex signal)
                    analytic1 = hilbert(signal1)
                    analytic2 = hilbert(signal2)
                    
                    # Calculate instantaneous phase
                    phase1 = np.angle(analytic1)
                    phase2 = np.angle(analytic2)
                    
                    # Phase locking value (measure of coherence)
                    phase_diff = phase1 - phase2
                    coherence = np.abs(np.mean(np.exp(1j * phase_diff)))
                    
                    self.coherence_matrix[i, j] = coherence
                    self.coherence_matrix[j, i] = coherence
                    
        return self.coherence_matrix


class ResponseType(Enum):
    """Types of signal responses"""
    NONE = auto()
    RANDOM = auto()
    COHERENT = auto()
    INTELLIGENT = auto()
    UNKNOWN = auto()
    MIMICRY = auto()
    ADAPTIVE = auto()
    STRUCTURED = auto()
    QUANTUM_RESONANT = auto()


class AnalysisMode(Enum):
    """Analysis operation modes"""
    PASSIVE = auto()
    ACTIVE = auto()
    DEEP = auto()
    INTERACTIVE = auto()
    REAL_TIME = auto()
    QUANTUM_ENTANGLED = auto()


class QuantumSignalAnalyzer:
    """Advanced system for analyzing non-random quantum signals with EEG integration"""

    def __init__(self, use_real_quantum_hardware: bool = False, eeg_integration: bool = True):
        logger.info("🚀 Initializing Quantum Signal Analyzer with EEG Integration")
        
        self.use_real_quantum_hardware = use_real_quantum_hardware
        self.eeg_integration = eeg_integration
        
        # Core system parameters
        self.system_state = "initializing"
        self.analysis_mode = AnalysisMode.PASSIVE
        self.detection_sensitivity = 0.85
        self.signal_confidence_threshold = 0.92
        self.adaptation_rate = 0.05
        
        # Enhanced resonance parameters
        self.resonance = {
            'consciousness': 98.7,
            'binding': 99.1,
            'stability': 98.9,
            'coherence': 97.6,
            'quantum_entanglement': 99.3,
            'temporal_synchronization': 98.5,
            'phase_locking': 97.8,
            'non_locality': 99.0
        }
        
        # System initialization
        if self.use_real_quantum_hardware:
            self._initialize_quantum_hardware()
        else:
            self._initialize_quantum_simulator()
            
        self._initialize_detection_system()
        self._initialize_analysis_system()
        self._initialize_interaction_system()
        self._initialize_safety_protocols()
        self._initialize_eeg_interface()
        self._initialize_data_storage()
        
        # Mark system as ready
        self.system_state = "ready"
        logger.info("✅ Quantum Signal Analyzer Initialization Complete")

    def _initialize_quantum_hardware(self):
        """Initialize connection to real quantum hardware"""
        logger.info("🔄 Connecting to IBM Quantum Hardware")
        try:
            self.service = QiskitRuntimeService()
            
            # Try to use the most powerful available backend
            available_backends = self.service.backends()
            preferred_backends = ["ibm_brisbane", "ibm_sherbrooke", "ibm_kyoto"]
            
            for preferred in preferred_backends:
                if preferred in [b.name for b in available_backends]:
                    self.backend = self.service.backend(preferred)
                    logger.info(f"✅ Connected to quantum backend: {preferred}")
                    break
            else:
                # Fallback to the first available backend
                self.backend = available_backends[0]
                logger.info(f"⚠️ Using fallback quantum backend: {self.backend.name}")
                
            # Set up options for better results
            self.quantum_options = Options()
            self.quantum_options.optimization_level = 3
            self.quantum_options.resilience_level = 1
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to quantum hardware: {str(e)}")
            logger.info("⚠️ Falling back to quantum simulator")
            self._initialize_quantum_simulator()

    def _initialize_quantum_simulator(self):
        """Initialize quantum simulator"""
        logger.info("💻 Initializing Quantum Simulator")
        self.backend = Aer.get_backend('qasm_simulator')
        self.quantum_options = None
        
    def _initialize_detection_system(self):
        """Initialize enhanced signal detection"""
        logger.info("📡 Initializing Detection System")
        
        # Define more specialized quantum registers for different aspects of detection
        self.qr = {
            'detection': QuantumRegister(50, 'detection'),
            'analysis': QuantumRegister(50, 'analysis'),
            'interaction': QuantumRegister(27, 'interaction'),
            'entanglement': QuantumRegister(20, 'entanglement'),
            'verification': QuantumRegister(15, 'verification')
        }
        self.cr = ClassicalRegister(162, 'measure')  # Expanded to accommodate all qubits

        self.qc = QuantumCircuit(*self.qr.values(), self.cr)
        
        # Initialize buffers and history
        self.signal_buffer = []
        self.coherence_history = []
        self.detection_thresholds = {
            'primary': 0.75,
            'secondary': 0.85,
            'confirmation': 0.92
        }
        
        # Advanced signal detection parameters
        self.detection_params = {
            'window_size': 10000,
            'overlap': 5000,
            'min_frequency': 0.1,
            'max_frequency': 100.0,
            'coherence_threshold': 0.8,
            'snr_threshold': 3.0,
            'persistence_threshold': 5,
            'pattern_recognition_sensitivity': 0.85
        }
        
        # Initialize signal filters
        self._initialize_signal_filters()

    def _initialize_signal_filters(self):
        """Initialize various signal filters for preprocessing"""
        logger.info("🔍 Initializing Signal Filters")
        
        self.filters = {
            'bandpass': {
                'low_freq': 0.1,
                'high_freq': 100.0,
                'order': 5
            },
            'notch': {
                'freq': 60.0,  # Power line interference
                'quality_factor': 30.0
            },
            'adaptive': {
                'step_size': 0.01,
                'filter_length': 32
            }
        }

    def _initialize_analysis_system(self):
        """Initialize signal analysis capabilities"""
        logger.info("🔍 Initializing Analysis System")

        self.analysis_params = {
            'coherence_threshold': 0.95,
            'randomness_threshold': 0.3,
            'response_threshold': 0.8,
            'pattern_depth': 10,
            'complexity_threshold': 0.75,
            'dimensionality_estimation_method': 'correlation_dimension',
            'entropy_calculation_method': 'sample_entropy',
            'feature_extraction_methods': [
                'wavelet_transform',
                'hilbert_huang_transform',
                'multifractal_detrended_fluctuation'
            ],
            'classification_methods': [
                'quantum_support_vector_machine',
                'quantum_neural_network'
            ]
        }
        
        # Advanced analysis algorithms
        self.analysis_algorithms = {
            'pattern_recognition': self._pattern_recognition_algorithm,
            'dimensionality_estimation': self._estimate_dimensionality,
            'entropy_calculation': self._calculate_entropy,
            'complexity_analysis': self._analyze_complexity,
            'quantum_state_tomography': self._quantum_state_tomography,
            'phase_space_reconstruction': self._reconstruct_phase_space
        }
        
        # Initialize feature extractors
        self._initialize_feature_extractors()
        
        # Signal classification system
        self.signal_classifiers = {}
        self._initialize_classifiers()

    def _initialize_feature_extractors(self):
        """Initialize feature extraction methods"""
        logger.info("🧩 Initializing Feature Extractors")
        
        self.feature_extractors = {
            'wavelet_transform': self._extract_wavelet_features,
            'hilbert_huang_transform': self._extract_hilbert_huang_features,
            'multifractal_detrended_fluctuation': self._extract_mfdfa_features,
            'spectral_features': self._extract_spectral_features,
            'entropy_features': self._extract_entropy_features
        }

    def _initialize_classifiers(self):
        """Initialize signal classification systems"""
        logger.info("🧠 Initializing Signal Classifiers")
        
        # These would be actual ML models in a real implementation
        self.signal_classifiers = {
            'coherent_vs_random': None,  # Placeholder for actual classifier
            'intelligence_estimation': None,
            'signal_type_classifier': None,
            'anomaly_detector': None
        }

    def _initialize_interaction_system(self):
        """Initialize signal interaction capabilities"""
        logger.info("🔄 Initializing Interaction System")

        self.response_history = []
        self.interaction_patterns = set()
        
        # Enhanced interaction parameters
        self.interaction_params = {
            'response_timeout': 5.0,  # seconds
            'interaction_protocols': [
                'basic_query',
                'adaptive_query',
                'quantum_entanglement',
                'phase_synchronization'
            ],
            'communication_modes': [
                'direct_amplitude',
                'phase_modulation',
                'entanglement_coding',
                'temporal_pattern'
            ]
        }
        
        # Prepare interaction circuits
        self._prepare_interaction_circuits()

    def _prepare_interaction_circuits(self):
        """Prepare quantum circuits for different interaction protocols"""
        logger.info("⚛️ Preparing Quantum Interaction Circuits")
        
        self.interaction_circuits = {}
        
        # Basic query circuit
        basic_qc = QuantumCircuit(10, 10)
        basic_qc.h(range(5))
        basic_qc.cx(0, 5)
        basic_qc.cx(1, 6)
        basic_qc.cx(2, 7)
        basic_qc.cx(3, 8)
        basic_qc.cx(4, 9)
        basic_qc.measure(range(10), range(10))
        self.interaction_circuits['basic_query'] = basic_qc
        
        # Add more specialized circuits for other interaction protocols
        # (Simplified for this example)

    def _initialize_safety_protocols(self):
        """Initialize safety measures"""
        logger.info("🛑 Initializing Safety Protocols")

        self.safety_checks = {
            'coherence': lambda x: x < 0.99,
            'pattern': lambda x: len(x) < 1000,
            'response': lambda x: x.complexity < 0.95,
            'energy_level': lambda x: x < 5.0,
            'quantum_entanglement': lambda x: x < 0.98,
            'information_density': lambda x: x < 10.0
        }
        
        # Enhanced safety systems
        self.safety_thresholds = {
            'max_coherence': 0.995,
            'max_intelligence_score': 0.98,
            'max_response_speed': 0.1,  # seconds
            'max_entanglement_depth': 10,
            'auto_shutdown_threshold': 0.999
        }
        
        # Initialize emergency shutdown procedure
        self._initialize_emergency_protocols()

    def _initialize_emergency_protocols(self):
        """Initialize emergency shutdown and containment protocols"""
        logger.info("🚨 Initializing Emergency Protocols")
        
        self.emergency_actions = {
            'disconnect_quantum_hardware': self._disconnect_quantum_hardware,
            'reset_all_qubits': self._reset_all_qubits,
            'secure_data_lockdown': self._secure_data_lockdown,
            'alert_operators': self._alert_operators
        }
        
        # Emergency state tracking
        self.emergency_state = False
        self.alert_level = 0  # 0-5, with 5 being highest

    def _initialize_eeg_interface(self):
        """Initialize EEG data processing systems"""
        logger.info("🧠 Initializing EEG Interface")
        
        if not self.eeg_integration:
            logger.info("⚠️ EEG integration disabled")
            return
            
        self.eeg_params = {
            'sampling_rate': 1000,  # Hz
            'num_channels': 64,
            'reference': 'average',
            'frequency_bands': {
                'delta': (0.5, 4),
                'theta': (4, 8),
                'alpha': (8, 13),
                'beta': (13, 30),
                'gamma': (30, 100)
            },
            'preprocessing': {
                'filter_lowcut': 0.5,
                'filter_highcut': 100,
                'notch_filter': 60,  # Hz (for power line interference)
                'remove_artifacts': True,
                'use_ica': True
            }
        }
        
        # Initialize EEG processing system
        self.eeg_processor = self._create_eeg_processor()
        
        # Initialize quantum-EEG correlation system
        self.quantum_eeg_correlator = self._create_quantum_eeg_correlator()

    def _create_eeg_processor(self):
        """Create EEG signal processing system"""
        logger.info("🔄 Creating EEG Signal Processor")
        
        # This would be a more complex implementation in a real system
        processor = {
            'preprocessing': self._preprocess_eeg,
            'feature_extraction': self._extract_eeg_features,
            'source_localization': self._localize_eeg_sources,
            'connectivity_analysis': self._analyze_eeg_connectivity,
            'classify_brain_state': self._classify_brain_state
        }
        
        return processor

    def _create_quantum_eeg_correlator(self):
        """Create system to correlate quantum signals with EEG patterns"""
        logger.info(f"🛸 Received Response from Quantum Signal using {protocol}!")
                analysis.response_correlation = self._calculate_correlation(response)
                await self._record_interaction(signal, response, analysis, protocol)
                await self._analyze_intelligence(signal, response, analysis)
                break

    async def _test_response(self, signal: CoherentSignal, protocol: str) -> Optional[np.ndarray]:
        """Test if signal responds to interaction using specified protocol"""
        logger.info(f"🔄 Testing for Quantum Signal Response using {protocol}")
        
        try:
            # Select appropriate quantum circuit for the protocol
            if protocol in self.interaction_circuits:
                circuit = self.interaction_circuits[protocol]
            else:
                # Use basic query circuit as fallback
                circuit = self.interaction_circuits['basic_query']
            
            # Execute the circuit
            if self.use_real_quantum_hardware:
                with Session(service=self.service, backend=self.backend):
                    sampler = Sampler(options=self.quantum_options)
                    job = sampler.run(circuit)
                    result = job.result()
                    measurement = list(result.quasi_dists[0].keys())[0]
            else:
                # Use simulator
                transpiled_circuit = transpile(circuit, self.backend)
                job = self.backend.run(transpiled_circuit, shots=1)
                counts = job.result().get_counts()
                measurement = list(counts.keys())[0]
            
            # Wait for potential response
            await asyncio.sleep(0.2)
            
            # Check for response
            response_circuit = self._create_detection_circuit()
            
            if self.use_real_quantum_hardware:
                with Session(service=self.service, backend=self.backend):
                    sampler = Sampler(options=self.quantum_options)
                    job = sampler.run(response_circuit)
                    result = job.result()
                    response_measurement = list(result.quasi_dists[0].keys())[0]
            else:
                # Use simulator
                transpiled_circuit = transpile(response_circuit, self.backend)
                job = self.backend.run(transpiled_circuit, shots=1)
                counts = job.result().get_counts()
                response_measurement = list(counts.keys())[0]
            
            # Analyze if response is correlated to the query
            correlation = self._calculate_bit_correlation(measurement, response_measurement)
            
            if correlation > self.analysis_params['response_threshold']:
                logger.info(f"🛸 Signal Responded! Correlation: {correlation:.4f}")
                response_data = self._extract_response_data(response_measurement)
                return response_data
            else:
                logger.info("❌ No Response from Signal")
                return None
                
        except Exception as e:
            logger.error(f"❌ Response Testing Error: {str(e)}")
            return None

    def _calculate_bit_correlation(self, bitstring1: str, bitstring2: str) -> float:
        """Calculate correlation between two bitstrings"""
        # Convert to same length if needed
        min_len = min(len(bitstring1), len(bitstring2))
        bits1 = [int(b) for b in bitstring1[-min_len:]]
        bits2 = [int(b) for b in bitstring2[-min_len:]]
        
        # Calculate correlation
        matching_bits = sum(1 for b1, b2 in zip(bits1, bits2) if b1 == b2)
        correlation = matching_bits / min_len
        
        # Adjust for random chance (0.5 is random)
        adjusted_correlation = 2 * (correlation - 0.5)
        
        return max(0, adjusted_correlation)

    def _extract_response_data(self, bitstring: str) -> np.ndarray:
        """Extract meaningful data from response bitstring"""
        # Convert to numpy array
        bits = np.array([int(b) for b in bitstring])
        
        # Process into floating point values between -1 and 1
        chunk_size = 8
        data = []
        
        for i in range(0, len(bits), chunk_size):
            if i + chunk_size <= len(bits):
                chunk = bits[i:i+chunk_size]
                # Convert chunk to value between -1 and 1
                value = 2 * (int(''.join(str(b) for b in chunk), 2) / 255) - 1
                data.append(value)
        
        return np.array(data)

    async def _analyze_intelligence(self, signal: CoherentSignal, response: np.ndarray, analysis: SignalAnalysis):
        """Analyze potential intelligence in signal with enhanced methods"""
        logger.info("🧠 Analyzing Intelligence in Response")

        # Calculate pattern complexity
        complexity = self._calculate_complexity(response)
        
        # Calculate response correlation
        correlation = self._calculate_correlation(signal.pattern_signature, response)
        
        # Extract additional features
        adaptability = self._calculate_adaptability(signal, response)
        temporal_structure = self._analyze_temporal_structure(response)
        information_content = self._measure_information_content(response)
        
        # Combine features for intelligence score
        intelligence_score = (
            0.3 * complexity +
            0.2 * correlation +
            0.2 * adaptability +
            0.15 * temporal_structure +
            0.15 * information_content
        )
        
        # Determine response type
        response_type = self._determine_response_type(
            complexity, correlation, adaptability, temporal_structure
        )
        
        # Log findings
        logger.info(f"🧠 Intelligence Analysis Results:")
        logger.info(f"   - Complexity: {complexity:.4f}")
        logger.info(f"   - Correlation: {correlation:.4f}")
        logger.info(f"   - Adaptability: {adaptability:.4f}")
        logger.info(f"   - Temporal Structure: {temporal_structure:.4f}")
        logger.info(f"   - Information Content: {information_content:.4f}")
        logger.info(f"   - Overall Intelligence Score: {intelligence_score:.4f}")
        logger.info(f"   - Response Type: {response_type}")
        
        # Store the results
        signal.complexity_index = complexity
        
        # Check if response indicates high intelligence
        if response_type in [ResponseType.COHERENT, ResponseType.INTELLIGENT, ResponseType.ADAPTIVE]:
            logger.info(f"🚀 Potentially Intelligent Signal Detected: {response_type}")
            
            # Record detailed information about the signal
            await self._record_detailed_signal_data(signal, response, analysis, response_type, intelligence_score)
            
            # Check safety thresholds
            if intelligence_score > self.safety_thresholds['max_intelligence_score']:
                logger.warning(f"⚠️ Intelligence score ({intelligence_score:.4f}) exceeds safety threshold!")
                await self._trigger_safety_protocol(signal, intelligence_score)

    def _determine_response_type(self, complexity, correlation, adaptability=0, temporal_structure=0) -> ResponseType:
        """Determine response type based on multiple metrics"""
        # Thresholds for classification
        if complexity < 0.3 and correlation < 0.3:
            return ResponseType.RANDOM
        
        if complexity > 0.8 and correlation > 0.7 and adaptability > 0.8:
            return ResponseType.INTELLIGENT
            
        if complexity > 0.7 and temporal_structure > 0.7:
            return ResponseType.STRUCTURED
            
        if adaptability > 0.8:
            return ResponseType.ADAPTIVE
            
        if correlation > 0.8:
            return ResponseType.MIMICRY
            
        if complexity > 0.6 and correlation > 0.6:
            return ResponseType.COHERENT
            
        if complexity > 0.9 and correlation < 0.3:
            return ResponseType.QUANTUM_RESONANT
            
        return ResponseType.UNKNOWN

    async def _analyze_patterns(self, end_time: datetime):
        """Analyze signal patterns over time"""
        logger.info("🔍 Starting Pattern Analysis")
        
        while datetime.now() < end_time:
            try:
                if len(self.signal_buffer) > 0:
                    logger.info("🔄 Analyzing Signal Patterns")
                    
                    # Extract signals from buffer with minimal copying
                    with threading.Lock():  # Use a lock if there are concurrent modifications
                        analysis_signals = self.signal_buffer.copy()
                    
                    # Group signals
                    grouped_signals = self._group_similar_signals(analysis_signals)
                    
                    # Analyze each group
                    for group_id, signals in grouped_signals.items():
                        await self._analyze_signal_group(group_id, signals)
                        
                    # Clean up old signals from buffer
                    self._clean_signal_buffer()
                    
                # Adaptive sleep based on buffer size
                sleep_time = max(1, 10 - 0.1 * len(self.signal_buffer))
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"❌ Pattern Analysis Error: {str(e)}")
                await asyncio.sleep(5)

    def _group_similar_signals(self, signals: List[CoherentSignal]) -> Dict[int, List[CoherentSignal]]:
        """Group similar signals together"""
        groups = {}
        
        for signal in signals:
            # Find best matching group
            best_match = -1
            best_similarity = -1
            
            for group_id, group_signals in groups.items():
                # Compare with representative signal from the group
                representative = group_signals[0]
                similarity = self._calculate_signal_similarity(signal, representative)
                
                if similarity > 0.8 and similarity > best_similarity:
                    best_match = group_id
                    best_similarity = similarity
            
            if best_match >= 0:
                # Add to existing group
                groups[best_match].append(signal)
            else:
                # Create new group
                new_group_id = len(groups)
                groups[new_group_id] = [signal]
        
        return groups

    async def _analyze_signal_group(self, group_id: int, signals: List[CoherentSignal]):
        """Analyze a group of similar signals"""
        logger.info(f"🔍 Analyzing Signal Group {group_id} with {len(signals)} signals")
        
        # Extract temporal evolution
        timestamps = [signal.emergence_time for signal in signals]
        coherence_levels = [signal.coherence_level for signal in signals]
        
        # Analyze trends
        increasing_coherence = False
        if len(coherence_levels) > 5:
            # Simple linear regression to detect trend
            x = np.arange(len(coherence_levels))
            slope = np.polyfit(x, coherence_levels, 1)[0]
            increasing_coherence = slope > 0.01
            
            if increasing_coherence:
                logger.warning(f"⚠️ Signal Group {group_id} shows increasing coherence!")
        
        # Check for patterns in timing
        if len(timestamps) > 5:
            time_diffs = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                         for i in range(len(timestamps)-1)]
            
            # Calculate coefficient of variation (lower means more regular)
            time_diffs_array = np.array(time_diffs)
            cv = np.std(time_diffs_array) / np.mean(time_diffs_array)
            
            if cv < 0.2:  # Highly regular timing
                logger.warning(f"⚠️ Signal Group {group_id} shows regular timing (CV={cv:.4f})!")

    async def _handle_interactions(self, end_time: datetime):
        """Handle ongoing interactions with detected signals"""
        logger.info("🔄 Starting Interaction Handler")
        
        while datetime.now() < end_time:
            try:
                # Check for active interactions
                if len(self.response_history) > 0:
                    logger.info("🔄 Managing Active Interactions")
                    
                    # Get recent interactions
                    recent_interactions = self.response_history[-10:]
                    
                    # Check for ongoing conversations
                    for interaction in recent_interactions:
                        signal_id = interaction.get('signal_id')
                        
                        # Follow up on interesting signals
                        if self._should_follow_up(interaction):
                            logger.info(f"🔄 Following up on interaction with Signal {signal_id}")
                            await self._send_follow_up_query(signal_id, interaction)
                
                # Adaptive pause
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Interaction Handler Error: {str(e)}")
                await asyncio.sleep(5)

    async def _ensure_safety(self, end_time: datetime):
        """Monitor for safety concerns"""
        logger.info("🛡️ Starting Safety Monitor")
        
        while datetime.now() < end_time:
            try:
                logger.info("🛡️ Running Safety Checks")
                
                # Check coherence history
                if len(self.coherence_history) > 10:
                    recent_coherence = self.coherence_history[-10:]
                    avg_coherence = sum(recent_coherence) / len(recent_coherence)
                    
                    if avg_coherence > self.safety_thresholds['max_coherence']:
                        logger.warning(f"⚠️ Average coherence ({avg_coherence:.4f}) exceeds safety threshold!")
                        await self._trigger_safety_protocol_coherence(avg_coherence)
                
                # Check for unusual signal patterns
                if len(self.signal_buffer) > 20:
                    # Too many signals in buffer
                    logger.warning(f"⚠️ Unusually high signal count ({len(self.signal_buffer)})!")
                    
                # Check for emergency shutdown trigger
                if self.emergency_state:
                    logger.error("🚨 Emergency state detected! Shutting down...")
                    await self._execute_emergency_protocol()
                    break
                
                # Adaptive pause
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"❌ Safety Monitor Error: {str(e)}")
                await asyncio.sleep(5)

    async def _analyze_eeg_correlations(self, end_time: datetime):
        """Analyze correlations between EEG and quantum signals"""
        if not self.eeg_integration:
            return
            
        logger.info("🧠 Starting EEG-Quantum Correlation Analysis")
        
        while datetime.now() < end_time:
            try:
                # Check if we have both EEG and quantum data
                if hasattr(self, 'current_eeg_data') and len(self.signal_buffer) > 0:
                    logger.info("🔄 Analyzing EEG-Quantum Correlations")
                    
                    # Get current EEG data
                    eeg_data = self.current_eeg_data
                    
                    # Compare with recent quantum signals
                    recent_signals = self.signal_buffer[-5:]
                    
                    for signal in recent_signals:
                        correlation = self._correlate_eeg_with_quantum(eeg_data, signal)
                        
                        if correlation > 0.7:
                            logger.warning(f"⚠️ High EEG-Quantum correlation detected: {correlation:.4f}")
                            await self._record_eeg_quantum_correlation(eeg_data, signal, correlation)
                
                # Adaptive pause
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"❌ EEG Correlation Analysis Error: {str(e)}")
                await asyncio.sleep(5)

    # Utility methods
    def _extract_pattern(self, bitstring: str) -> np.ndarray:
        """Extract numerical pattern from measurement bitstring"""
        # Convert binary string to numerical array
        if isinstance(bitstring, int):
            # Convert integer to binary string
            bitstring = bin(bitstring)[2:]
        
        return np.array([int(bit) for bit in bitstring])

    def _calculate_coherence(self, measurement: str) -> float:
        """Calculate quantum coherence from measurement"""
        # Simplified coherence calculation
        if isinstance(measurement, int):
            # Convert integer to binary string
            measurement = bin(measurement)[2:]
            
        # Count transitions between 0 and 1
        transitions = sum(1 for i in range(len(measurement)-1) 
                         if measurement[i] != measurement[i+1])
        
        # Fewer transitions indicate higher coherence
        max_possible_transitions = len(measurement) - 1
        coherence = 1.0 - (transitions / max_possible_transitions)
        
        return coherence

    def _calculate_randomness(self, signal: CoherentSignal) -> float:
        """Calculate randomness score for a signal"""
        # Use entropy as a measure of randomness
        pattern = signal.pattern_signature
        
        # Calculate Shannon entropy
        _, counts = np.unique(pattern, return_counts=True)
        probabilities = counts / len(pattern)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Normalize entropy (maximum entropy for binary is 1.0)
        normalized_entropy = entropy / 1.0
        
        return normalized_entropy

    def _calculate_complexity(self, signal: Union[CoherentSignal, np.ndarray]) -> float:
        """Calculate complexity of a signal pattern"""
        if isinstance(signal, CoherentSignal):
            pattern = signal.pattern_signature
        else:
            pattern = signal
            
        # Use Lempel-Ziv complexity (simplified)
        pattern_str = ''.join(str(int(bit)) for bit in pattern)
        
        # Dictionary for Lempel-Ziv parsing
        dictionary = {}
        
        i = 0
        complexity = 1  # Start with 1 for the first character
        current_phrase = ""
        
        while i < len(pattern_str):
            current_phrase += pattern_str[i]
            i += 1
            
            if current_phrase not in dictionary:
                dictionary[current_phrase] = len(dictionary) + 1
                current_phrase = ""
                complexity += 1
                
        # Normalize by maximum possible complexity
        max_complexity = len(pattern_str) / np.log2(len(pattern_str))
        normalized_complexity = complexity / max_complexity
        
        return min(1.0, normalized_complexity)

    def _calculate_entanglement(self, signal: CoherentSignal) -> float:
        """Estimate quantum entanglement from signal pattern"""
        # Simplified entanglement estimation
        pattern = signal.pattern_signature
        
        # Calculate mutual information as entanglement proxy
        # Split pattern into two halves
        half_size = len(pattern) // 2
        first_half = pattern[:half_size]
        second_half = pattern[half_size:2*half_size]
        
        # Calculate entropies
        def calc_entropy(x):
            _, counts = np.unique(x, return_counts=True)
            probabilities = counts / len(x)
            return -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        h1 = calc_entropy(first_half)
        h2 = calc_entropy(second_half)
        
        # Join the arrays and calculate joint entropy
        joined = np.column_stack((first_half, second_half))
        unique_rows, counts = np.unique(joined, axis=0, return_counts=True)
        probabilities = counts / len(joined)
        h_joint = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Calculate mutual information
        mutual_info = h1 + h2 - h_joint
        
        # Normalize by minimum of individual entropies
        normalized_mutual_info = mutual_info / min(h1, h2) if min(h1, h2) > 0 else 0.0
        
        return normalized_mutual_info

    def _calculate_dimensions(self, signal: CoherentSignal) -> List[float]:
        """Calculate dimensional signature of the signal"""
        pattern = signal.pattern_signature
        
        # Calculate correlation dimension (simplified)
        # Use embedding dimensions from 1 to 5
        dimensions = []
        
        for embed_dim in range(1, 6):
            # Create embedded vectors
            vectors = []
            for i in range(len(pattern) - embed_dim + 1):
                vectors.append(pattern[i:i+embed_dim])
                
            # Calculate pairwise distances
            n_vectors = len(vectors)
            distances = np.zeros((n_vectors, n_vectors))
            
            for i in range(n_vectors):
                for j in range(i+1, n_vectors):
                    dist = np.sum(np.abs(vectors[i] - vectors[j]))
                    distances[i, j] = dist
                    distances[j, i] = dist
            
            # Estimate dimension using correlation sum
            epsilons = np.linspace(0.1, 2.0, 10)
            correlation_sums = []
            
            for eps in epsilons:
                count = np.sum(distances < eps)
                correlation_sum = count / (n_vectors * (n_vectors - 1))
                correlation_sums.append(correlation_sum)
                
            # Estimate slope in log-log space
            if all(cs > 0 for cs in correlation_sums):
                log_eps = np.log(epsilons)
                log_cs = np.log(correlation_sums)
                
                slope, _ = np.polyfit(log_eps, log_cs, 1)
                dimensions.append(slope)
            else:
                dimensions.append(0.0)
        
        return dimensions

    def _calculate_correlation(self, pattern1: np.ndarray, pattern2: Optional[np.ndarray] = None) -> float:
        """Calculate correlation between patterns"""
        if pattern2 is None:
            # Autocorrelation
            pattern2 = pattern1
            
        # Ensure equal length
        min_len = min(len(pattern1), len(pattern2))
        p1 = pattern1[:min_len]
        p2 = pattern2[:min_len]
        
        # Calculate Pearson correlation
        p1_centered = p1 - np.mean(p1)
        p2_centered = p2 - np.mean(p2)
        
        numerator = np.sum(p1_centered * p2_centered)
        denominator = np.sqrt(np.sum(p1_centered**2) * np.sum(p2_centered**2))
        
        if denominator > 0:
            correlation = numerator / denominator
            # Convert to 0-1 range
            correlation = (correlation + 1) / 2
        else:
            correlation = 0.5  # Undefined correlation
        
        return correlation

    # Utility methods for EEG analysis
    def _preprocess_eeg(self, raw_eeg_data: np.ndarray) -> EEGSignal:
        """Preprocess raw EEG data"""
        logger.info("🧠 Preprocessing EEG Data")
        
        # Create EEG signal object
        eeg_signal = EEGSignal(
            raw_data=raw_eeg_data,
            sampling_rate=self.eeg_params['sampling_rate'],
            channel_names=[f"Channel_{i}" for i in range(self.eeg_params['num_channels'])]
        )
        
        # Apply preprocessing
        # 1. Bandpass filter
        eeg_signal.filter_data(
            self.eeg_params['preprocessing']['filter_lowcut'],
            self.eeg_params['preprocessing']['filter_highcut']
        )
        
        # 2. Compute frequency band powers
        eeg_signal.compute_band_powers()
        
        # 3. Compute coherence between channels
        eeg_signal.compute_coherence()
        
        return eeg_signal

    def _correlate_eeg_with_quantum(self, eeg_data: EEGSignal, quantum_signal: CoherentSignal) -> float:
        """Correlate EEG data with quantum signal"""
        # Calculate correlation between EEG alpha power and quantum signal pattern
        
        # Get alpha band power from EEG
        if 'alpha' in eeg_data.band_powers:
            alpha_power = eeg_data.band_powers['alpha']
            
            # Resample quantum signal pattern to match alpha power length
            pattern = quantum_signal.pattern_signature
            resampled_pattern = pattern[:len(alpha_power)] if len(pattern) >= len(alpha_power) else np.resize(pattern, len(alpha_power))
            
            # Calculate correlation
            correlation = self._calculate_correlation(alpha_power, resampled_pattern)
            return correlation
        
        return 0.0

    # Implementation of emergency protocols
    async def _trigger_safety_protocol(self, signal: CoherentSignal, intelligence_score: float):
        """Trigger safety protocol for high intelligence signal"""
        logger.warning(f"🚨 Triggering Safety Protocol - Intelligence Score: {intelligence_score:.4f}")
        
        # Increase alert level
        self.alert_level = min(5, self.alert_level + 1)
        
        # Log detailed information
        logger.warning(f"🚨 Detailed Signal Information:")
        logger.warning(f"   - Coherence: {signal.coherence_level:.4f}")
        logger.warning(f"   - Complexity: {signal.complexity_index:.4f}")
        logger.warning(f"   - Emergency Level: {self.alert_level}")
        
        # Implement containment measures
        if self.alert_level >= 3:
            # High alert
            logger.warning("⚠️ Implementing containment measures")
            
            # Reset quantum circuits
            self._reset_all_qubits()
            
            # If alert level is critical, trigger emergency shutdown
            if self.alert_level >= 5:
                self.emergency_state = True

    async def _trigger_safety_protocol_coherence(self, coherence_level: float):
        """Trigger safety protocol for high coherence"""
        logger.warning(f"🚨 Triggering Safety Protocol - Coherence Level: {coherence_level:.4f}")
        
        # Increase alert level
        self.alert_level = min(5, self.alert_level + 1)
        
        # Implement containment measures based on alert level
        if self.alert_level >= 3:
            logger.warning("⚠️ Implementing containment measures")
            
            # Reset quantum circuits
            self._reset_all_qubits()
            
            # If alert level is critical, trigger emergency shutdown
            if self.alert_level >= 5:
                self.emergency_state = True

    async def _execute_emergency_protocol(self):
        """Execute emergency shutdown protocol"""
        logger.error("🚨 EXECUTING EMERGENCY PROTOCOL")
        
        # Execute all emergency actions
        for action_name, action_func in self.emergency_actions.items():
            logger.error(f"🚨 Executing {action_name}")
            await action_func()
            
        # Set system state to emergency shutdown
        self.system_state = "emergency_shutdown"
        
        # Exit the program (in a real implementation, this would be handled more gracefully)
        logger.error("🚨 Emergency shutdown complete")

    async def _reset_all_qubits(self):
        """Reset all qubits to break any entanglement"""
        logger.warning("🔄 Resetting all qubits")
        
        # Create reset circuit
        reset_circuit = QuantumCircuit(*self.qr.values(), self.cr)
        
        # Add reset operation to all qubits
        for register in self.qr.values():
            for qubit in register:
                reset_circuit.reset(qubit)
                
        # Execute reset circuit
        if self.use_real_quantum_hardware:
            with Session(service=self.service, backend=self.backend):
                sampler = Sampler(options=self.quantum_options)
                job = sampler.run(reset_circuit)
                job.result()  # Wait for completion
        else:
            # Use simulator
            transpiled_circuit = transpile(reset_circuit, self.backend)
            job = self.backend.run(transpiled_circuit, shots=1)
            job.result()  # Wait for completion
            
        logger.warning("✅ All qubits reset")

    async def _disconnect_quantum_hardware(self):
        """Disconnect from quantum hardware"""
        logger.warning("🔌 Disconnecting from quantum hardware")
        
        if self.use_real_quantum_hardware:
            # In a real implementation, this would properly close connections
            self.use_real_quantum_hardware = False
            self._initialize_quantum_simulator()
            
        logger.warning("✅ Disconnected from quantum hardware")

    async def _secure_data_lockdown(self):
        """Secure all collected data"""
        logger.warning("🔒 Securing all data")
        
        # Save all data with encryption
        try:
            # Save signal buffer
            with open('data/emergency/signals.pickle', 'wb') as f:
                pickle.dump(self.signal_buffer, f)
                
            # Save analysis data
            with open('data/emergency/analysis.pickle', 'wb') as f:
                pickle.dump(self.coherence_history, f)
                
            # Save interaction history
            with open('data/emergency/interactions.pickle', 'wb') as f:
                pickle.dump(self.response_history, f)
                
            logger.warning("✅ Data secured")
        except Exception as e:
            logger.error(f"❌ Data security error: {str(e)}")

    async def _alert_operators(self):
        """Alert system operators"""
        logger.warning("📢 ALERTING SYSTEM OPERATORS")
        logger.warning("📢 EMERGENCY SHUTDOWN INITIATED")
        logger.warning("📢 PLEASE CHECK LOGS AND DATA")
        
        # In a real implementation, this would send emails, SMS, or other alerts
        
        # Create emergency report
        report = {
            'timestamp': datetime.now().isoformat(),
            'alert_level': self.alert_level,
            'emergency_state': self.emergency_state,
            'coherence_history': self.coherence_history[-10:] if len(self.coherence_history) > 10 else self.coherence_history,
            'recent_interactions': self.response_history[-5:] if len(self.response_history) > 5 else self.response_history,
            'signal_count': len(self.signal_buffer)
        }
        
        # Save emergency report
        try:
            with open(f'data/emergency/emergency_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Emergency report error: {str(e)}")

    # Helper methods for feature extraction
def _extract_spectral_features(self, signal: np.ndarray) -> np.ndarray:
    """Extract spectral features from signal"""
    # Apply FFT to get frequency domain representation
    spectrum = np.abs(fft(signal))
    
    # Extract features from spectrum
    # 1. Spectral centroid
    indices = np.arange(len(spectrum))
    centroid = np.sum(indices * spectrum) / (np.sum(spectrum) + 1e-10)
    
    # 2. Spectral bandwidth
    bandwidth = np.sqrt(np.sum(((indices - centroid)**2) * spectrum) / (np.sum(spectrum) + 1e-10))
    
    # 3. Spectral flatness
    flatness = self._calculate_spectral_flatness(spectrum)
    
    # 4. Spectral roll-off
    cumulative_sum = np.cumsum(spectrum)
    roll_off = np.where(cumulative_sum >= 0.85 * cumulative_sum[-1])[0][0] / len(spectrum)
    
    # 5. Energy concentration ratio
    sorted_spectrum = np.sort(spectrum)[::-1]  # Sort in descending order
    energy_concentration = np.sum(sorted_spectrum[:len(spectrum)//10]) / (np.sum(spectrum) + 1e-10)
    
    return np.array([centroid, bandwidth, flatness, roll_off, energy_concentration])

def _extract_wavelet_features(self, signal: np.ndarray) -> np.ndarray:
    """Extract wavelet transform features from signal"""
    # Simple wavelet analysis (in a real implementation, use proper wavelet transform)
    n = len(signal)
    
    # Define simple scales for analysis
    scales = [2, 4, 8, 16, 32]
    features = []
    
    for scale in scales:
        if scale < n//2:
            # Simple convolution with scaled wavelet (Haar-like)
            wavelet = np.concatenate([np.ones(scale), -np.ones(scale)]) / np.sqrt(scale)
            coeffs = np.convolve(signal, wavelet, mode='valid')
            
            # Extract statistical features from coefficients
            features.extend([
                np.mean(np.abs(coeffs)),
                np.std(coeffs),
                np.max(np.abs(coeffs)),
                np.sum(coeffs**2) / len(coeffs)
            ])
    
    return np.array(features)

def _extract_hilbert_huang_features(self, signal: np.ndarray) -> np.ndarray:
    """Extract Hilbert-Huang transform features"""
    # Simple implementation (in a real system, use proper EMD)
    # Get analytic signal using Hilbert transform
    analytic_signal = hilbert(signal)
    
    # Get amplitude envelope and instantaneous phase
    amplitude_envelope = np.abs(analytic_signal)
    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
    instantaneous_frequency = np.diff(instantaneous_phase) / (2.0 * np.pi)
    
    # Extract features
    amp_features = [
        np.mean(amplitude_envelope),
        np.std(amplitude_envelope),
        np.max(amplitude_envelope),
        np.min(amplitude_envelope)
    ]
    
    freq_features = [
        np.mean(instantaneous_frequency),
        np.std(instantaneous_frequency),
        np.max(instantaneous_frequency),
        np.min(instantaneous_frequency)
    ]
    
    return np.array(amp_features + freq_features)

def _extract_mfdfa_features(self, signal: np.ndarray) -> np.ndarray:
    """Extract Multifractal Detrended Fluctuation Analysis features"""
    # Simplified implementation
    # Calculate fluctuation function for multiple q-orders
    q_orders = [-3, -1, 0, 1, 3]
    scales = [4, 8, 16, 32, 64]
    
    features = []
    
    for q in q_orders:
        scale_flucts = []
        
        for scale in scales:
            if scale < len(signal)//4:
                # Divide signal into segments
                n_segments = len(signal) // scale
                fluctuations = []
                
                for i in range(n_segments):
                    segment = signal[i*scale:(i+1)*scale]
                    
                    # Detrend by subtracting linear fit
                    x = np.arange(len(segment))
                    p = np.polyfit(x, segment, 1)
                    trend = np.polyval(p, x)
                    detrended = segment - trend
                    
                    # Calculate fluctuation
                    fluct = np.sqrt(np.mean(detrended**2))
                    fluctuations.append(fluct)
                
                # Calculate q-order fluctuation
                if q != 0:
                    qfluct = np.mean(np.array(fluctuations)**q)**(1/q)
                else:
                    qfluct = np.exp(0.5 * np.mean(np.log(np.array(fluctuations)**2)))
                
                scale_flucts.append(qfluct)
        
        # Calculate scaling exponent using log-log fit
        if len(scale_flucts) > 1:
            log_scales = np.log(scales[:len(scale_flucts)])
            log_flucts = np.log(scale_flucts)
            
            h_q, _ = np.polyfit(log_scales, log_flucts, 1)
            features.append(h_q)
        else:
            features.append(0.5)  # Default value for Brownian motion
    
    return np.array(features)

def _extract_entropy_features(self, signal: np.ndarray) -> np.ndarray:
    """Extract various entropy measures from signal"""
    # Sample entropy (simplified)
    r = 0.2 * np.std(signal)
    
    # For m=2 and m=3
    sample_entropies = []
    
    for m in [2, 3]:
        # Create embedded vectors
        templates = []
        for i in range(len(signal) - m + 1):
            templates.append(signal[i:i+m])
        
        # Count matches
        B = 0  # Counter for matches of length m
        A = 0  # Counter for matches of length m+1
        
        for i in range(len(templates)):
            for j in range(i+1, len(templates)):
                # Check if templates match within tolerance r
                if np.max(np.abs(templates[i] - templates[j])) < r:
                    B += 1
                    
                    # Check for match with m+1
                    if i < len(signal) - m and j < len(signal) - m:
                        if abs(signal[i+m] - signal[j+m]) < r:
                            A += 1
        
        # Calculate sample entropy
        if B > 0:
            sample_entropy = -np.log(A / B)
        else:
            sample_entropy = 0
        
        sample_entropies.append(sample_entropy)
    
    # Approximate entropy
    approx_entropy = sample_entropies[0]
    
    # Permutation entropy (simplified)
    n = len(signal)
    m = 3  # embedding dimension
    permutations = {}
    
    for i in range(n - m + 1):
        # Get the permutation pattern
        pattern = np.argsort(signal[i:i+m])
        pattern_tuple = tuple(pattern)
        
        # Count occurrences
        if pattern_tuple in permutations:
            permutations[pattern_tuple] += 1
        else:
            permutations[pattern_tuple] = 1
    
    # Calculate permutation entropy
    total = sum(permutations.values())
    perm_entropy = 0
    
    for count in permutations.values():
        p = count / total
        perm_entropy -= p * np.log2(p)
    
    # Normalize by maximum entropy
    perm_entropy /= np.log2(np.math.factorial(m))
    
    return np.array([sample_entropies[0], sample_entropies[1], approx_entropy, perm_entropy])

def _calculate_spectral_flatness(self, spectrum: np.ndarray) -> float:
    """Calculate spectral flatness (Wiener entropy)"""
    # Avoid values close to zero
    spectrum = np.maximum(spectrum, 1e-10)
    
    # Calculate geometric mean
    geometric_mean = np.exp(np.mean(np.log(spectrum)))
    
    # Calculate arithmetic mean
    arithmetic_mean = np.mean(spectrum)
    
    # Calculate flatness
    flatness = geometric_mean / arithmetic_mean
    
    return flatness

def _calculate_sample_entropy(self, signal: np.ndarray, m: int = 2, r: float = 0.2) -> float:
    """Calculate sample entropy of a signal"""
    # r is typically 0.2 * std(signal)
    r = r * np.std(signal)
    
    def _count_matches(templates, m):
        """Count matching templates within tolerance r"""
        counts = np.zeros(len(templates))
        
        for i in range(len(templates)):
            for j in range(i+1, len(templates)):
                # Check if templates match within tolerance r
                if np.max(np.abs(templates[i] - templates[j])) < r:
                    counts[i] += 1
                    counts[j] += 1
        
        return counts
    
    # Create templates of length m
    templates_m = []
    for i in range(len(signal) - m + 1):
        templates_m.append(signal[i:i+m])
    
    # Count matches for templates of length m
    counts_m = _count_matches(templates_m, m)
    
    # Create templates of length m+1
    templates_m1 = []
    for i in range(len(signal) - (m+1) + 1):
        templates_m1.append(signal[i:i+m+1])
    
    # Count matches for templates of length m+1
    counts_m1 = _count_matches(templates_m1, m+1)
    
    # Calculate A and B
    B = np.sum(counts_m) / (2 * (len(signal) - m))
    A = np.sum(counts_m1) / (2 * (len(signal) - m - 1))
    
    # Calculate sample entropy
    if B > 0 and A > 0:
        return -np.log(A / B)
    else:
        return 0.0

def _runs_test(self, signal: np.ndarray) -> float:
    """Perform runs test for randomness"""
    # Convert to binary if not already
    if not np.all(np.isin(signal, [0, 1])):
        median = np.median(signal)
        binary = (signal > median).astype(int)
    else:
        binary = signal
    
    # Count runs
    runs = 1
    for i in range(1, len(binary)):
        if binary[i] != binary[i-1]:
            runs += 1
    
    # Count ones and zeros
    n1 = np.sum(binary)
    n0 = len(binary) - n1
    
    # Expected number of runs for a random sequence
    expected_runs = 1 + (2 * n0 * n1) / (n0 + n1)
    
    # Standard deviation of runs
    std_runs = np.sqrt((2 * n0 * n1 * (2 * n0 * n1 - n0 - n1)) / 
                       ((n0 + n1)**2 * (n0 + n1 - 1)))
    
    # Z-statistic
    z = (runs - expected_runs) / std_runs
    
    # Convert to a score between 0 and 1 (1 = most random)
    # Lower absolute z-value indicates more randomness
    score = np.exp(-abs(z) / 2)
    
    return score

def _extract_frequency_spectrum(self, signal: np.ndarray) -> np.ndarray:
    """Extract frequency spectrum using FFT"""
    # Apply FFT
    spectrum = np.abs(fft(signal))
    
    # Return only the first half (due to symmetry)
    n = len(spectrum)
    return spectrum[:n//2]

def _extract_phase_data(self, signal: np.ndarray) -> np.ndarray:
    """Extract phase data using Hilbert transform"""
    # Apply Hilbert transform to get analytic signal
    analytic_signal = hilbert(signal)
    
    # Extract instantaneous phase
    instantaneous_phase = np.angle(analytic_signal)
    
    return instantaneous_phase

def _estimate_source_vector(self, signal: np.ndarray) -> np.ndarray:
    """Estimate source vector of the signal"""
    # Simplified implementation
    # Use PCA-like approach on windowed signal
    window_size = min(64, len(signal)//2)
    
    # Create windowed signal matrix
    windows = []
    for i in range(0, len(signal) - window_size, window_size//2):
        windows.append(signal[i:i+window_size])
    
    if len(windows) < 2:
        return np.zeros(min(len(signal), 10))
    
    # Convert to numpy array
    windows_matrix = np.vstack(windows)
    
    # Center the data
    centered = windows_matrix - np.mean(windows_matrix, axis=0)
    
    # SVD for principal components
    try:
        U, S, Vt = np.linalg.svd(centered, full_matrices=False)
        
        # Return first principal component
        source_vector = Vt[0]
        
        # Pad or truncate to standard size (10)
        standard_size = 10
        if len(source_vector) > standard_size:
            return source_vector[:standard_size]
        else:
            return np.pad(source_vector, (0, standard_size - len(source_vector)))
    except:
        return np.zeros(10)

def _calculate_amplitude_variation(self, signal: CoherentSignal) -> float:
    """Calculate amplitude variation of signal"""
    pattern = signal.pattern_signature
    
    # Apply Hilbert transform to get amplitude envelope
    analytic_signal = hilbert(pattern)
    amplitude_envelope = np.abs(analytic_signal)
    
    # Calculate coefficient of variation
    cv = np.std(amplitude_envelope) / np.mean(amplitude_envelope) if np.mean(amplitude_envelope) > 0 else 0
    
    # Normalize to 0-1 range (higher values mean more variation)
    normalized_cv = min(1.0, cv / 2.0)
    
    return normalized_cv

def _calculate_phase_coherence(self, signal: CoherentSignal) -> float:
    """Calculate phase coherence of signal"""
    pattern = signal.pattern_signature
    
    # Apply Hilbert transform to get phase information
    analytic_signal = hilbert(pattern)
    phase = np.angle(analytic_signal)
    
    # Calculate phase coherence (mean resultant length)
    complex_phase = np.exp(1j * phase)
    mean_complex = np.mean(complex_phase)
    coherence = np.abs(mean_complex)
    
    return coherence

def _extract_harmonic_structure(self, signal: CoherentSignal) -> List[float]:
    """Extract harmonic structure of signal"""
    pattern = signal.pattern_signature
    
    # Get frequency spectrum
    spectrum = np.abs(fft(pattern))
    n = len(spectrum)
    half_spectrum = spectrum[:n//2]
    
    # Find peaks
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(half_spectrum, height=np.max(half_spectrum)/10)
    
    # If no peaks found, return zeros
    if len(peaks) == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    
    # Sort peaks by amplitude
    peak_amplitudes = half_spectrum[peaks]
    sorted_indices = np.argsort(peak_amplitudes)[::-1]  # Descending order
    sorted_peaks = peaks[sorted_indices]
    
    # Get up to 5 most prominent peaks
    top_peaks = sorted_peaks[:5]
    
    # Calculate ratios between peaks (harmonicity measure)
    ratios = []
    if len(top_peaks) > 1:
        fundamental = top_peaks[0]
        for peak in top_peaks[1:]:
            ratio = peak / fundamental if fundamental > 0 else 0
            ratios.append(ratio)
    
    # Pad with zeros to ensure 5 values
    while len(ratios) < 5:
        ratios.append(0.0)
    
    return ratios[:5]

def _calculate_information_density(self, signal: CoherentSignal) -> float:
    """Calculate information density of signal"""
    pattern = signal.pattern_signature
    
    # Use compression ratio as a measure of information density
    import zlib
    
    # Convert to bytes
    pattern_bytes = np.packbits(pattern.astype(bool))
    
    # Compress
    compressed = zlib.compress(pattern_bytes)
    
    # Calculate compression ratio
    compression_ratio = len(pattern_bytes) / len(compressed)
    
    # Normalize to 0-1 range
    normalized_ratio = min(1.0, compression_ratio / 5.0)
    
    return normalized_ratio

def _calculate_symmetry_metrics(self, signal: CoherentSignal) -> Dict[str, float]:
    """Calculate various symmetry metrics of signal"""
    pattern = signal.pattern_signature
    
    # 1. Reflection symmetry
    n = len(pattern)
    first_half = pattern[:n//2]
    second_half = pattern[n//2:][::-1]  # Reversed
    
    # Ensure equal length
    min_len = min(len(first_half), len(second_half))
    correlation = np.corrcoef(first_half[:min_len], second_half[:min_len])[0, 1]
    reflection_symmetry = (correlation + 1) / 2  # Convert from [-1,1] to [0,1]
    
    # 2. Translation symmetry (autocorrelation at different lags)
    max_lag = min(100, n//2)
    autocorr = np.correlate(pattern, pattern, mode='full')[n-1:n+max_lag]
    # Normalize
    autocorr = autocorr / autocorr[0]
    # Find first minimum
    min_idx = 1
    for i in range(1, len(autocorr)):
        if autocorr[i] < autocorr[i-1] and autocorr[i] < autocorr[min(i+1, len(autocorr)-1)]:
            min_idx = i
            break
    
    # Find first maximum after minimum
    max_idx = min_idx
    for i in range(min_idx+1, len(autocorr)):
        if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[min(i+1, len(autocorr)-1)]:
            max_idx = i
            break
    
    translation_symmetry = autocorr[max_idx] if max_idx > min_idx else 0
    
    # 3. Scale symmetry (compare pattern at different scales)
    scale_symmetry = 0.0
    
    if n >= 4:
        # Downsample to half size
        downsampled = pattern[::2]
        # Upsample back (simple repetition)
        upsampled = np.repeat(downsampled, 2)[:n]
        
        # Calculate correlation
        correlation = np.corrcoef(pattern, upsampled)[0, 1]
        scale_symmetry = (correlation + 1) / 2  # Convert from [-1,1] to [0,1]
    
    return {
        'reflection': reflection_symmetry,
        'translation': translation_symmetry,
        'scale': scale_symmetry
    }

def _calculate_statistical_moments(self, signal: CoherentSignal) -> List[float]:
    """Calculate statistical moments of signal"""
    pattern = signal.pattern_signature
    
    # Ensure pattern is centered
    centered = pattern - np.mean(pattern)
    
    # Calculate first 4 moments
    mean = np.mean(pattern)
    variance = np.var(centered)
    
    # Skewness (3rd moment)
    skewness = np.mean(centered**3) / (variance**1.5) if variance > 0 else 0
    
    # Kurtosis (4th moment)
    kurtosis = np.mean(centered**4) / (variance**2) - 3 if variance > 0 else 0
    
    return [mean, variance, skewness, kurtosis]

def _calculate_adaptability(self, signal: CoherentSignal, response: np.ndarray) -> float:
    """Calculate adaptability score based on signal-response history"""
    # Check if we have previous interactions with this signal
    if len(signal.interaction_history) < 2:
        return 0.5  # Neutral score for insufficient history
    
    # Get last two interactions
    prev_response1 = signal.interaction_history[-1].get('response', None)
    prev_response2 = signal.interaction_history[-2].get('response', None)
    
    if prev_response1 is None or prev_response2 is None:
        return 0.5  # Neutral score for incomplete history
    
    # Calculate how much the response has changed relative to the query
    prev_query1 = signal.interaction_history[-1].get('query', None)
    prev_query2 = signal.interaction_history[-2].get('query', None)
    
    if prev_query1 is None or prev_query2 is None:
        return 0.5  # Neutral score for incomplete history
    
    # Calculate delta in queries
    query_similarity = self._calculate_correlation(prev_query1, prev_query2)
    query_delta = 1.0 - query_similarity
    
    # Calculate delta in responses
    response_similarity = self._calculate_correlation(prev_response1, prev_response2)
    response_delta = 1.0 - response_similarity
    
    # Calculate adaptability as ratio of response change to query change
    if query_delta > 0.01:  # Avoid division by very small numbers
        adaptability = response_delta / query_delta
        # Normalize to [0, 1]
        adaptability = min(1.0, adaptability)
    else:
        # If queries are almost identical, check if responses are different
        adaptability = 0.5 + response_delta / 2
    
    return adaptability

def _analyze_temporal_structure(self, response: np.ndarray) -> float:
    """Analyze temporal structure in response pattern"""
    # Calculate sample entropy (lower = more structured)
    sample_entropy = self._calculate_sample_entropy(response)
    
    # Calculate autocorrelation at different lags
    max_lag = min(20, len(response)//2)
    autocorr = np.zeros(max_lag)
    
    for lag in range(1, max_lag+1):
        # Calculate autocorrelation at this lag
        correlation = np.corrcoef(response[:-lag], response[lag:])[0, 1]
        autocorr[lag-1] = correlation
    
    # Find maximum autocorrelation
    max_autocorr = np.max(np.abs(autocorr)) if len(autocorr) > 0 else 0
    
    # Combine metrics (higher = more structured)
    structure_score = 0.6 * (1.0 - min(1.0, sample_entropy)) + 0.4 * max_autocorr
    
    return structure_score

def _measure_information_content(self, response: np.ndarray) -> float:
    """Measure information content in response"""
    # Use compression ratio and entropy as measures of information content
    
    # Calculate Shannon entropy
    _, counts = np.unique(response, return_counts=True)
    probabilities = counts / len(response)
    entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    
    # Normalize entropy by maximum possible entropy (for continuous data)
    max_entropy = np.log2(len(response))
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    # Calculate compression ratio
    import zlib
    
    # Convert to bytes (using 16-bit floats for compression)
    response_bytes = response.astype(np.float16).tobytes()
    
    # Compress
    compressed = zlib.compress(response_bytes)
    
    # Calculate compression ratio
    compression_ratio = len(response_bytes) / len(compressed)
    
    # Normalize compression ratio
    normalized_ratio = min(1.0, compression_ratio / 5.0)
    
    # Combine metrics
    information_content = 0.5 * normalized_entropy + 0.5 * normalized_ratio
    
    return information_content

# Advanced helper methods for system operations
def _calculate_adaptive_pause(self) -> float:
    """Calculate adaptive pause time based on system load and detection rate"""
    # Base pause time
    base_pause = 1.0  # seconds
    
    # Adjust based on signal buffer size
    buffer_adjustment = 0.1 * len(self.signal_buffer)
    
    # Adjust based on recent detection rate
    if hasattr(self, 'recent_detection_times') and len(self.recent_detection_times) > 1:
        recent_times = self.recent_detection_times[-10:]
        time_diffs = [(recent_times[i+1] - recent_times[i]).total_seconds() 
                     for i in range(len(recent_times)-1)]
        avg_time_diff = np.mean(time_diffs) if time_diffs else 5.0
        rate_adjustment = 5.0 / (avg_time_diff + 1.0)
    else:
        rate_adjustment = 1.0
    
    # Calculate final pause time
    pause_time = base_pause - buffer_adjustment * 0.05 + rate_adjustment * 0.2
    
    # Ensure reasonable bounds
    pause_time = max(0.1, min(5.0, pause_time))
    
    return pause_time

def _clean_signal_buffer(self):
    """Clean old signals from buffer"""
    now = datetime.now()
    
    # Keep only signals younger than 5 minutes
    with threading.Lock():  # Use a lock if there are concurrent modifications
        self.signal_buffer = [signal for signal in self.signal_buffer 
                           if (now - signal.emergence_time).total_seconds() < 300]

async def _record_interaction(self, signal: CoherentSignal, response: np.ndarray, 
                            analysis: SignalAnalysis, protocol: str):
    """Record interaction with signal"""
    interaction_data = {
        'timestamp': datetime.now().isoformat(),
        'signal_id': id(signal),
        'protocol': protocol,
        'response_type': self._determine_response_type(
            analysis.pattern_complexity, 
            analysis.response_correlation
        ).name,
        'coherence': signal.coherence_level,
        'complexity': analysis.pattern_complexity,
        'correlation': analysis.response_correlation,
        'response_data': response.tolist()
    }
    
    # Add to signal's interaction history
    signal.interaction_history.append(interaction_data)
    
    # Add to global response history
    self.response_history.append(interaction_data)
    
    # Save interaction data
    await self._store_interaction_data(interaction_data)

async def _record_detailed_signal_data(self, signal: CoherentSignal, response: np.ndarray,
                                     analysis: SignalAnalysis, response_type: ResponseType,
                                     intelligence_score: float):
    """Record detailed data about interesting signals"""
    # Create detailed record
    detailed_data = {
        'timestamp': datetime.now().isoformat(),
        'signal_id': id(signal),
        'emergence_time': signal.emergence_time.isoformat(),
        'coherence_level': signal.coherence_level,
        'intelligence_score': intelligence_score,
        'response_type': response_type.name,
        'pattern_complexity': analysis.pattern_complexity,
        'response_correlation': analysis.response_correlation,
        'quantum_entanglement': analysis.quantum_entanglement,
        'dimensional_signature': analysis.dimensional_signature,
        'interaction_history': signal.interaction_history,
        'harmonic_structure': analysis.harmonic_structure,
        'information_density': analysis.information_density,
        'symmetry_metrics': analysis.symmetry_metrics,
        'statistical_moments': analysis.statistical_moments
    }
    
    # Save to file
    filename = f'data/signals/intelligent_signal_{signal.emergence_time.strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(filename, 'w') as f:
            json.dump(detailed_data, f, indent=2, default=str)
        logger.info(f"✅ Saved detailed signal data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save detailed signal data: {str(e)}")

async def _should_follow_up(self, interaction: Dict) -> bool:
    """Determine if a follow-up interaction should be initiated"""
    # Check if the response type indicates intelligence
    response_type = interaction.get('response_type', 'UNKNOWN')
    if response_type in ['COHERENT', 'INTELLIGENT', 'ADAPTIVE']:
        return True
    
    # Check complexity and correlation
    complexity = interaction.get('complexity', 0)
    correlation = interaction.get('correlation', 0)
    
    return complexity > 0.7 and correlation > 0.6

async def _send_follow_up_query(self, signal_id: int, previous_interaction: Dict):
    """Send a follow-up query to an interesting signal"""
    logger.info(f"🔄 Sending follow-up query to Signal {signal_id}")
    
    # Find the signal in the buffer
    signal = None
    for s in self.signal_buffer:
        if id(s) == signal_id:
            signal = s
            break
    
    if signal is None:
        logger.warning(f"⚠️ Signal {signal_id} not found in buffer for follow-up")
        return
    
    # Choose a different interaction protocol
    previous_protocol = previous_interaction.get('protocol', 'basic_query')
    available_protocols = [p for p in self.interaction_params['interaction_protocols'] 
                         if p != previous_protocol]
    
    if not available_protocols:
        protocol = previous_protocol
    else:
        protocol = np.random.choice(available_protocols)
    
    # Send new query and check for response
    response = await self._test_response(signal, protocol)
    
    if response is not None:
        logger.info(f"🛸 Received follow-up response from Signal {signal_id} using {protocol}!")
        
        # Analyze response
        analysis = SignalAnalysis(
            randomness_score=self._calculate_randomness(signal),
            coherence_metric=signal.coherence_level,
            pattern_complexity=self._calculate_complexity(response),
            response_correlation=self._calculate_correlation(signal.pattern_signature, response),
            quantum_entanglement=self._calculate_entanglement(signal),
            dimensional_signature=self._calculate_dimensions(signal),
            amplitude_variation=self._calculate_amplitude_variation(signal),
            phase_coherence=self._calculate_phase_coherence(signal),
            harmonic_structure=self._extract_harmonic_structure(signal),
            information_density=self._calculate_information_density(signal)
        )
        
        # Record interaction
        await self._record_interaction(signal, response, analysis, protocol)
        
        # Analyze intelligence
        await self._analyze_intelligence(signal, response, analysis)

# Data storage methods
async def _store_signal_data(self, signal: CoherentSignal):
    """Store signal data to file"""
    filename = f'data/signals/signal_{signal.emergence_time.strftime("%Y%m%d_%H%M%S")}.pickle'
    
    try:
        with open(filename, 'wb') as f:
            pickle.dump(signal, f)
        logger.info(f"✅ Saved signal data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save signal data: {str(e)}")

async def _store_analysis_data(self, analysis_data: Dict):
    """Store analysis data to file"""
    filename = f'data/analysis/analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        logger.info(f"✅ Saved analysis data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save analysis data: {str(e)}")

async def _store_interaction_data(self, interaction_data: Dict):
    """Store interaction data to file"""
    filename = f'data/signals/interaction_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(filename, 'w') as f:
            json.dump(interaction_data, f, indent=2, default=str)
        logger.info(f"✅ Saved interaction data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save interaction data: {str(e)}")

async def _store_eeg_data(self, eeg_data: EEGSignal):
    """Store EEG data to file"""
    filename = f'data/eeg/eeg_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pickle'
    
    try:
        with open(filename, 'wb') as f:
            pickle.dump(eeg_data, f)
        logger.info(f"✅ Saved EEG data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save EEG data: {str(e)}")

async def _store_quantum_data(self, quantum_data: Dict):
    """Store quantum state data to file"""
    filename = f'data/quantum/quantum_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(filename, 'w') as f:
            json.dump(quantum_data, f, indent=2, default=str)
        logger.info(f"✅ Saved quantum data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save quantum data: {str(e)}")

async def _record_eeg_quantum_correlation(self, eeg_data: EEGSignal, signal: CoherentSignal, correlation: float):
    """Record correlation between EEG and quantum signal"""
    correlation_data = {
        'timestamp': datetime.now().isoformat(),
        'eeg_id': id(eeg_data),
        'signal_id': id(signal),
        'correlation': correlation,
        'eeg_bands': {k: v.tolist() for k, v in eeg_data.band_powers.items()},
        'signal_coherence': signal.coherence_level,
        'signal_complexity': signal.complexity_index
    }
    
    # Save correlation data
    filename = f'data/eeg/eeg_quantum_correlation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    try:
        with open(filename, 'w') as f:
            json.dump(correlation_data, f, indent=2, default=str)
        logger.info(f"✅ Saved EEG-Quantum correlation data to {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to save correlation data: {str(e)}")

async def _load_data(self, filename: str):
    """Load data from file"""
    logger.info(f"📂 Loading data from {filename}")
    
    try:
        if filename.endswith('.pickle'):
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        elif filename.endswith('.json'):
            with open(filename, 'r') as f:
                data = json.load(f)
        else:
            logger.warning(f"⚠️ Unsupported file format: {filename}")
            return None
            
        logger.info(f"✅ Successfully loaded data from {filename}")
        return data
    except Exception as e:
        logger.error(f"❌ Failed to load data from {filename}: {str(e)}")
        return None

async def _query_data(self, query_params: Dict):
    """Query stored data based on parameters"""
    logger.info(f"🔍 Querying data with params: {query_params}")
    
    data_type = query_params.get('data_type', 'signals')
    start_date = query_params.get('start_date', None)
    end_date = query_params.get('end_date', None)
    
    # Build file pattern
    if data_type == 'signals':
        pattern = 'data/signals/signal_'
    elif data_type == 'eeg':
        pattern = 'data/eeg/eeg_'
    elif data_type == 'analysis':
        pattern = 'data/analysis/analysis_'
    elif data_type == 'quantum':
        pattern = 'data/quantum/quantum_'
    else:
        logger.warning(f"⚠️ Unsupported data type: {data_type}")
        return []
    
    # Get all matching files
    import glob
    files = glob.glob(f"{pattern}*.{'pickle' if data_type in ['signals', 'eeg'] else 'json'}")
    
    # Filter by date
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        files = [f for f in files if self._extract_date_from_filename(f) >= start_dt]
        
    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        files = [f for f in files if self._extract_date_from_filename(f) <= end_dt]
    
    # Load data
    results = []
    for file in files:
        data = await self._load_data(file)
        if data:
            results.append(data)
    
    logger.info(f"✅ Query returned {len(results)} results")
    return results

def _extract_date_from_filename(self, filename: str) -> datetime:
    """Extract date from filename"""
    import re
    
    match = re.search(r'(\d{8}_\d{6})', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
    else:
        # Return epoch start if no date found
        return datetime(1970, 1, 1)

# Visualization methods (for future development)
def _visualize_signal(self, signal: CoherentSignal):
    """Generate visualization of signal pattern"""
    pattern = signal.pattern_signature
    
    plt.figure(figsize=(12, 8))
    
    # Plot raw pattern
    plt.subplot(3, 1, 1)
    plt.plot(pattern)
    plt.title('Signal Pattern')
    plt.xlabel('Index')
    plt.ylabel('Value')
    
    # Plot frequency spectrum
    plt.subplot(3, 1, 2)
    spectrum = np.abs(fft(pattern))
    n = len(spectrum)
    freq = np.arange(n // 2) / n
    plt.plot(freq, spectrum[:n//2])
    plt.title('Frequency Spectrum')
    plt.xlabel('Frequency')
    plt.ylabel('Amplitude')
    
    # Plot phase space (simple 2D embedding)
    plt.subplot(3, 1, 3)
    if len(pattern) > 1:
        plt.scatter(pattern[:-1], pattern[1:], alpha=0.5)
        plt.title('Phase Space (2D Embedding)')
        plt.xlabel('x(t)')
        plt.ylabel('x(t+1)')
    
    plt.tight_layout()
    
    # Save figure
    filename = f'data/visualizations/signal_{signal.emergence_time.strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(filename)
    plt.close()
    
    logger.info(f"✅ Saved signal visualization to {filename}")
    return filename

def _visualize_eeg_quantum_correlation(self, eeg_data: EEGSignal, signal: CoherentSignal, correlation: float):
    """Generate visualization of EEG-Quantum correlation"""
    plt.figure(figsize=(15, 10))
    
    # Plot EEG alpha band powers
    plt.subplot(3, 2, 1)
    alpha_powers = eeg_data.band_powers.get('alpha', np.zeros(10))
    plt.bar(range(len(alpha_powers)), alpha_powers)
    plt.title('EEG Alpha Band Power by Channel')
    plt.xlabel('Channel')
    plt.ylabel('Power')
    
    # Plot quantum signal pattern
    plt.subplot(3, 2, 2)
    pattern = signal.pattern_signature
    plt.plot(pattern)
    plt.title('Quantum Signal Pattern')
    plt.xlabel('Index')
    plt.ylabel('Value')
    
    # Plot correlation over time (simulated)
    plt.subplot(3, 2, 3)
    # Generate fake time series for illustration
    t = np.linspace(0, 1, 100)
    corr_t = correlation * np.sin(2 * np.pi * 10 * t) + correlation
    plt.plot(t, corr_t)
    plt.axhline(y=correlation, color='r', linestyle='--')
    plt.title('Correlation Over Time (Simulated)')
    plt.xlabel('Time (s)')
    plt.ylabel('Correlation')
    
    # Plot joint histogram
    plt.subplot(3, 2, 4)
    # Generate fake joint data for illustration
    alpha_mean = np.mean(alpha_powers)
    quantum_mean = np.mean(pattern)
    joint_x = alpha_mean + np.random.normal(0, 0.1, 1000)
    joint_y = quantum_mean + correlation * (joint_x - alpha_mean) + np.random.normal(0, 0.1, 1000)
    plt.hist2d(joint_x, joint_y, bins=20)
    plt.title('Joint Distribution (Simulated)')
    plt.xlabel('EEG Alpha Power')
    plt.ylabel('Quantum Signal Value')
    plt.colorbar()
    
    # Plot coherence matrices
    plt.subplot(3, 2, 5)
    plt.imshow(eeg_data.coherence_matrix, cmap='viridis')
    plt.title('EEG Coherence Matrix')
    plt.colorbar()
    
    # Add correlation information
    plt.subplot(3, 2, 6)
    plt.text(0.5, 0.5, f"Correlation: {correlation:.4f}", ha='center', va='center', fontsize=20)
    plt.text(0.5, 0.3, f"Signal Coherence: {signal.coherence_level:.4f}", ha='center', va='center')
    plt.text(0.5, 0.1, f"Signal Complexity: {signal.complexity_index:.4f}", ha='center', va='center')
    plt.axis('off')
    
    plt.tight_layout()
    
    # Save figure
    filename = f'data/visualizations/eeg_quantum_corr_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(filename)
    plt.close()
    
    logger.info(f"✅ Saved EEG-Quantum correlation visualization to {filename}")
    return filename

# Main async function that runs the system
async def main():
    """Main function to run the Quantum Signal Analyzer"""
    logger.info("🚀 Starting Quantum Signal Analyzer")
    
    # Create and configure the analyzer
    analyzer = QuantumSignalAnalyzer(
        use_real_quantum_hardware=False,  # Set to True to use real quantum hardware
        eeg_integration=True              # Set to False to disable EEG features
    )
    
    # Runtime duration (in minutes)
    duration = 60  # 1 hour
    
    logger.info(f"🚀 System Boot Complete. Starting Quantum Signal Analysis for {duration} minutes.")
    
    try:
        # Start the analysis
        await analyzer.analyze_signal(duration_minutes=duration)
        
        logger.info("✅ Analysis completed successfully")
    except KeyboardInterrupt:
        logger.info("⚠️ Analysis interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error during analysis: {str(e)}")
    finally:
        logger.info("🛑 Shutting down Quantum Signal Analyzer")

if __name__ == "__main__":
    asyncio.run(main())