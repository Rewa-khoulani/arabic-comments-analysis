import fs from 'fs';

const DATASET_PATH = './dataset.json';
let cachedDataset = null;
let lastModifiedTime = 0;

export const getDataset = () => {
    if (!fs.existsSync(DATASET_PATH)) return null;
    
    try {
        const stats = fs.statSync(DATASET_PATH);
        if (cachedDataset && stats.mtimeMs === lastModifiedTime) {
            return cachedDataset;
        }

        const rawData = fs.readFileSync(DATASET_PATH, 'utf8');
        cachedDataset = JSON.parse(rawData);
        lastModifiedTime = stats.mtimeMs;
        return cachedDataset;
    } catch (err) {
        console.error("Error loading dataset:", err);
        return null;
    }
};