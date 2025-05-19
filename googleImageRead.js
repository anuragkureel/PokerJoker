import { GoogleGenAI } from "@google/genai";
import * as fs from "node:fs";
import dotenv from "dotenv";

dotenv.config();

const apiKey = process.env.GOOGLE_API_KEY;

const ai = new GoogleGenAI({ apiKey });
const cardInfoImage = "/Users/trip/git/PokerJoker/test2.jpeg";
const playerInfoImage = "/Users/trip/git/PokerJoker/test1.jpeg";
const solver_results = "/Users/trip/git/PokerJoker/test4.png";
const base64ImageFile = fs.readFileSync(solver_results, {
  encoding: "base64",
});

const cardSchema = {
  value: "string", // "2-10, J, Q, K, A"
  type: "string", // "hearts", "diamonds", "clubs", "spades"
  description: "A playing card in a standard 52-card deck",
  properties: {
    value: {
      type: "string",
      enum: ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"],
      description: "The rank of the card",
    },
    type: {
      type: "string",
      enum: ["hearts", "diamonds", "clubs", "spades"],
      description: "The suit of the card",
    },
  },
};
const tableInfoSchema = {
  community_cards: {
    type: "array",
    items: cardSchema,
    description: "Community cards on the table (flop, turn, river)",
  },
  pot_size: {
    type: "number",
    description: "Total chips in play at the table in big blinds (BB)",
  },
  description: "Information about the current state of the poker table",
};
const playerInfoSchema = {
  properties: {
    playerName: {
      type: "string",
      description: "The username or name of the player",
    },
    playerPosition: {
      type: "string",
      enum: ["UTG", "MP", "CO", "BTN", "SB", "BB", "Sitting out"],
      description: "The position of the player at the table",
    },
    playerState: {
      type: "string",
      enum: [
        "Active",
        "Sitting out",
        "All-In",
        "Folded",
        "Waiting for BB",
        "Disconnected",
        "Time Bank",
      ],
      description: "Current state of the player in the game",
    },
    playerBet: {
      type: "string",
      description: "Current bet amount in BB",
    },
    stack: {
      type: "number",
      description: "Player's current chip stack in big blinds (BB)",
    },
  },
};
const data_schema_short = {
  tableInfo: tableInfoSchema,
  mainplayerInfo: playerInfoSchema,
  otherPlayerInfo: {
    type: "array",
    items: playerInfoSchema,
    description: "Information about other players at the table",
  },
};
const tableInfoPrompt = `you are an expert image analyser. You need to extract this image of a poker game, and output the data related to this schema: tableInfoSchema: ${tableInfoSchema}  inside the tableInfoSchema, cardSchema stands for: ${cardSchema}. Your output is tableInfoSchema object with, tableInfoSchema['community_cards']['items'] = array of cardSchema objects and tableInfoSchema['pot_size']=number`;
const mainplayerInfoPrompt = `you are an expert image analyser. You need to analyse the poker game image provided, and output the cards of the current player for this schema: ${cardSchema}. Output an array of card objects. `;
const otherPlayerInfoPropmt = `you are an expert image analyser. You need to analyse the poker game image provided, and extract the player related information. fit your response into this schema: playerInfoSchema: ${playerInfoSchema}. output should be a json `;
const solver_result_prompt = `you are an expert image analuyser. HEre you need to analyse the poker solver image, which is a grid of colored boxes. give me a list of boxes which has >50% of green color. Do not include boxes with less than 50% green. Your output must be a JSON`;
const contents = [
  {
    inlineData: {
      mimeType: "image/jpeg",
      data: base64ImageFile,
    },
  },
  { text: solver_result_prompt },
];

console.log("LLM input ", contents);
const response = await ai.models.generateContent({
  model: "gemini-2.0-flash",
  contents: contents,
});
try {
  // Try to parse the response text as JSON
  let cleanedResponse = response.text.replace(/```json\n|\n```/g, "");

  const jsonData = JSON.parse(cleanedResponse);

  // Write the JSON data to a file
  fs.writeFileSync(
    "/Users/trip/git/PokerJoker/tests2.json",
    JSON.stringify(jsonData, null, 2),
    "utf8"
  );

  console.log("Successfully saved response to tests.json");
} catch (parseError) {
  console.error("Error parsing response as JSON:", parseError);

  // If parsing fails, still save the raw text
  fs.writeFileSync(
    "/Users/trip/git/PokerJoker/tests1.json",
    response.text,
    "utf8"
  );

  console.log("Saved raw response text to tests.json (not valid JSON)");
}
console.log("here is the response of the LLM", response.text);
