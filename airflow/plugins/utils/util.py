import re
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import psycopg2
from nltk.tokenize import word_tokenize
from gradio_client import Client
from psycopg2 import sql


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
    