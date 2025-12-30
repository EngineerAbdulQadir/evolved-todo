"use client";

import React, { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

function LoadingBox() {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.x += 0.01;
      meshRef.current.rotation.y += 0.01;
      const s = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.1;
      meshRef.current.scale.set(s, s, s);
    }
  });

  return (
    <mesh ref={meshRef}>
      <boxGeometry args={[1, 1, 1]} />
      <meshBasicMaterial color="#ffffff" wireframe />
    </mesh>
  );
}

interface Loader3DProps {
  label?: string;
}

export function Loader3D({ label = "INITIALIZING..." }: Loader3DProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <div className="w-16 h-16">
        <Canvas camera={{ position: [0, 0, 3] }}>
          <ambientLight intensity={0.5} />
          <LoadingBox />
        </Canvas>
      </div>
      <div className="text-white font-mono text-[10px] uppercase tracking-[0.3em] animate-pulse">
        {label}
      </div>
    </div>
  );
}
