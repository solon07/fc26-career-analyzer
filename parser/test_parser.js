const fs = require('fs');
const path = require('path');
const parseCareer = require('fifa-career-save-parser');
require('dotenv').config({ path: '../.env' });

// Configuration
const CONFIG = {
    saveFilePath: process.env.FC26_SAVES_PATH 
        ? path.join(process.env.FC26_SAVES_PATH, 'CmMgrC20251119080713440')
        : 'C:\\Users\\mateu\\AppData\\Local\\EA SPORTS FC 26\\settings\\CmMgrC20251119080713440',
    outputPath: path.join(__dirname, 'output', 'test_parse.json'),
    xmlPath: path.join(__dirname, 'xml', '21', 'fifa_ng_db-meta.xml'),
    parserMode: 21 // FIFA 21 mode for FC 26 compatibility
};

// Critical tables to check
const CRITICAL_TABLES = [
    'career_playergrowthuserseason',
    'career_playerlastgrowth',
    'career_playercontract',
    'career_managerinfo',
    'career_users'
];

async function validateParser() {
    console.log('🎮 FC26 Save Parser - Validation Test');
    console.log('=' .repeat(60));
    console.log('');
    
    try {
        // Step 1: Verify save file exists
        console.log('📂 Step 1: Locating save file...');
        console.log(`   Path: ${CONFIG.saveFilePath}`);
        
        if (!fs.existsSync(CONFIG.saveFilePath)) {
            throw new Error(`Save file not found at: ${CONFIG.saveFilePath}`);
        }
        
        const stats = fs.statSync(CONFIG.saveFilePath);
        console.log(`   ✅ Found save file (${(stats.size / 1024 / 1024).toFixed(2)} MB)`);
        console.log('');
        
        // Step 2: Verify XML metadata exists
        console.log('📄 Step 2: Verifying XML metadata...');
        console.log(`   Path: ${CONFIG.xmlPath}`);
        
        if (!fs.existsSync(CONFIG.xmlPath)) {
            throw new Error(`XML metadata not found at: ${CONFIG.xmlPath}`);
        }
        
        console.log(`   ✅ XML metadata found`);
        console.log('');
        
        // Step 3: Attempt parsing
        console.log('⚙️  Step 3: Parsing save file...');
        console.log('   This may take 10-30 seconds...');
        
        const startTime = Date.now();
        
        const fileBuffer = fs.readFileSync(CONFIG.saveFilePath);
        
        const result = await parseCareer(fileBuffer, CONFIG.parserMode);
        
        const parseTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`   ✅ Parsing completed in ${parseTime}s`);
        console.log('');
        
        // Flatten the array of databases into a single object
        let mergedResult = {};
        if (Array.isArray(result)) {
            console.log(`   ℹ️  Found ${result.length} databases in save file`);
            result.forEach(db => {
                mergedResult = { ...mergedResult, ...db };
            });
        } else {
            mergedResult = result;
        }
        
        // Step 4: Validate structure
        console.log('🔍 Step 4: Validating data structure...');
        
        const tables = Object.keys(mergedResult);
        const tableCount = tables.length;
        
        // Use mergedResult for further checks instead of result
        const dataToValidate = mergedResult;
        
        console.log(`   Total tables found: ${tableCount}`);
        console.log('');
        
        // Check for critical tables
        console.log('   Checking critical tables:');
        const missingTables = [];
        
        for (const tableName of CRITICAL_TABLES) {
            if (result[tableName]) {
                const recordCount = Array.isArray(result[tableName]) 
                    ? result[tableName].length 
                    : 'N/A';
                console.log(`   ✅ ${tableName}: ${recordCount} records`);
            } else {
                console.log(`   ❌ ${tableName}: MISSING`);
                missingTables.push(tableName);
            }
        }
        console.log('');
        
        // Step 5: Sample data preview
        console.log('📊 Step 5: Sample data preview:');
        
        if (result.career_playergrowthuserseason && result.career_playergrowthuserseason.length > 0) {
            const player = result.career_playergrowthuserseason[0];
            console.log('   Sample player from squad:');
            console.log(`   - Name: ${player.firstname || 'N/A'} ${player.surname || 'N/A'}`);
            console.log(`   - Overall: ${player.overallrating || 'N/A'}`);
            console.log(`   - Potential: ${player.potential || 'N/A'}`);
            console.log(`   - Age: ${player.age || 'N/A'}`);
            console.log(`   - Position: ${player.preferredposition1 || 'N/A'}`);
        }
        console.log('');
        
        // Step 6: Calculate statistics
        console.log('📈 Step 6: Statistics:');
        
        let totalRecords = 0;
        const tableSummary = {};
        
        for (const [tableName, data] of Object.entries(result)) {
            if (Array.isArray(data)) {
                tableSummary[tableName] = data.length;
                totalRecords += data.length;
            }
        }
        
        console.log(`   Total records across all tables: ${totalRecords.toLocaleString()}`);
        console.log('');
        console.log('   Top 10 largest tables:');
        
        const sortedTables = Object.entries(tableSummary)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10);
        
        for (const [tableName, count] of sortedTables) {
            console.log(`   - ${tableName}: ${count.toLocaleString()} records`);
        }
        console.log('');
        
        // Step 7: Save output
        console.log('💾 Step 7: Saving output...');
        
        const outputDir = path.dirname(CONFIG.outputPath);
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        fs.writeFileSync(
            CONFIG.outputPath, 
            JSON.stringify(result, null, 2),
            'utf8'
        );
        
        console.log(`   ✅ Saved to: ${CONFIG.outputPath}`);
        console.log('');
        
        // Final verdict
        console.log('=' .repeat(60));
        
        if (missingTables.length > 0) {
            console.log('⚠️  PARSER VALIDATION: PARTIAL SUCCESS');
            console.log('=' .repeat(60));
            console.log('');
            console.log(`✅ Parser works with FC 26!`);
            console.log(`✅ ${tableCount} tables extracted`);
            console.log(`✅ ${totalRecords.toLocaleString()} total records`);
            console.log('');
            console.log(`⚠️  Warning: ${missingTables.length} critical tables missing:`);
            for (const table of missingTables) {
                console.log(`   - ${table}`);
            }
            console.log('');
            console.log('💡 This is still usable - we can work with available tables.');
        } else {
            console.log('🎉 PARSER VALIDATION: COMPLETE SUCCESS');
            console.log('=' .repeat(60));
            console.log('');
            console.log(`✅ FC 26 save parsing works perfectly!`);
            console.log(`✅ All ${CRITICAL_TABLES.length} critical tables present`);
            console.log(`✅ ${tableCount} tables extracted`);
            console.log(`✅ ${totalRecords.toLocaleString()} total records`);
            console.log('');
            console.log('🚀 Ready to proceed with Sprint 1!');
        }
        console.log('');
        
        return {
            success: true,
            tableCount,
            totalRecords,
            missingTables,
            parseTime,
            outputPath: CONFIG.outputPath
        };
        
    } catch (error) {
        console.log('');
        console.log('=' .repeat(60));
        console.log('❌ PARSER VALIDATION: FAILED');
        console.log('=' .repeat(60));
        console.log('');
        console.log('Error:', error.message);
        console.log('');
        console.log('Stack trace:');
        console.log(error.stack);
        console.log('');
        console.log('Possible causes:');
        console.log('1. FC 26 save format changed (not compatible with FIFA 21 mode)');
        console.log('2. XML metadata incorrect or corrupted');
        console.log('3. Save file corrupted');
        console.log('4. Parser library incompatible with Node.js v25');
        console.log('');
        console.log('Next steps:');
        console.log('- Verify save file is from Career Mode (not other game modes)');
        console.log('- Try with a different/newer save file');
        console.log('- Check parser library version compatibility');
        console.log('- Consider Plan B: FIFA Live Editor');
        console.log('');
        
        return {
            success: false,
            error: error.message
        };
    }
}

// Run validation
validateParser()
    .then(result => {
        process.exit(result.success ? 0 : 1);
    })
    .catch(error => {
        console.error('Unexpected error:', error);
        process.exit(1);
    });
