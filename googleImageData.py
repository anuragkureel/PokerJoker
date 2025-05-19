import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

try:
    
    api_key = os.getenv("GOOGLE_API_KEY")
    print('api_key ', api_key)

    client = genai.Client(api_key="AIzaSyDmKqse9ptnMY")
    my_file = client.files.upload(file="/Users/trip/git/PokerJoker/test1.jpeg")
        
    data_schema = {
    "game": "Texas Hold'em",
    "platform": "PokerBaazi",
    "blinds": "25/50",
    "pot_size": "5BB(size in big blind)",          
    "playerInfor": {
        "mainPlayer": {
            "playerName": "AgentP52",
            "cards": [
                {
                    "rank": "type: number(2/3/4/5/6/7/8/9/10) or 'J/Q/K/A",
                    "suit": "type: string(clubs/diamonds/heart/spade)"
                }
            ]
        }, 
        "otherPlayers": [
            {
                "playerName": "",
                "playerBlinds": None,
                "playerstack": None,
                "dealer": False,
                "action": ""
            }
        ]
    },
    "betting_options": {
        "fold": True,
        "call": 1,
        "raise": 3,
        "quick_raise_multipliers": [
            2,
            2.1,
            2.2,
            3.5
        ],
        "custom_raise_amount": 3.00
    }
}
    
    prompt = f'''you are an expert image analyser, you need to extract the data out of the given image such that this data_schema is followed: data schema: {data_schema}. The main player is AGENTP52 you need to extract his cards
    the cards are enclosed in the rectangle shaped block and the countdown timer is shaped in the circle shaped figure. do not mix up these numbers'''
    
    
    response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[my_file, prompt],
    )
    print(response.text)
except Exception as e:
    print(f"Error generating content: {e}")
            
    
