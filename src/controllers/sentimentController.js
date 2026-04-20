import axios from "axios"
import { getDataset } from "../utils/datasetLoader.js"

export const analyzeSentimentByPostId = async (req, res) => {
  try {
    const { postId } = req.params
    const dataset = getDataset()

    if (!dataset) {
      return res.status(404).json({ error: "Dataset file not found" })
    }

    const postComments = dataset.filter(
      (item) => String(item.post_id) === String(postId)
    )

    if (postComments.length === 0) {
      return res
        .status(404)
        .json({ message: `No comments found for post_id ${postId}` })
    }

    const validComments = postComments.filter(
      (item) => item.comment && typeof item.comment === "string"
    )

    if (validComments.length === 0) {
      return res.status(200).json({
        post_id: postId,
        sentiment_analysis: [],
        message: "No valid text comments found to analyze."
      })
    }

    const response = await axios.post(
      `${process.env.PYTHON_API_URL}/predict_sentiment`,
      {
        texts: validComments.map((c) => c.comment)
      }
    )

    const predictions = response.data

    const distribution = predictions.reduce((acc, curr) => {
        const label = curr.pred_label_name || 'Unknown';
        acc[label] = (acc[label] || 0) + 1;
        return acc;
    }, {});

    const total = predictions.length;
    const percentages = {};
    for (const [key, value] of Object.entries(distribution)) {
        percentages[key] = ((value / total) * 100).toFixed(2) + '%';
    }

    const results = validComments.map((item, index) => ({
      ...item,
      sentiment: predictions[index]
    }))

    res.json({
      post_id: postId,
      count: results.length,
      sentiment_distribution: percentages,
      results: results
    })
  } catch (error) {
    console.error("Error in sentiment analysis:", error.message)
    res.status(500).json({ error: "Internal Server Error" })
  }
}
