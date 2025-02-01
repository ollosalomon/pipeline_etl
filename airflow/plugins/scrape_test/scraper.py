import os
from datetime import datetime
import polars as pl
from twikit import Client, TooManyRequests
from dotenv import load_dotenv
from random import randint
import asyncio
import time
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import psycopg2
from nltk.tokenize import word_tokenize
from gradio_client import Client as Gradio_client
from psycopg2 import sql
from psycopg2.extras import DictCursor


# Chargement des variables d'environnement
load_dotenv()
# os.chdir("airflow/plugins/")
MINIMUM_TWEETS = int(os.getenv('MINIMUM_TWEETS', 10))
QUERY = 'from:elonmusk lang:fr'

cookies_file = {
    "_twitter_sess": "BAh7CSIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADoPY3JlYXRlZF9hdGwrCOGuhquSAToMY3NyZl9p%250AZCIlOGZhODcwMDE0MzcxNzEwYWM3Zjk2N2VhNzA0NWYwNDg6B2lkIiU4ZjVh%250AYjgwNjRmM2NlMzIxYjNiM2RkZjQ0ODMzZGU0MA%253D%253D--ca697796b15c8bb7a992e33fb35658228c641214",
    "att": "1-oiD4A3V3rMsK4cgM4xfuF1IEmVZZ66340ahiWgzD",
    "auth_token": "45905e32577bd3eac097e36dbd6700fe07643a1e",
    "ct0": "4eb891e60d5aa2d797d72c569c869122",
    "guest_id": "v1%3A172945458275182349",
    "guest_id_ads": "v1%3A172945458275182349",
    "guest_id_marketing": "v1%3A172945458275182349",
    "kdt": "lDW1eu3M1zqOLG2rR7IxPjULKQ2eLtKdOQHsPt1H",
    "personalization_id": "\"v1_WJqxBj0FZVh6d6D+0moymQ==\"",
    "twid": "\"u=1500831330300530694\""
}


def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL"""
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host='host.docker.internal',
        port='5433'
    )



def create_tweets_table():
    """Crée la table tweets si elle n'existe pas"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        create_table_query = """
            CREATE TABLE IF NOT EXISTS tweets (
                tweet_count SERIAL PRIMARY KEY,
                username VARCHAR(255),
                text TEXT,
                created_at TIMESTAMP,
                retweets INTEGER,
                likes INTEGER
            )
        """
        cursor.execute(create_table_query)
        connection.commit()
    except Exception as e:
        print(f"Erreur lors de la création de la table: {e}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()

async def get_tweets_batch(client=None, next_batch=None):
    """Get a batch of tweets using the provided client or create a new one"""
    if client is None:
        client = Client(language='en-US')
        client.set_cookies(cookies_file)
        print(f'{datetime.now()} - New client initialized')
    
    try:
        if next_batch is None:
            tweets = await client.search_tweet(QUERY, product='Top')
        else:
            wait_time = randint(5, 10)
            print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
            await asyncio.sleep(wait_time)
            tweets = await next_batch.next()

        tweets_data = []
        for tweet in tweets:
            tweets_data.append({
                "username": tweet.user.name,
                "text": tweet.text,
                "created_at": tweet.created_at,
                "retweets": tweet.retweet_count,
                "likes": tweet.favorite_count
            })
        
        return tweets_data, tweets
    except Exception as e:
        print(f"Error getting tweets: {e}")
        return [], None

async def async_scrape_tweets():
    """Asynchronous function to scrape tweets"""
    try:
        tweet_count = 0
        all_tweets = []
        next_batch = None
        client = Client(language='en-US')
        client.set_cookies(cookies_file)

        while tweet_count < MINIMUM_TWEETS:
            try:
                tweets_data, next_batch = await get_tweets_batch(client, next_batch)
                
                if not tweets_data:
                    print(f'{datetime.now()} - No more tweets found')
                    break

                for tweet in tweets_data:
                    tweet_count += 1
                    tweet_data = {
                        "tweet_count": tweet_count,
                        **tweet
                    }
                    all_tweets.append(tweet_data)

                print(f'{datetime.now()} - Got {tweet_count} tweets')

            except TooManyRequests as e:
                rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
                print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
                wait_time = (rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        print(f'{datetime.now()} - Done! Got {tweet_count} tweets')
        return all_tweets
        
    except Exception as e:
        print(f"Error in async_scrape_tweets: {e}")
        raise

def insert_tweets_to_db(tweets_data):
    """Insère les tweets dans la base de données PostgreSQL"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        insert_query = """
            INSERT INTO tweets (username, text, created_at, retweets, likes)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for tweet in tweets_data:
            cursor.execute(insert_query, (
                tweet['username'],
                tweet['text'],
                tweet['created_at'],
                tweet['retweets'],
                tweet['likes']
            ))
        
        connection.commit()
        print(f"{len(tweets_data)} tweets have been inserted into the database.")
    except Exception as e:
        print(f"Error while inserting tweets into the database: {e}")
        raise
    finally:
        if connection:
            cursor.close()
            connection.close()

