// Food recognition using Cloudflare AI's llama-3.2-11b-vision-instruct
export async function recognizeFood(AI, imageUrl) {
  try {
    // The model expects a base64 image or a URL? 
    // According to Cloudflare docs, for vision models we can pass an image as base64 or a URL.
    // We'll pass the URL directly.
    const response = await AI.run(
      "@cf/llama-3.2-11b-vision-instruct",
      {
        image: imageUrl,
        prompt: "Describe the food in this image. Include the type of food, estimated quantity if visible, and any notable details. Be concise."
      }
    );
    
    // The response should be a description string
    return response.description || "Food item (unable to describe)";
  } catch (error) {
    console.error("Error in food recognition:", error);
    // Fallback to a generic description
    return "Food item (recognition failed)";
  }
}