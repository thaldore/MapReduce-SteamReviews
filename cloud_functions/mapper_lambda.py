import json
import boto3
import re
from collections import Counter
import urllib.parse
import os

s3_client = boto3.client('s3')

STOP_WORDS = set([
    "the", "and", "a", "to", "of", "is", "it", "in", "i", "this", "that", "was", "for", "on", "with", "as", "are", "at", 
    "be", "by", "have", "not", "but", "you", "my", "if", "or", "an", "so", "up", "out", "can", "more", "about", "all", 
    "has", "can't", "don't", "get", "they", "there", "me", "some", "would", "will", "your", "from", "had", "been", 
    "one", "only", "much", "even", "when", "which", "do", "still", "also", "into", "than", "other", "then", "just",
    "game", "play", "played", "playing", "games", "really", "very", "much", "good", "great", "well", "think",
    "like", "best", "recommend", "time", "hours", "steam", "actually", "probably", "should", "could", "would",
    "many", "people", "bit", "way", "after", "before", "make", "made", "back", "ever", "never", "every",
    "lol", "hey", "guy", "guys", "even", "does", "doesn't", "did", "didn't", "know", "want", "got", "say"
])

def clean_text(text):
    if not text: return []
    words = re.findall(r'\b[a-z]{3,}\b', str(text).lower())
    return [w for w in words if w not in STOP_WORDS]

def lambda_handler(event, context):
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        
        print(f"İşleniyor: {key}")

        if not key.startswith('raw-reviews/') or not key.endswith('.json'):
            return {'statusCode': 200, 'body': 'Atlandı'}

        response = s3_client.get_object(Bucket=bucket, Key=key)
        game_data = json.loads(response['Body'].read().decode('utf-8'))
        
        game_name = list(game_data.keys())[0]
        reviews = game_data[game_name].get('reviews', [])

        if not reviews:
            print(f"Uyarı: {game_name} için yorum bulunamadı.")

        pos_count = 0
        neg_count = 0
        all_words = []

        for rev in reviews:
            if not isinstance(rev, dict): continue
            if rev.get('voted_up'): pos_count += 1
            else: neg_count += 1
            all_words.extend(clean_text(rev.get('review', '')))

        word_frequencies = dict(Counter(all_words).most_common(50))

        result = {
            "game": game_name,
            "pos": pos_count,
            "neg": neg_count,
            "word_frequencies": word_frequencies,
            "review_count": len(reviews)
        }

        filename = key.split('/')[-1].replace('.json', '_result.json')
        output_key = f"map-output/{filename}"

        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(result, ensure_ascii=False),
            ContentType='application/json'
        )

        print(f"Tamamlandı: {game_name} -> {output_key}")
        return {'statusCode': 200, 'body': f"OK: {game_name}"}

    except Exception as e:
        print(f"HATA: {str(e)}")
        raise e
