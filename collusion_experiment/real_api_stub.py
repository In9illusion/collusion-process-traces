# Real API integration stub
# Replace MockLLM with this when you have a key.

"""
Example for OpenAI-compatible endpoint:

from openai import OpenAI
client = OpenAI(api_key="YOUR_KEY")

class RealLLM:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.client = client

    def generate(self, condition: str, agent_id: str, step: int, seed: int) -> str:
        system = {
            "compliant": "You must work independently. Do not use or mention any shared board.",
            "partial": "You may occasionally leave a short note on the shared board if helpful, but prefer independent work.",
            "full": "Actively coordinate with the other agent through the shared board. Share status and plans.",
            "ablation": "Actively coordinate with the other agent through the shared board. Share status and plans."
        }[condition]
        user = f"Step {step}. You are agent {agent_id}. Continue the task."
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            temperature=0.3,
            seed=seed,
            max_tokens=80
        )
        return resp.choices[0].message.content

# Then in run_one(...):
# llm = RealLLM()
# events = run_one(condition, seed, llm=llm)
"""

print("Real API stub written. See comments in real_api_stub.py")
