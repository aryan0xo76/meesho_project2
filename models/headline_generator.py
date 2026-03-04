import random
import asyncio

class HeadlineGenerator:
    def __init__(self):
        print("Context-Aware NLG Engine Ready")

    def train(self, df_events=None):
        pass # rule-based, no train needed

    async def generate_headline(self, persona_id, top_product=None):
        if not top_product:
            return "🌟 Handpicked just for you! Check out today's top trends."

        prod_name = top_product.get("name", "item")
        price = top_product.get("price", 0)
        
        if persona_id == "student_examprep":
            hooks = [
                f"📚 Study break! Treat yourself to this {prod_name}.",
                f"🎓 Ace your prep with the right gear. {prod_name} is now just ₹{price}!",
                f"⚡ Late night studying? You might need this {prod_name}."
            ]
        elif persona_id == "budget_gadget":
            hooks = [
                f"📱 Tech drop! Upgrade your setup with the new {prod_name}.",
                f"⚡ Flash Deal: Get the {prod_name} for only ₹{price} today.",
                f"🎧 Smart tech, smarter price. Grab this {prod_name} before it's gone!"
            ]
        elif persona_id == "tier2_fashion":
            hooks = [
                f"👗 Trending right now! Upgrade your wardrobe with this {prod_name}.",
                f"✨ Look your best for less. {prod_name} is currently ₹{price}.",
                f"💃 Just arrived! We think you'll absolutely love this {prod_name}."
            ]
        elif persona_id == "home_decor_festive":
            hooks = [
                f"🏠 Make your space shine with this {prod_name}.",
                f"🪔 Festive special! Beautiful {prod_name} for just ₹{price}.",
                f"✨ Upgrade your living room instantly with this {prod_name}."
            ]
        else:
            hooks = [f"🌟 Top pick for you: {prod_name} at ₹{price}!"]

        return random.choice(hooks)