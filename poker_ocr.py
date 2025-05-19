
# pylint: disable=all
import cv2
import pytesseract
import requests
import numpy as np
from PIL import Image
import pyautogui
import logging
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import json
from pathlib import Path
import time

# Configuration
@dataclass
class Config:
    API_ENDPOINT: str = "http://your-api.com/endpoint"
    DEBUG_MODE: bool = True
    TESSERACT_PATH: str = "/opt/homebrew/bin/tesseract"  # Updated for MacOS
    SCREENSHOT_INTERVAL: float = 1.0
    REGIONS_OF_INTEREST: Dict[str, tuple] = field(default_factory=lambda: {
        'player_name': (100, 130, 50, 200),
        'cards': (280, 330, 280, 330),
    })

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG_MODE else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class GameState:
    player_name: str = ""
    stack_size: str = ""
    pot_size: str = ""
    action: str = ""
    cards: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

class ImageProcessor:
    @staticmethod
    def capture_screenshot(path: Optional[str] = None) -> Optional[np.ndarray]:
        """
        Captures image either from a file path or screen.
        
        Args:
            path: Optional path to image file. If None, captures screen.
        
        Returns:
            numpy.ndarray: The image as a BGR numpy array, or None if failed.
        """
        try:
            if path:
                # Read from file
                image = cv2.imread(path)
                if image is None:
                    logger.error(f"Failed to load image from path: {path}")
                    return None
                return image
            else:
                # Capture screen
                screenshot = pyautogui.screenshot()
                numpy_image = np.array(screenshot)
                return cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        except Exception as e:
            logger.error(f"Image capture failed: {e}")
            return None
        
    @staticmethod
    def preprocess_image(image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        denoised = cv2.fastNlMeansDenoising(thresh)
        return denoised

    @staticmethod
    def extract_text_from_roi(image: np.ndarray, roi: tuple, config: str = '--psm 7') -> str:
        try:
            y1, y2, x1, x2 = roi
            roi_image = image[y1:y2, x1:x2]
            return pytesseract.image_to_string(roi_image, config=config).strip()
        except Exception as e:
            logger.error(f"ROI extraction failed: {e}")
            return ""

class PokerStateAnalyzer:
    def __init__(self, config: Config):
        self.config = config
        if Path(config.TESSERACT_PATH).exists():
            pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

    def parse_game_state(self, image: np.ndarray) -> GameState:
        try:
            processed_image = ImageProcessor.preprocess_image(image)
            if self.config.DEBUG_MODE:
                Path("debug").mkdir(exist_ok=True)
                cv2.imwrite("debug/processed.png", processed_image)

            game_state = GameState()
            
            # Extract text from defined regions
            for region_name, roi in self.config.REGIONS_OF_INTEREST.items():
                text = ImageProcessor.extract_text_from_roi(processed_image, roi)
                setattr(game_state, region_name, text)

            # Parse full image for additional information
            full_text = pytesseract.image_to_string(processed_image)
            self._parse_additional_info(full_text, game_state)

            return game_state

        except Exception as e:
            logger.error(f"Error parsing game state: {e}")
            return GameState()

    def _parse_additional_info(self, text: str, game_state: GameState) -> None:
        for line in text.split('\n'):
            line = line.strip()
            if "Pot" in line:
                game_state.pot_size = line.split("Pot")[1].strip()
            elif any(action in line for action in ["Raise", "Call", "Fold"]):
                game_state.action = line.strip()
            elif "BB" in line and "Pot" not in line:
                game_state.stack_size = next(
                    (part for part in line.split() if "BB" in part), 
                    ""
                )

class APIClient:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session = requests.Session()

    def send_game_state(self, game_state: GameState) -> Optional[dict]:
        """Sends game state to API synchronously."""
        print('game state recieved by the API funciton ' + game_state)
        return 1
        # try:
        #     response = self.session.post(
        #         self.endpoint, 
        #         json=game_state.to_dict(),
        #         timeout=5.0
        #     )
        #     response.raise_for_status()
        #     return response.json()
        # except Exception as e:
        #     logger.error(f"API request failed: {e}")
        #     return None

def main():
    config = Config()
    analyzer = PokerStateAnalyzer(config)
    api_client = APIClient()

    logger.info("Starting poker state analyzer...")
    
    try:
        while True:
            path = '/Users/trip/git/PokerJoker/test1.jpeg'
            screenshot = ImageProcessor.capture_screenshot(path)
            if screenshot is None:
                logger.warning("Failed to capture screenshot, retrying...")
                time.sleep(config.SCREENSHOT_INTERVAL)
                continue

            game_state = analyzer.parse_game_state(screenshot)
            logger.info(f"Parsed game state: {game_state}")

            if config.DEBUG_MODE:
                Path("debug").mkdir(exist_ok=True)
                with open("debug/game_state.json", "w") as f:
                    json.dump(game_state.to_dict(), f, indent=4)

            # Send to API and handle response
            response = api_client.send_game_state(game_state)
            if response:
                logger.info(f"API Response: {response}")

            time.sleep(config.SCREENSHOT_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {e}")
    finally:
        api_client.session.close()
        logger.info("Cleanup complete")

if __name__ == "__main__":
    main()