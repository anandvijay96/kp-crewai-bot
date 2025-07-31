#!/usr/bin/env node

/**
 * Test script to demonstrate graceful shutdown behavior
 * This simulates a simple server that handles SIGINT properly
 */

console.log('🚀 Test server starting...');
console.log('💡 Press Ctrl+C to test graceful shutdown');

let isShuttingDown = false;

// Simulate some work
const interval = setInterval(() => {
  if (!isShuttingDown) {
    console.log('⚡ Server is running... (tick)');
  }
}, 2000);

// Handle graceful shutdown
process.on('SIGINT', async () => {
  if (isShuttingDown) {
    console.log('⚠️ Force shutdown detected!');
    process.exit(1);
  }
  
  isShuttingDown = true;
  console.log('\n🛑 Received SIGINT (Ctrl+C). Gracefully shutting down...');
  
  // Clear the interval
  clearInterval(interval);
  
  // Simulate cleanup work
  console.log('🔄 Cleaning up resources...');
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  console.log('✅ Cleanup complete');
  console.log('👋 Graceful shutdown complete. Goodbye!');
  process.exit(0);
});

// Prevent the process from exiting immediately
process.stdin.resume();
