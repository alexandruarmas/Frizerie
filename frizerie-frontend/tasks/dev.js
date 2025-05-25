#!/usr/bin/env node

import { spawn } from 'child_process';

// Run Vite dev server
const vite = spawn('vite', [], { 
  stdio: 'inherit',
  shell: true
});

// Handle process termination
process.on('SIGINT', () => {
  vite.kill('SIGINT');
  process.exit(0);
});

process.on('SIGTERM', () => {
  vite.kill('SIGTERM');
  process.exit(0);
});

vite.on('close', (code) => {
  process.exit(code);
}); 