import requests
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor
import json
import re

# Load model and processor only once
model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

# Sample data for testing
# SAMPLE_DATA = {
#     'aadhar': {
#         'name': 'John Doe',
#         'dob': '1990-05-15',
#         'gender': 'Male',
#         'aadhar': '1234 5678 9012'
#     },
#     'pan': {
#         'name': 'John Doe',
#         'pan': 'ABCDE1234F'
#     },
#     'marksheet': {
#         'semester': 'VI',
#         'rollNumber': 'CS2023001',
#         'cgpa': '8.75',
#         'sgpa': '9.0'
#     }
# }

# def extract_data(image_path: str, prompt: str) -> dict | None:
#     """
#     For testing purposes, this function returns sample data based on the document type.
#     In production, this would use the Llama model to extract data from the image.
#     """
#     try:
#         # Determine document type from the prompt
#         if 'Aadhaar Card' in prompt:
#             return SAMPLE_DATA['aadhar']
#         elif 'PAN Card' in prompt:
#             return SAMPLE_DATA['pan']
#         elif 'Marksheet' in prompt:
#             return SAMPLE_DATA['marksheet']
#         else:
#             return None
#     except Exception as e:
#         print("Error during extraction:", e)
#         return None

# Original implementation (commented out for now)
def extract_data(image_path: str, prompt: str) -> dict | None:
    try:
        # Load and process image
        image = Image.open(image_path).convert("RGB")

        # Create messages template
        messages = [
            {"role": "user", "content": [
                {"type": "image"},
                {"type": "text", "text": prompt}
            ]}
        ]

        # Process input
        input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
        inputs = processor(
            image,
            input_text,
            add_special_tokens=False,
            return_tensors="pt"
        ).to(model.device)

        # Generate output
        output = model.generate(**inputs, max_new_tokens=500)
        response_text = processor.decode(output[0])
        
        # Print response for testing
        # print("LLAMA Response:", response_text)

        # Extract JSON
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            json_output = json_match.group()
            try:
                return json.loads(json_output)
            except json.JSONDecodeError:
                print("Extracted text is not valid JSON:", json_output)
        else:
            print("No JSON found in the response.")
    except Exception as e:
        print("Error during extraction:", e)

    return None
