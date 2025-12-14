#!/usr/bin/env node
/**
 * Node.js job with axios for external connections
 * This job makes HTTP requests to external APIs
 */

const axios = require('axios');
const process = require('process');

const EXTERNAL_API = process.env.EXTERNAL_API_URL || 'https://jsonplaceholder.typicode.com/posts/1';
const MAX_RETRIES = parseInt(process.env.MAX_RETRIES || '3', 10);
const RETRY_DELAY = parseInt(process.env.RETRY_DELAY || '1000', 10);

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchExternalData(url, retries = MAX_RETRIES) {
    for (let i = 0; i < retries; i++) {
        try {
            console.log(`[Attempt ${i + 1}/${retries}] Fetching data from: ${url}`);
            
            const response = await axios.get(url, {
                timeout: 10000,
                headers: {
                    'User-Agent': 'k8s-node-job/1.0'
                }
            });
            
            console.log('✓ Successfully fetched data');
            console.log(`  Status: ${response.status} ${response.statusText}`);
            console.log(`  Data preview:`, JSON.stringify(response.data).substring(0, 100) + '...');
            
            return response.data;
        } catch (error) {
            console.error(`✗ Attempt ${i + 1} failed:`, error.message);
            
            if (i < retries - 1) {
                console.log(`  Retrying in ${RETRY_DELAY}ms...`);
                await sleep(RETRY_DELAY);
            } else {
                throw error;
            }
        }
    }
}

async function processData(data) {
    console.log('\nProcessing fetched data...');
    
    // Example processing
    if (data && typeof data === 'object') {
        const keys = Object.keys(data);
        console.log(`  Found ${keys.length} fields in response`);
        console.log(`  Fields: ${keys.join(', ')}`);
    }
    
    return { processed: true, timestamp: new Date().toISOString() };
}

async function main() {
    console.log('==========================================');
    console.log('Node.js Job with External Connections');
    console.log(`Started at: ${new Date().toISOString()}`);
    console.log(`Pod Name: ${process.env.HOSTNAME || 'unknown'}`);
    console.log(`Job Name: ${process.env.JOB_NAME || 'node-job'}`);
    console.log('==========================================\n');
    
    try {
        // Fetch data from external API
        const data = await fetchExternalData(EXTERNAL_API);
        
        // Process the data
        const result = await processData(data);
        
        console.log('\n==========================================');
        console.log('Job completed successfully!');
        console.log(`Completed at: ${new Date().toISOString()}`);
        console.log('==========================================');
        
        process.exit(0);
    } catch (error) {
        console.error('\n==========================================');
        console.error('Job failed with error:');
        console.error(error.message);
        if (error.response) {
            console.error(`  Status: ${error.response.status}`);
            console.error(`  Status Text: ${error.response.statusText}`);
        }
        console.error('==========================================');
        process.exit(1);
    }
}

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

main();

