import json

def check_counts(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        game_count = len(data)
        print(f"Toplam oyun sayısı: {game_count}")
        
        counts = {}
        for game, content in data.items():
            counts[game] = len(content.get('reviews', []))
        
        # Oyun bazında yorum sayıları
        for game, count in list(counts.items())[:10]: # İlk 10 oyunu göster
            print(f"- {game}: {count} yorum")
        
        if game_count > 10:
            print("...")
        
        # Özet istatistikler
        min_reviews = min(counts.values())
        max_reviews = max(counts.values())
        avg_reviews = sum(counts.values()) / game_count
        
        print(f"\nİstatistikler:")
        print(f"En az yorum: {min_reviews}")
        print(f"En çok yorum: {max_reviews}")
        print(f"Ortalama yorum: {avg_reviews:.2f}")
        
        # 100'den az olanlar
        less_than_100 = {g: c for g, c in counts.items() if c < 100}
        if less_than_100:
            print(f"\n100'den az yorumu olan oyunlar ({len(less_than_100)} adet):")
            for game, count in less_than_100.items():
                print(f"- {game}: {count} yorum")
        else:
            print("\nTüm oyunlar 100 veya daha fazla yoruma sahip.")

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    check_counts('raw_reviews.json')
