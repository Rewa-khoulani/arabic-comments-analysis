import express from 'express';
import { getCommentsByPostId, classifyCommentsByPostId } from '../controllers/classificationController.js';
import { analyzeSentimentByPostId } from '../controllers/sentimentController.js';
import { summarizeCommentsByPostId } from '../controllers/summarizationController.js';

const router = express.Router();

router.get('/posts/:postId/comments', getCommentsByPostId);
router.get('/posts/:postId/classify', classifyCommentsByPostId);
router.get('/posts/:postId/sentiment', analyzeSentimentByPostId);
router.get('/posts/:postId/summarize', summarizeCommentsByPostId);

export default router;
