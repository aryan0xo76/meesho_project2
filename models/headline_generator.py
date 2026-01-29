import random
import asyncio

class HeadlineGenerator:
    def __init__(self):
        self.templates = {
            "tier2_fashion": ["✨ New Wedding Collection: Styles just for you!", "💃 Ethnic Wear Sale: Up to 60% Off Sarees"],
            "student_examprep": ["🎓 Exam Essentials: Everything you need to succeed!", "📝 Study Smart: Best deals on Stationery."],
            "budget_gadget": ["🔥 Tech Drop: Best Earbuds under ₹999", "⚡ Flash Sale: Mobile Accessories ending soon!"],
            "home_decor_festive": ["🪔 Light up your home this Diwali!", "🏠 Home Makeover: Festive prices are here."],
            "default": ["🌟 Special Offers Just for You!"]
        }

    def train(self, df_events):
        print("Headline Generator Ready")

    async def generate_headline(self, persona_dict):
        pid = persona_dict.get("id", "default")
        opts = self.templates.get(pid, self.templates["default"])
        await asyncio.sleep(0.1)
        return random.choice(opts)