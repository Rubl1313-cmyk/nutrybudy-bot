// Brain module using Cloudflare AI's hermes-2-pro-mistral-7b for reasoning
export async function processTextWithBrain(AI, prompt) {
  try {
    const response = await AI.run(
      "@cf/hermes-2-pro-mistral-7b",
      {
        prompt: prompt,
        max_tokens: 500, // Adjust as needed
        temperature: 0.7
      }
    );
    
    // The response is expected to be a string. We assume it's a JSON string for structured outputs.
    // For safety, we try to parse it as JSON, but if it's not, we return the text.
    try {
      return JSON.parse(response);
    } catch (e) {
      // If not JSON, return the text response
      return response;
    }
  } catch (error) {
    console.error("Error in brain processing:", error);
    throw error;
  }
}