#!/usr/bin/env node

import { spawn } from 'child_process';

// Run TypeScript compiler first
const tsc = spawn('tsc', [], { 
  stdio: 'inherit',
  shell: true
});

tsc.on('close', (code) => {
  if (code !== 0) {
    console.error('TypeScript compilation failed');
    process.exit(code);
  }
  
  // Run Vite build after TypeScript compilation
  const vite = spawn('vite', ['build'], { 
    stdio: 'inherit',
    shell: true
  });
  
  vite.on('close', (code) => {
    process.exit(code);
  });
}); 