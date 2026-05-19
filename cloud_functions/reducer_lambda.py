import json
import boto3
import os
from collections import Counter

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # BUCKET_NAME'i environment variable olarak alacağız
        BUCKET_NAME = os.environ['BUCKET_NAME']
        
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix='map-output/')
        
        if 'Contents' not in response:
            return {'statusCode': 404, 'body': 'map-output klasörü boş!'}

        json_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
        print(f"Toplam {len(json_files)} map sonucu okunacak...")

        global_words = Counter()
        games = []
        total_pos = 0
        total_neg = 0
        errors = 0

        for obj in json_files:
            key = obj['Key']
            try:
                file_obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
                res = json.loads(file_obj['Body'].read().decode('utf-8'))

                total_pos += res.get('pos', 0)
                total_neg += res.get('neg', 0)
                global_words.update(res.get('word_frequencies', {}))

                total = res.get('pos', 0) + res.get('neg', 0)
                ratio = (res['pos'] / total * 100) if total > 0 else 0

                games.append({
                    "name": res['game'],
                    "pos": res.get('pos', 0),
                    "neg": res.get('neg', 0),
                    "ratio": round(ratio, 2),
                    "top_words": dict(Counter(res.get('word_frequencies', {})).most_common(10))
                })
            except Exception as e:
                print(f"HATA ({key}): {str(e)}")
                errors += 1
                continue

        games.sort(key=lambda x: x['ratio'], reverse=True)

        final_results = {
            "stats": {
                "total_reviews": total_pos + total_neg,
                "total_pos": total_pos,
                "total_neg": total_neg,
                "game_count": len(games),
                "failed_maps": errors
            },
            "global_word_cloud": [{"text": k, "value": v} for k, v in global_words.most_common(200)],
            "games": games
        }

        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key='final-output/analysis_results.json',
            Body=json.dumps(final_results, ensure_ascii=False, indent=2),
            ContentType='application/json'
        )

        print(f"Reduce tamamlandı. {len(games)} oyun işlendi, {errors} hata.")
        return {'statusCode': 200, 'body': f"Tamamlandı: {len(games)} oyun, {errors} hata"}

    except Exception as e:
        print(f"KRİTİK HATA: {str(e)}")
        raise e
