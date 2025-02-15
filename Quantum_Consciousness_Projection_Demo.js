import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { Brain, Activity, Zap, CircuitBoard, Server, Waveform, Heart, Box, AlertCircle } from 'lucide-react';

const QuantumNeuralInterface = () => {
  const [vitalMetrics, setVitalMetrics] = useState({
    neuralSync: 0,
    quantumCoherence: 0,
    brainwaveSync: 0,
    systemIntegrity: 0
  });

  const [brainwaveData, setBrainwaveData] = useState({
    alpha: 0,
    beta: 0,
    theta: 0,
    gamma: 0,
    delta: 0
  });

  const [systemStatus, setSystemStatus] = useState({
    active: false,
    progress: 0,
    phase: 'standby',
    alerts: []
  });

  const [telemetryHistory, setTelemetryHistory] = useState([]);
  const [safetyMetrics, setSafetyMetrics] = useState({
    patternStability: 1.0,
    quantumIntegrity: 1.0,
    neuralSafety: 1.0
  });

  useEffect(() => {
    if (systemStatus.active) {
      const interval = setInterval(() => {
        updateSystemState();
      }, 50); // Faster updates for smoother visualization
      return () => clearInterval(interval);
    }
  }, [systemStatus.active]);

  const updateSystemState = () => {
    if (systemStatus.progress < 100) {
      // Update neural telemetry
      setVitalMetrics(prev => ({
        neuralSync: Math.min(1, prev.neuralSync + 0.02),
        quantumCoherence: calculateQuantumCoherence(systemStatus.progress + 1),
        brainwaveSync: calculateBrainwaveSync(systemStatus.progress + 1),
        systemIntegrity: Math.min(1, prev.systemIntegrity + 0.01)
      }));

      // Update brainwave frequencies
      setBrainwaveData({
        alpha: Math.sin(Date.now() * 0.001) * 0.3 + 0.6,
        beta: Math.sin(Date.now() * 0.002) * 0.3 + 0.6,
        theta: Math.sin(Date.now() * 0.003) * 0.3 + 0.6,
        gamma: Math.sin(Date.now() * 0.004) * 0.3 + 0.6,
        delta: Math.sin(Date.now() * 0.005) * 0.3 + 0.6
      });

      // Update system status
      setSystemStatus(prev => ({
        ...prev,
        progress: prev.progress + 0.5,
        phase: getSystemPhase(prev.progress + 0.5)
      }));

      // Update telemetry history
      setTelemetryHistory(prev => [...prev, {
        timestamp: Date.now(),
        neuralSync: vitalMetrics.neuralSync,
        quantumCoherence: vitalMetrics.quantumCoherence,
        brainwaveSync: vitalMetrics.brainwaveSync
      }].slice(-200)); // Keep last 200 data points

      // Update safety metrics
      setSafetyMetrics({
        patternStability: 0.95 + Math.random() * 0.05,
        quantumIntegrity: 0.97 + Math.random() * 0.03,
        neuralSafety: 0.98 + Math.random() * 0.02
      });
    }
  };

  const calculateQuantumCoherence = (progress) => {
    return Math.sin(progress * 0.0991) * 0.3 + 0.7;
  };

  const calculateBrainwaveSync = (progress) => {
    return Math.sin(progress * 0.0987) * 0.2 + 0.8;
  };

  const getSystemPhase = (progress) => {
    if (progress < 20) return 'neural_calibration';
    if (progress < 40) return 'quantum_initialization';
    if (progress < 60) return 'bridge_formation';
    if (progress < 80) return 'consciousness_sync';
    if (progress < 100) return 'stability_verification';
    return 'operational';
  };

  const getPhaseDescription = (phase) => {
    const phases = {
      'standby': 'System Standby - Ready for Initialization',
      'neural_calibration': 'Neural Interface Calibration (98.7 Hz)',
      'quantum_initialization': 'Quantum Coherence Initialization (99.1 Hz)',
      'bridge_formation': 'Neural-Quantum Bridge Formation (98.9 Hz)',
      'consciousness_sync': 'Consciousness Pattern Synchronization',
      'stability_verification': 'System Stability Verification',
      'operational': 'System Operational - Full Bridge Established'
    };
    return phases[phase] || phase;
  };

  const startSystem = () => {
    setSystemStatus({
      active: true,
      progress: 0,
      phase: 'neural_calibration',
      alerts: []
    });
    setTelemetryHistory([]);
  };

  return (
    <div className="w-full max-w-7xl mx-auto p-6 space-y-6 bg-gray-50">
      {/* Header */}
      <div className="flex justify-between items-center bg-white p-4 rounded-lg shadow">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            SAAAM Neural Interface System
          </h1>
          <p className="text-sm text-gray-600">Quantum-Enhanced Neural Bridge v1.0</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-600">
            System Status: 
            <span className="ml-2 font-semibold text-green-600">
              {systemStatus.active ? 'ACTIVE' : 'STANDBY'}
            </span>
          </div>
          <button
            onClick={startSystem}
            disabled={systemStatus.active}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
          >
            {systemStatus.active ? 'System Active' : 'Initialize System'}
          </button>
        </div>
      </div>

      {/* Primary Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2">
            <Brain className="w-6 h-6 text-blue-500" />
            <span className="font-semibold">Neural Sync</span>
          </div>
          <div className="mt-2">
            <div className="text-3xl font-bold text-blue-600">
              {(vitalMetrics.neuralSync * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Pattern Stability</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2">
            <CircuitBoard className="w-6 h-6 text-purple-500" />
            <span className="font-semibold">Quantum Coherence</span>
          </div>
          <div className="mt-2">
            <div className="text-3xl font-bold text-purple-600">
              {(vitalMetrics.quantumCoherence * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Field Stability</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2">
            <Waveform className="w-6 h-6 text-green-500" />
            <span className="font-semibold">Brainwave Sync</span>
          </div>
          <div className="mt-2">
            <div className="text-3xl font-bold text-green-600">
              {(vitalMetrics.brainwaveSync * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Pattern Matching</div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2">
            <Heart className="w-6 h-6 text-red-500" />
            <span className="font-semibold">System Integrity</span>
          </div>
          <div className="mt-2">
            <div className="text-3xl font-bold text-red-600">
              {(vitalMetrics.systemIntegrity * 100).toFixed(1)}%
            </div>
            <div className="text-sm text-gray-500">Overall Health</div>
          </div>
        </div>
      </div>

      {/* System Phase & Safety Metrics */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <Server className="w-6 h-6 text-gray-500" />
            <span className="font-semibold">System Phase:</span>
            <span className="text-blue-600 font-medium">
              {getPhaseDescription(systemStatus.phase)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-300"
              style={{ width: `${systemStatus.progress}%` }}
            ></div>
          </div>
          <div className="mt-2 text-sm text-gray-500 flex justify-between">
            <span>0%</span>
            <span>System Progress</span>
            <span>100%</span>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center space-x-2 mb-4">
            <AlertCircle className="w-6 h-6 text-yellow-500" />
            <span className="font-semibold">Safety Metrics</span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Pattern Stability</span>
              <span className="font-medium">{(safetyMetrics.patternStability * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Quantum Integrity</span>
              <span className="font-medium">{(safetyMetrics.quantumIntegrity * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Neural Safety</span>
              <span className="font-medium">{(safetyMetrics.neuralSafety * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Telemetry & Brainwave Analysis */}
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2 bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Neural Telemetry</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={telemetryHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" hide />
                <YAxis domain={[0, 1]} />
                <Tooltip 
                  formatter={(value) => `${(value * 100).toFixed(1)}%`}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="neuralSync" 
                  stroke="#2563eb" 
                  name="Neural Sync"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="quantumCoherence" 
                  stroke="#9333ea" 
                  name="Quantum Coherence"
                  strokeWidth={2}
                />
                <Line 
                  type="monotone" 
                  dataKey="brainwaveSync" 
                  stroke="#16a34a" 
                  name="Brainwave Sync"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Brainwave Analysis</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={[{
                name: 'Frequencies',
                alpha: brainwaveData.alpha,
                beta: brainwaveData.beta,
                theta: brainwaveData.theta,
                gamma: brainwaveData.gamma,
                delta: brainwaveData.delta
              }]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" hide />
                <YAxis domain={[0, 1]} />
                <Tooltip 
                  formatter={(value) => `${(value * 100).toFixed(1)}%`}
                />
                <Legend />
                <Bar dataKey="alpha" fill="#3b82f6" name="Alpha" />
                <Bar dataKey="beta" fill="#8b5cf6" name="Beta" />
                <Bar dataKey="theta" fill="#10b981" name="Theta" />
                <Bar dataKey="gamma" fill="#f59e0b" name="Gamma" />
                <Bar dataKey="delta" fill="#ef4444" name="Delta" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuantumNeuralInterface;
