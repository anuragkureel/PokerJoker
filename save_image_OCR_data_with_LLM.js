import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const apiKey = process.env.GOOGLE_API_KEY;
const ai = new GoogleGenAI({ apiKey });
const cardInfoImage = "/Users/trip/git/PokerJoker/test2.jpeg";
const playerInfoImage = "/Users/trip/git/PokerJoker/test1.jpeg";
const solver_results = "/Users/trip/git/PokerJoker/test4.png";
const base64ImageFile = fs.readFileSync(solver_results, {
  encoding: "base64",
});
const MAX_RETRIES = 3;
// Zod schemas for validation
const CardSchema = z.object({
  cards: z.array(
    z.object({
      rank: z.enum([
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
        "A",
      ]),
      suit: z.enum(["hearts", "diamonds", "clubs", "spades"]),
    })
  ),
});
const TableInfoSchema = z.object({
  community_cards: z.array(
    z.object({
      rank: z.enum([
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
        "A",
      ]),
      suit: z.enum(["hearts", "diamonds", "clubs", "spades"]),
    })
  ),
  pot_size: z.number(),
});

const PlayerInfoSchema = z.object({
  players: z.array(
    z.object({
      playerName: z.string(),
      playerPosition: z.enum([
        "UTG",
        "MP",
        "CO",
        "BTN",
        "SB",
        "BB",
        "Sitting out",
      ]),
      playerState: z.enum([
        "Active",
        "Sitting out",
        "All-In",
        "Folded",
        "Waiting for BB",
        "Disconnected",
        "Time Bank",
      ]),
      playerBet: z.string().nullable(),
      stack: z.number(),
    })
  ),
});

//add following cases:
//1. main player card info
//2. table info
//3. other player info
const input_variables = [
  {
    type: "main_player_cards",
    prompt: `Analyze this poker game image and return a JSON object in this exact format:
    {
      "cards": [
        {
          "rank": "2-10, J, Q, K, or A",
          "suit": "hearts, diamonds, clubs, or spades"
        }
      ]
    }
    Return ONLY the JSON object, no other text or explanation.`,
    imageInputPath:
      "/Users/trip/git/PokerJoker/imageDataForLLMPrompt/crop/image_crop_mainplayer_cards.png",
    imageOutPath:
      "/Users/trip/git/PokerJoker/OCR_result/main_player_cards.json",
    outputSchema: CardSchema,
  },
  {
    type: "table_cards",
    prompt: `Analyze this poker game image and return a JSON object in this exact format:
    {
      "community_cards": [
        {
          "rank": "2-10, J, Q, K, or A",
          "suit": "hearts, diamonds, clubs, or spades"
        }
      ],
      "pot_size": number
    }
    Return ONLY the JSON object, no other text or explanation.`,
    imageInputPath:
      "/Users/trip/git/PokerJoker/imageDataForLLMPrompt/crop/image_crop_table_cards.png",
    imageOutPath: "/Users/trip/git/PokerJoker/OCR_result/table_cards.json",
    outputSchema: TableInfoSchema,
  },
  {
    type: "other_player_info",
    prompt: `Analyze this poker game image and return a JSON object in this exact format:
    {
      "players": [
        {
          "playerName": "string",
          "playerPosition": "UTG, MP, CO, BTN, SB, BB, or Sitting out",
          "playerState": "Active, Sitting out, All-In, Folded, Waiting for BB, Disconnected, or Time Bank",
          "playerBet": "string",
          "stack": number
        }
      ]
    }
    Return ONLY the JSON object, no other text or explanation.`,
    imageInputPath:
      "/Users/trip/git/PokerJoker/imageDataForLLMPrompt/crop/image_crop_table_info.png",
    imageOutPath:
      "/Users/trip/git/PokerJoker/OCR_result/other_player_info.json",
    outputSchema: PlayerInfoSchema,
  },
];

const SolverResultSchema = z.object({
  greenBoxes: z.array(
    z.object({
      x: z.number(),
      y: z.number(),
      greenPercentage: z.number().min(50),
    })
  ),
});

// Function to clean and parse LLM response
function cleanAndParseLLMResponse(response) {
  return response.replace(/```json\n|\n```/g, "");
}

// Function to validate response against schema
async function validateResponse(response, schema) {
  try {
    const cleanedResponse = cleanAndParseLLMResponse(response);
    console.log("cleanedResponse ", cleanedResponse);
    const parsedData = JSON.parse(cleanedResponse);
    return schema.parse(parsedData);
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("Schema validation error:", error.errors);
    } else {
      console.error("JSON parsing error:", error);
    }
    throw error;
  }
}

// Function to make API call with retries
async function makeAPICallWithRetry(prompt, schema, imageData, retryCount = 0) {
  try {
    const response = await ai.models.generateContent({
      model: "gemini-2.0-flash",
      contents: [
        {
          inlineData: {
            mimeType: "image/jpeg",
            data: imageData,
          },
        },
        { text: prompt },
      ],
    });
    console.log("response.text", response.text);
    const validatedData = await validateResponse(response.text, schema);
    return validatedData;
  } catch (error) {
    if (retryCount < MAX_RETRIES) {
      console.log(`Retry attempt ${retryCount + 1} of ${MAX_RETRIES}`);
      const modifiedPrompt =
        prompt +
        `{error while parsing response into the schema: ${error}, schema: ${schema}}`;
      return makeAPICallWithRetry(
        modifiedPrompt,
        schema,
        imageData,
        retryCount + 1
      );
    }
    throw new Error(`Failed after ${MAX_RETRIES} attempts: ${error.message}`);
  }
}

// Main function to process solver results
async function processInputVariable(inputVar) {
  try {
    // Read the image file for this specific input
    const imageData = fs.readFileSync(inputVar.imageInputPath, {
      encoding: "base64",
    });

    const result = await makeAPICallWithRetry(
      inputVar.prompt,
      inputVar.outputSchema,
      imageData
    );

    // Save the result to the specified output path
    fs.writeFileSync(
      inputVar.imageOutPath,
      JSON.stringify(result, null, 2),
      "utf8"
    );

    console.log(
      `Successfully processed ${inputVar.type} and saved to ${inputVar.imageOutPath}`
    );
    return result;
  } catch (error) {
    console.error(`Error processing ${inputVar.type}:`, error);
    throw error;
  }
}

// Main function to process all input variables
async function processSolverResults() {
  try {
    const results = {};

    // Process each input variable sequentially
    for (const inputVar of input_variables) {
      try {
        results[inputVar.type] = await processInputVariable(inputVar);
      } catch (error) {
        console.error(`Failed to process ${inputVar.type}:`, error);
        // Save error information
      }
    }

    // Save combined results
    fs.writeFileSync(
      "/Users/trip/git/PokerJoker/OCR_result/combined_results.json",
      JSON.stringify(results, null, 2),
      "utf8"
    );
    console.log("Successfully processed all inputs");
    return results;
  } catch (error) {
    console.error("Failed to process solver results:", error);
    throw error;
  }
}

// Example usage
async function main() {
  try {
    const result = await processSolverResults();
    console.log("Processed result:", result);
  } catch (error) {
    console.error("Main process failed:", error);
  }
}

main();
