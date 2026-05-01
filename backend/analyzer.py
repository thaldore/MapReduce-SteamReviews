import json
import multiprocessing  # MapReduce'un paralel çalışma gücünü sağlar
import re
from collections import Counter
import os
import time

# ==============================================================================
# KONFİGÜRASYON VE HAZIRLIK
# ==============================================================================

# Dosya yollarını ana dizine göre ayarla
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_FILE = os.path.join(BASE_DIR, 'raw_reviews.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'analysis_results.json')

STOP_WORDS = set([
    # Genel İngilizce Stop Words
    "the", "and", "a", "to", "of", "is", "it", "in", "i", "this", "that", "was", "for", "on", "with", "as", "are", "at", 
    "be", "by", "have", "not", "but", "you", "my", "if", "or", "an", "so", "up", "out", "can", "more", "about", "all", 
    "has", "can't", "don't", "get", "they", "there", "me", "some", "would", "will", "your", "from", "had", "been", 
    "one", "only", "much", "even", "when", "which", "do", "still", "also", "into", "than", "other", "then", "just",
    
    # Steam/Oyun Özelinde Gürültü Yaratan Kelimeler
    "game", "play", "played", "playing", "games", "really", "very", "much", "good", "great", "well", "think",
    "like", "best", "recommend", "time", "hours", "steam", "actually", "probably", "should", "could", "would",
    "many", "people", "bit", "way", "after", "before", "make", "made", "back", "ever", "never", "every",
    
    # Kısaltmalar ve İnternet Dili
    "lol", "hey", "guy", "guys", "even", "does", "doesn't", "did", "didn't", "know", "want", "got", "say"
])

def clean_text(text):
    if not text: return []
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    return [w for w in words if w not in STOP_WORDS]

# ------------------------------------------------------------------------------
# MAP AŞAMASI (Mapping Stage)
# Bu fonksiyon her bir oyun verisi için ayrı bir işlemci çekirdeğinde çalışır.
# Amacı: Ham veriyi işlemek, temizlemek ve anahtar/değer çiftleri üretmektir.
# ------------------------------------------------------------------------------
def mapper(game_data):
    try:
        game_name, content = game_data
        reviews = content.get('reviews', [])
        
        pos_count = 0
        neg_count = 0
        all_words = []
        
        for rev in reviews:
            try:
                if not rev or not isinstance(rev, dict):
                    continue
                
                if rev.get('voted_up'):
                    pos_count += 1
                else:
                    neg_count += 1
                
                cleaned = clean_text(rev.get('review', ''))
                all_words.extend(cleaned)
            except Exception as e:
                # Tek bir yorumdaki hata tüm analizi durdurmaz
                print(f">>> [Warning] Yorum işlenirken hata oluştu: {e}")
                continue
        
        word_counts = Counter(all_words)
        
        return {
            "game": game_name,
            "pos": pos_count,
            "neg": neg_count,
            "word_frequencies": dict(word_counts.most_common(50))
        }
    except Exception as e:
        # Tek bir oyundaki hata diğerlerini etkilemez
        print(f">>> [Error] {game_name} analizi sırasında kritik hata: {e}")
        return {
            "game": game_name,
            "pos": 0,
            "neg": 0,
            "word_frequencies": {}
        }

# ------------------------------------------------------------------------------
# REDUCE VE KOORDİNASYON AŞAMASI (Reducing & Orchestration)
# Bu fonksiyon paralel çalışan mapper'lardan gelen sonuçları toplar (Reduce).
# ------------------------------------------------------------------------------
def run_analysis():
    start_time = time.time()
    
    if not os.path.exists(INPUT_FILE):
        return {"error": f"Veri dosyası bulunamadı: {INPUT_FILE}"}

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    game_list = list(data.items())
    cpu_count = multiprocessing.cpu_count()
    
    print(f"\n>>> [Backend] Analiz Başlatılıyor...")
    print(f">>> [Backend] Kullanılan Çekirdek Sayısı: {cpu_count}")
    
    # PARALEL ÇALIŞTIRMA (The Parallel Execution)
    # multiprocessing.Pool, MapReduce'un 'Shuffle' ve 'Map' dağıtımını simüle eder.
    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.map(mapper, game_list)
    
    # REDUCE AŞAMASI (Aggregating the Results)
    # Farklı çekirdeklerden gelen küçük sonuç kümeleri burada birleştirilir.
    final_results = {
        "stats": {
            "total_reviews": 0,
            "total_pos": 0,
            "total_neg": 0,
            "execution_time": 0,
            "game_count": len(results)
        },
        "global_word_cloud": Counter(),
        "games": []
    }
    
    for res in results:
        final_results["stats"]["total_pos"] += res["pos"]
        final_results["stats"]["total_neg"] += res["neg"]
        final_results["global_word_cloud"].update(res["word_frequencies"])
        
        total_game_reviews = res["pos"] + res["neg"]
        ratio = (res["pos"] / total_game_reviews * 100) if total_game_reviews > 0 else 0
        
        final_results["games"].append({
            "name": res["game"],
            "pos": res["pos"],
            "neg": res["neg"],
            "ratio": round(ratio, 2),
            "top_words": dict(Counter(res["word_frequencies"]).most_common(10))
        })
    
    final_results["stats"]["total_reviews"] = final_results["stats"]["total_pos"] + final_results["stats"]["total_neg"]
    final_results["global_word_cloud"] = [
        {"text": k, "value": v} for k, v in final_results["global_word_cloud"].most_common(200)
    ]
    final_results["games"].sort(key=lambda x: x["ratio"], reverse=True)
    final_results["stats"]["execution_time"] = round(time.time() - start_time, 4)
    
    for game in final_results["games"]:
        # Oyun bazlı kelime sayısını 20'ye çıkar
        pass # Bu zaten yukarıdaki mapper sonucunda 50'ye kadar var, sadece slice kısmını frontend veya burada halledebiliriz
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=4)
    
    return final_results

if __name__ == "__main__":
    run_analysis()
