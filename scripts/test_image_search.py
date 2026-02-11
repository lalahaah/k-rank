import asyncio
import os
import sys
from dotenv import load_dotenv

# 스크립트 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
env_path = os.path.join(project_root, '.env')
load_dotenv(env_path)

sys.path.append(script_dir)
from scraper import get_amazon_image

async def test():
    test_products = [
        "Torriden Dive In Serum",
        "Round Lab Birch Juice Sunscreen",
        "Anua PDRN Capsule Serum",
        "Medicube Zero Pore Pad"
    ]
    
    for product in test_products:
        print(f"Testing: {product}")
        url = await get_amazon_image(product)
        print(f"Result URL: {url}\n")

if __name__ == "__main__":
    asyncio.run(test())
