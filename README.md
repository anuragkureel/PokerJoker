# PokerJoker

Solver Analysis

how to run the OCR:
2 important files are there: image_crop_for_ocr_input.py & save_image_OCR_data_with_LLM.js

How does it work?
->image_crop_for_ocr_input.py takes an image input and breaks it into smaller cropped images with specific regions of interest. These are saved at the folder PokerJoker/imageDataForLLMPrompt

-> save_image_OCR_data_with_LLM.js file takes these cropped images as input and asks Gemini to read the input and save it to the folder PokerJoker/OCR_result.

-> If everything happend correctly, you should be able to see the results at PokerJoker/OCR_result/combined_results.json

How to run?
a scrip located at PokerJoker/runImageExtraction.sh – handles the complete logic of image crop and image OCR extraction.

requirements:

1. install nvm
2. install node 23.6.0
3. pip install opencv-python numpy
4. set the GOOGLE_API_KEY at .env file

after the requirements are installed, -->call the script: ./runImageExtraction.sh PokerJoker/test6.jpeg