def scrape_tweets(**context):
    """Task to scrape tweets and store the results"""
    try:
        # Create new event loop and run the async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tweets = loop.run_until_complete(async_scrape_tweets())
        loop.close()
        
        # Push the results to XCom
        if tweets:
            context['task_instance'].xcom_push(key="tweets_data", value=tweets)
            return tweets
        return None
        
    except Exception as e:
        print(f"Error in scrape_tweets: {e}")
        raise

def save_tweets_to_db(**context):
    """Task to save tweets to PostgreSQL database"""
    try:
        tweets = context['task_instance'].xcom_pull(key="data_cleaned", task_ids="processing_tweets")
        if tweets:
            # Créer la table si elle n'existe pas
            create_tweets_table()
            # Insérer les tweets
            insert_tweets_to_db(tweets)
            print("Database save successful")
        else:
            print("No tweets to save to database")
    except Exception as e:
        print(f"Error in save_tweets_to_db: {e}")
        raise

def write_to_csv(**context):
    """Task to write the collected tweets to a CSV file"""
    try:
        tweets = context['task_instance'].xcom_pull(key="data_cleaned", task_ids="processing_tweets")
        if tweets:
            tweets_df = pl.DataFrame(tweets)
            tweets_df.write_csv('tweets.csv')
            print("CSV save successful")
        else:
            print("No tweets to save to CSV")
    except Exception as e:
        print(f"Error in write_to_csv: {e}")
        raise
    
def preprocessing_data(**context):

    """Task to save tweets to PostgreSQL database"""
    try:
        tweets = context['task_instance'].xcom_pull(key="tweets_data", task_ids="scrape_tweets")
        if tweets:
            data = pl.DataFrame(tweets)
            data_cleaned = data.with_columns(
                pl.col("Text").map_elements(clean_text).alias("Text")
            )
            context['task_instance'].xcom_push(key="data_cleaned", value=data_cleaned.to_dict())
            
        else:
            print("No tweets to preprocess")
    except Exception as e:
        print(f"Error preprocess: {e}")
        raise
    
    
    
########################################################################################

try:
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
except Exception as e:
    print(f"Erreur lors du chargement des ressources NLTK: {e}")
    raise
def clean_text(text):
    """
    Nettoie et pré-traite une phrase pour des tâches de NLP en utilisant nltk.
    
    Args:
    - text (str): La phrase à nettoyer.
    
    Returns:
    - str: La phrase nettoyée.
    """
    try:
        # Vérifier que l'entrée est une chaîne de caractères
        if not isinstance(text, str):
            raise ValueError("L'entrée doit être une chaîne de caractères")
            
        # Convertir en minuscules
        text = text.lower()
        
        # Suppression des URL et emails
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
        text = re.sub(r'\S+@\S+', '', text)
        
        # Suppression des chiffres
        text = re.sub(r'\d+', '', text)
        
        # Suppression de la ponctuation
        text = re.sub(r'[^\w\s]', '', text)
        
        # Tokenisation
        try:
            words = word_tokenize(text)
        except LookupError:
            print("Erreur de tokenisation, re-téléchargement des ressources...")
            nltk.download('punkt')
            words = word_tokenize(text)
        
        # Suppression des stopwords et lemmatisation
        cleaned_text = ' '.join([
            lemmatizer.lemmatize(word) 
            for word in words 
            if word not in stop_words and word.isalpha()
        ])
        
        return cleaned_text
    
    except Exception as e:
        print(f"Une erreur s'est produite lors du nettoyage du texte: {str(e)}")
        return text  # Retourner le texte original en cas d'erreur
    

############################################################# Service NLP ############################

def fetch_data_from_db(query="SELECT id, text FROM public.tweets;", *args):
    """
    Exécute une requête SQL et retourne les résultats.
    """
    connection = None
    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")
        raise
    finally:
        if connection:
            connection.close()

def insert_tweets_to_db_after_apply_service():
    """
    Retourne la requête SQL pour mettre à jour les tweets avec les résultats du service.
    """
    return """
        UPDATE public.tweets
        SET label = %s, probability = %s
        WHERE id = %s;
    """

def apply_services():
    """
    Applique un service de prédiction sur les tweets et met à jour la base de données.
    """
    connection = None
    try:
        # Récupérer les tweets depuis la base de données
        tweets = fetch_data_from_db()
        print(f"tweets: {tweets}")
        # Initialiser le client de prédiction
        client = Client("Ollosalomon/Sentiment_analysis")

        # Connexion pour mise à jour des résultats
        connection = get_db_connection()
        with connection.cursor() as cursor:
            for tweet in tweets:
                tweet_id, tweet_text = tweet['id'], tweet['text']
                
                # Appel au service de prédiction
                result = client.predict(
                    text=tweet_text,
                    api_name="/predict"
                )

                # Récupérer le label et la probabilité
                label = result.get('label', 'Unknown')
                probability = result.get('score', 0)
                print(f"label: {label}, probability: {probability}")

                # Préparer et exécuter la requête de mise à jour
                update_query = insert_tweets_to_db_after_apply_service()
                cursor.execute(update_query, (label, probability, tweet_id))

            # Valider les changements
            connection.commit()
    except Exception as e:
        print(f"Erreur lors de l'application des services : {e}")
        raise
    finally:
        if connection:
            connection.close()
