import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const NetworkVisualization = () => {
  const [network, setNetwork] = useState(null);
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    // Simulate network updates
    const interval = setInterval(() => {
      setRotation(prev => (prev + 1) % 360);
    }, 50);

    return () => clearInterval(interval);
  }, []);

  const renderNode = (node, index) => {
    const x = node.position[0] * 400;
    const y = node.position[1] * 400;
    const z = node.position[2] * 100;
    
    const transformStyle = {
      transform: `translate(${x}px, ${y}px) translateZ(${z}px) rotateY(${rotation}deg)`,
      position: 'absolute',
      width: '20px',
      height: '20px',
      borderRadius: '50%',
      background: `rgba(${node.stability * 255}, ${node.coherence * 255}, 255, 0.8)`,
      boxShadow: `0 0 10px rgba(${node.stability * 255}, ${node.coherence * 255}, 255, 0.5)`,
      transition: 'all 0.1s ease-out'
    };

    return (
      <div key={node.id} style={transformStyle}>
        <div className="text-xs text-white absolute -top-5 whitespace-nowrap">
          {node.id}
        </div>
      </div>
    );
  };

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>Quantum Network Visualization</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative w-full h-96 bg-black rounded-lg overflow-hidden perspective-1000">
          <div 
            className="absolute w-full h-full"
            style={{
              transformStyle: 'preserve-3d',
              transform: `rotateY(${rotation}deg)`
            }}
          >
            {network?.nodes.map(renderNode)}
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="p-4 border rounded">
            <h3 className="font-bold text-sm">Active Nodes</h3>
            <p className="text-xl">{network?.nodes.length || 0}</p>
          </div>
          <div className="p-4 border rounded">
            <h3 className="font-bold text-sm">Average Stability</h3>
            <p className="text-xl">
              {network?.nodes.reduce((acc, n) => acc + n.stability, 0) / (network?.nodes.length || 1)}
            </p>
          </div>
          <div className="p-4 border rounded">
            <h3 className="font-bold text-sm">Network Coherence</h3>
            <p className="text-xl">
              {network?.nodes.reduce((acc, n) => acc + n.coherence, 0) / (network?.nodes.length || 1)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default NetworkVisualization;
