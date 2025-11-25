const fs = require('fs');
const path = require('path');
const parseCareer = require('fifa-career-save-parser');
require('dotenv').config({ path: '../.env' });

/**
 * FC26 Save Parser - Dynamic Script
 * Accepts save path as command line argument
 */

// Get save path from command line argument or use default (fallback)
const defaultSavePath = process.env.FC26_SAVES_PATH 
    ? path.join(process.env.FC26_SAVES_PATH, 'CmMgrC20251119080713440')
    : 'C:\\Users\\mateu\\AppData\\Local\\EA SPORTS FC 26\\settings\\CmMgrC20251119080713440';

const saveFilePath = process.argv[2] || defaultSavePath;

const outputPath = path.join(__dirname, 'output', 'test_parse.json');
const parserMode = 21; // FIFA 21 mode for FC 26 compatibility

async function parseCareerSave() {
    console.log('🎮 FC26 Save Parser');
    console.log('='.repeat(60));
    console.log('');
    
    try {
        // Step 1: Verify save file exists
        console.log('📂 Step 1: Locating save file...');
        console.log(`   Path: ${saveFilePath}`);
        
        if (!fs.existsSync(saveFilePath)) {
            throw new Error(`Save file not found at: ${saveFilePath}`);
        }
        
        const stats = fs.statSync(saveFilePath);
        console.log(`   ✅ Found save file (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
        console.log('');
        
        // Step 2: Parse save file
        console.log('⚙️  Step 2: Parsing save file...');
        console.log('   This may take 10-30 seconds...');
        
        const startTime = Date.now();
        const fileBuffer = fs.readFileSync(saveFilePath);
        const result = await parseCareer(fileBuffer, parserMode);
        
        const parseTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`   ✅ Parsing completed in ${parseTime}s`);
        console.log('');
        
        // Step 3: Merge databases if array
        let mergedResult = {};
        if (Array.isArray(result)) {
            console.log(`   ℹ️  Found ${result.length} databases in save file`);
            result.forEach(db => {
                mergedResult = { ...mergedResult, ...db };
            });
        } else {
            mergedResult = result;
        }
        
        // Step 4: Calculate statistics
        console.log('📈 Step 3: Statistics:');
        
        let totalRecords = 0;
        const tableSummary = {};
        
        for (const [tableName, data] of Object.entries(mergedResult)) {
            if (Array.isArray(data)) {
                tableSummary[tableName] = data.length;
                totalRecords += data.length;
            }
        }
        
        const tableCount = Object.keys(mergedResult).length;
        console.log(`   Total tables: ${tableCount}`);
        console.log(`   Total records: ${totalRecords.toLocaleString()}`);
        console.log('');
        
        // Show top tables
        console.log('   Top 5 largest tables:');
        const sortedTables = Object.entries(tableSummary)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);
        
        for (const [tableName, count] of sortedTables) {
            console.log(`   - ${tableName}: ${count.toLocaleString()} records`);
        }
        console.log('');
        
        // Step 5: Save output
        console.log('💾 Step 4: Saving output...');
        
        const outputDir = path.dirname(outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        fs.writeFileSync(
            outputPath, 
            JSON.stringify(mergedResult, null, 2),
            'utf8'
        );
        
        console.log(`   ✅ Saved to: ${outputPath}`);
        console.log('');
        
        // Final message
        console.log('='.repeat(60));
        console.log('🎉 PARSING COMPLETE');
        console.log('='.repeat(60));
        console.log('');
        
        return {
            success: true,
            tableCount,
            totalRecords,
            parseTime,
            outputPath
        };
        
    } catch (error) {
        console.log('');
        console.log('='.repeat(60));
        console.log('❌ PARSING FAILED');
        console.log('='.repeat(60));
        console.log('');
        console.log('Error:', error.message);
        console.log('');
        console.log('Stack trace:');
        console.log(error.stack);
        console.log('');
        
        return {
            success: false,
            error: error.message
        };
    }
}

// Run parser
parseCareerSave()
    .then(result => {
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        console.error('Unexpected error:', error);
        process.exit(1);
    });
