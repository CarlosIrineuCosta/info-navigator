// Simple test to debug the data loading issue
const fs = require('fs');
const path = require('path');

// Load the JSON files directly
const contentSetsPath = path.join(__dirname, '../public/data/content_sets.json');
const cardsPath = path.join(__dirname, '../public/data/cards.json');
const creatorsPath = path.join(__dirname, '../public/data/creators.json');

console.log('=== DEBUGGING DATA LOADING ===\n');

try {
    // Load all data
    const contentSets = JSON.parse(fs.readFileSync(contentSetsPath, 'utf8'));
    const cards = JSON.parse(fs.readFileSync(cardsPath, 'utf8'));
    const creators = JSON.parse(fs.readFileSync(creatorsPath, 'utf8'));
    
    console.log('✅ Data loaded successfully:');
    console.log(`   Content Sets: ${contentSets.length}`);
    console.log(`   Cards: ${cards.length}`);
    console.log(`   Creators: ${creators.length}\n`);
    
    // Test the specific setId that's failing
    const setId = 'anacontti50mais_dc55d49d_wellness_20250602_2102';
    console.log(`🔍 Testing setId: ${setId}\n`);
    
    // Step 1: Find content set
    const contentSet = contentSets.find(set => set.set_id === setId);
    console.log('Step 1 - Find content set:');
    console.log(`   Found: ${!!contentSet}`);
    if (contentSet) {
        console.log(`   Title: ${contentSet.title}`);
        console.log(`   Creator ID: ${contentSet.creator_id}`);
    } else {
        console.log('   Available set IDs:');
        contentSets.forEach((set, i) => {
            console.log(`     ${i + 1}. ${set.set_id} - ${set.title}`);
        });
        process.exit(1);
    }
    console.log();
    
    // Step 2: Find creator
    const creator = creators.find(c => c.creator_id === contentSet.creator_id);
    console.log('Step 2 - Find creator:');
    console.log(`   Found: ${!!creator}`);
    if (creator) {
        console.log(`   Name: ${creator.display_name}`);
    }
    console.log();
    
    // Step 3: Find cards for this set
    const setCards = cards.filter(card => card.set_id === setId);
    console.log('Step 3 - Find cards:');
    console.log(`   Cards found: ${setCards.length}`);
    if (setCards.length > 0) {
        console.log('   Card titles:');
        setCards.forEach((card, i) => {
            console.log(`     ${i + 1}. ${card.title}`);
        });
    }
    console.log();
    
    // Test what getContentSetById should return
    const finalResult = {
        ...contentSet,
        creator: creator || { display_name: 'Autor Desconhecido' }
    };
    
    console.log('✅ Final result structure:');
    console.log(`   Has set_id: ${!!finalResult.set_id}`);
    console.log(`   Has title: ${!!finalResult.title}`);
    console.log(`   Has creator: ${!!finalResult.creator}`);
    console.log(`   Creator name: ${finalResult.creator.display_name}`);
    console.log();
    
    console.log('🎯 CONCLUSION: Data loading should work perfectly!');
    console.log('   The issue must be in the React component logic or error handling.');
    
} catch (error) {
    console.log('❌ Error loading data:', error.message);
    console.log('   Check if JSON files exist and are valid');
}
