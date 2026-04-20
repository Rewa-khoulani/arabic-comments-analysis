import axios from 'axios';
import { getDataset } from '../utils/datasetLoader.js';

export const getCommentsByPostId = async (req, res) => {
    try {
        const { postId } = req.params;
        const dataset = getDataset();
        
        if (!dataset) {
            return res.status(404).json({ error: 'Dataset file not found' });
        }

        // Filter comments by post_id (ensure types match, e.g. string vs number)
        const postComments = dataset.filter(item => String(item.post_id) === String(postId));

        if (postComments.length === 0) {
            return res.status(404).json({ message: `No comments found for post_id ${postId}` });
        }

        res.json({
            post_id: postId,
            count: postComments.length,
            comments: postComments
        });

    } catch (error) {
        console.error('Error reading dataset:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
};

export const classifyCommentsByPostId = async (req, res) => {
    try {
        const { postId } = req.params;
        const dataset = getDataset();
        
        if (!dataset) {
            return res.status(404).json({ error: 'Dataset file not found' });
        }

        const postComments = dataset.filter(item => String(item.post_id) === String(postId));

        if (postComments.length === 0) {
            return res.status(404).json({ message: `No comments found for post_id ${postId}` });
        }

        const validComments = [];
        const invalidComments = [];

        postComments.forEach(item => {
            if (item.comment) {
                validComments.push(item);
            } else {
                invalidComments.push({
                    post_id: item.post_id,
                    comment: item.comment,
                    error: 'Invalid comment data: comment is missing or null'
                });
            }
        });

        let classifiedValidComments = [];

        if (validComments.length > 0) {
            try {// يلي بتاخد من كود البايثون الجواب من بردكت كلاسيفير 

                
                const response = await axios.post(`${process.env.PYTHON_API_URL}/predict_classifier`//
                    , {// هاد هو الريكوست داتا يلي عم ينبعت مع البوست ريكوست 
                    texts: validComments.map(c => c.comment)
                });
                // الداتا اللي رجعتلي من البايثون الكومنتات 
                const predictions = response.data;
                
                classifiedValidComments = validComments.map((item, index) => ({
                    post_id: item.post_id,
                    comment: item.comment,
                    classification: predictions[index]
                }));

            } catch (err) {
                console.error('Batch classification failed, falling back to individual:', err.message);
                // هي ركوست بترجع رسبونس 
                 const promises = validComments.map(async (item) => {
                    try {
                        const response = await axios.post(`${process.env.PYTHON_API_URL}/predict`, {
                            text: item.comment
                        });
                        return {
                            post_id: item.post_id,
                            comment: item.comment,
                            classification: response.data
                        };
                    } catch (e) {
                         return {
                            post_id: item.post_id,
                            comment: item.comment,
                            error: `Classification failed: ${e.message}`
                        };
                    }
                });
                classifiedValidComments = await Promise.all(promises);
            }
        }
// عم نجمع مصفوفة كومنتات 
        const classifiedComments = [...classifiedValidComments, ...invalidComments];

        let results = classifiedComments;
        // هي يلي بعد اشارة الاستفهام بالبوست مان
        // هي مشان رجع حسب الليبل 
        const { label } = req.query;
// اذا مابعتلا كويري يلي هوة ليبل بترجعلي كل الكومنتات 
        if (label) {
            results = classifiedComments.filter(item => 
                item.classification && 
                item.classification.pred_label_name.toLowerCase() === label.toLowerCase()
            );
        }

        res.json({
            post_id: postId,
            count: results.length,
            results: results
        });

    } catch (error) {
        console.error('Error in classifyCommentsByPostId:', error);
        res.status(500).json({ error: 'Internal Server Error' });
    }
};
