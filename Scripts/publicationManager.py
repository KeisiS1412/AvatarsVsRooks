from dotenv import load_dotenv
import os
import tweepy
import requests

load_dotenv()


class publicationManager:
    def __init__(self, scores):
        self.scores = scores
        self.image_url = "https://imgur.com/a/H5G7L7x"

        self.client = tweepy.Client(
            consumer_key=os.getenv("JRGxeogWq83cpOW3Tmn3SCijv"),
            consumer_secret=os.getenv("HUKQtID8sxo2UmWk4wpcCHuACf7wwTw7F3ax0LVIU3DFeUS3mN"),
            access_token=os.getenv("1988830542046064641-z51hp21R7epy032yddEkTJNEElZO7"),
            access_token_secret=os.getenv("YkTm2KiV1kiA1oEfWxcPnVIiHlVbU5OgFlvThTOUDYNbp")
        )

        self.ig_user_id = os.getenv("17841478254236978")
        self.ig_access_token = os.getenv("EAAWECzGhzwIBP7JzU9aeHVE5RntAFWUFtXrDx8L7QEpHiL2i9hpm9LZCYko2vCsK6qooMtT31WLvb449EWBf2tXjY7edwdaNQzLrscpHATOimfURmhJ9n57n8ih9C9y8bBaasAqA4zWFTY2kz188UgdWs8K4L7VgKvUEOkhMYDZAlczoEJxGNvyEuzJSb1")

    def twitterPost(self, message):
        try:
            resp = self.client.create_tweet(text=message)
            print(f"✅ Tweet publicado (ID: {resp.data['id']})")
        except Exception as e:
            print("❌ Error publicando en Twitter:", e)

    def instagramPost(self, caption):
        try:
            media_endpoint = f"https://graph.facebook.com/v17.0/{self.ig_user_id}/media"
            media_params = {
                "image_url": self.image_url,
                "caption": caption,
                "access_token": self.ig_access_token
            }
            media_response = requests.post(media_endpoint, data=media_params)
            media_data = media_response.json()

            if "id" not in media_data:
                print("❌ Error creando contenedor IG:", media_data)
                return

            creation_id = media_data["id"]
            print(f"📦 Contenedor IG creado: {creation_id}")

            publish_endpoint = f"https://graph.facebook.com/v17.0/{self.ig_user_id}/media_publish"
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.ig_access_token
            }
            publish_response = requests.post(publish_endpoint, data=publish_params)
            publish_data = publish_response.json()

            if "id" in publish_data:
                print(f"Publicado en Instagram (ID: {publish_data['id']})")
            else:
                print("Error al publicar IG:", publish_data)

        except Exception as e:
            print("Error general publicando en Instagram:", e)

    def leaderboardTemplate(self):
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        place_emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        message = "🏆 TOP 5 - Leaderboard Oficial 🏆\n\n"
        for i, (player, score) in enumerate(sorted_scores[:5]):
            message += f"{place_emojis[i]} {player} — {score} pts\n"
        message += "\n🔥 ¡Nuevo récord alcanzado!"
        return message

    def makePosts(self):
        message = self.leaderboardTemplate()
        print("🟦 Publicando en Twitter...")
        self.twitterPost(message)
        print("🟩 Publicando en Instagram...")
        self.instagramPost(message)
