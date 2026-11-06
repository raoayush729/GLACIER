import time
import ollama as ol
# model = qwen3:4b-instruct-2507-q4_K_M

# response = ol.generate(
#     model="qwen3:4b",
#     prompt="Hello Qwen, are you working?",
#     think=False
# )

# print(response.response)



# start = time.perf_counter()

# response = ol.chat(

#     model="qwen3:4b-instruct-2507-q4_K_M",
#     messages=[
#         {
#             "role": "user",
#             "content": "tell me something about python language"
#         }
#     ],
#     think=False
# )

# end = time.perf_counter()


# print("Answer:", response.message.content)
# print("Time taken:", end - start, "seconds")




# start = time.perf_counter()

# stream = ol.chat(
#     model="qwen3:4b-instruct-2507-q4_K_M",
#     messages=[
#         {
#             "role": "user",
#             "content": "tell me the summery of class 12 english chapter 1 cbse"
#         }
#     ],
#     think=False,
#     stream=True
# )

# for chunck in stream:          # chunck will contain every word that qwen thinking and writing 
#     print(chunck.message.content,end="",flush=True)     # end= "" means to Dont move to a new line after every chunk.
#                                                         # flush= true means show the text on the screen immediately rather than waiting for Python's output buffer to release it.



# end = time.perf_counter()
# print(f"\ntime takken: {end-start} seconds")






# import time
# import ollama

# model = "qwen3:4b-instruct-2507-q4_K_M"

# messages = [
#     {
#         "role": "user",
#         "content": "Reply with exactly: Hello."
#     }
# ]

# for run in range(1, 3):
#     start = time.perf_counter()

#     response = ollama.chat(
#         model=model,
#         messages=messages,
#         think=False,
#         stream=False,
#         options={"num_ctx": 8192}
#     )

#     elapsed = time.perf_counter() - start

#     print(f"\n--- Run {run} ---")
#     print("Response:", response.message.content)
#     print(f"Total time: {elapsed:.2f}s")
#     print(f"Model load: {response.load_duration / 1e9:.2f}s")
#     print(f"Prompt evaluation: {response.prompt_eval_duration / 1e9:.2f}s")
#     print(f"Generation: {response.eval_duration / 1e9:.2f}s")
















import os, time
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
for i in range(3):
    start = time.perf_counter()
    r = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="Reply with the single word: ok",
        config=types.GenerateContentConfig(max_output_tokens=20),
    )
    print(i + 1, round(time.perf_counter() - start, 2), "s ->", r.text)



import os, time, urllib.request
from google import genai
from google.genai import types

# 1) Plain connection speed to Google (should be well under 1 second)
start = time.perf_counter()
try:
    urllib.request.urlopen("https://generativelanguage.googleapis.com/", timeout=30)
except Exception:
    pass                      # an error page is fine, we only time the connection
print("network check:", round(time.perf_counter() - start, 2), "s")

# 2) The same tiny request on several models
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
for model in ["gemini-3.5-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash"]:
    for _ in range(2):
        start = time.perf_counter()
        try:
            r = client.models.generate_content(
                model=model,
                contents="Reply with the single word: ok",
                config=types.GenerateContentConfig(max_output_tokens=50),
            )
            thinking = getattr(r.usage_metadata, "thoughts_token_count", None)
            print(f"{model:24} {time.perf_counter() - start:5.2f} s  thinking tokens: {thinking}  -> {r.text!r}")
        except Exception as error:
            print(f"{model:24} FAILED: {str(error)[:120]}")