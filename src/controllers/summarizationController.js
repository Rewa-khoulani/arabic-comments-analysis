import axios from "axios"
import { getDataset } from "../utils/datasetLoader.js"

export const summarizeCommentsByPostId = async (req, res) => {
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

    const validComments = postComments
      .map((item) => item.comment)
      .filter((c) => c && typeof c === "string")

    if (validComments.length === 0) {
      return res.status(200).json({ summary: "No content to summarize." })
    }

    const response = await axios.post(
      `${process.env.PYTHON_API_URL}/summarize`,
      {
        texts: validComments
      }
    )

    res.json({
      post_id: postId,
      comment_count: validComments.length,
      summary: response.data.summary
    })
  } catch (error) {
    console.error("Error in summarization:", error.message)
    res.status(500).json({ error: "Internal Server Error" })
  }
}
