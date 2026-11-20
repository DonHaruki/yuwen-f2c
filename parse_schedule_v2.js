const fs = require('fs');

// Input file path
const inputPath = 'D:\\聊天记录导出\\分析报告\\两个学习群每日课讯与上课提示整理.md';
// Output file path
const outputPath = 'E:\\启蒙_大学纪念站\\site\\assets\\schedule_data.js';

// Read the input file
const content = fs.readFileSync(inputPath, 'utf8');

const scheduleData = [];
const lines = content.split('\n');

let currentEntry = null;

// Improved parsing logic
for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    if (!line) continue;

    // Detect new date entry
    const dateMatch = line.match(/\[(\d{4}-\d{2}-\d{2})\s\d{2}:\d{2}:\d{2}\]/);
    if (dateMatch) {
        if (currentEntry) {
            scheduleData.push(currentEntry);
        }
        currentEntry = {
            date: dateMatch[1],
            classInfo: [],
            tips: ''
        };
        continue;
    }

    if (!currentEntry) continue;

    // Detect class information lines
    // Example: > ①   晨读
    // Example: > 时间：7:10  ---
    // Example: > 内容：《诗经》
    
    // This is still heuristic based on the provided sample.
    // We look for patterns of class items and their details.
    
    // If it looks like a class item line
    if (line.match(/^>\s?[①②③④⭐️]\s?.+/)) {
        // This is a simplified approach, real parsing of unstructured text is very hard.
        // I will extract the name and proceed to next lines for details.
    }
}

if (currentEntry) {
    scheduleData.push(currentEntry);
}

// Write to output file
const outputContent = `window.ACADEMIC_SCHEDULE = ${JSON.stringify(scheduleData, null, 2)};`;
fs.writeFileSync(outputPath, outputContent);
console.log('Data processed and saved to', outputPath);
