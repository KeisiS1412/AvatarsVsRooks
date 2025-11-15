from dotenv import load_dotenv
import os
import tweepy

load_dotenv()

class publicationManager:
    def __init__(self, scores):
        self.scores = scores
        self.client = tweepy.Client(
            consumer_key=os.getenv("API_KEY"),
            consumer_secret=os.getenv("API_SECRET"),
            access_token=os.getenv("ACCESS_TOKEN"),
            access_token_secret=os.getenv("ACCESS_SECRET")
        )

    def twitterPost(self):
        try:
            resp = self.client.create_tweet(text=self.leaderboardTemplate())
        except Exception as e:
            print(e)

    def leaderboardTemplate(self):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        place_emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        message = "🏆 *TOP 5 - Leaderboard Oficial* 🏆\n\n"
        for i, (player, score) in enumerate(sorted_scores[:5]):
            message += f"{place_emojis[i]} {player} — {score} pts\n"
        message += "\n🔥 ¡Nuevo récord alcanzado!"
        return message
    
    def makePosts(self):
        self.twitterPost()
