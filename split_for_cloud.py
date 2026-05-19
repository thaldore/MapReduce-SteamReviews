import json
import os
import re

# S3'e yüklemek için klasörleri oluştur
OUTPUT_DIR = 's3_ready/raw-reviews'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Veriler S3 için parçalanıyor...")

# Mevcut raw_reviews.json dosyasını oku
try:
    with open('raw_reviews.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("HATA: raw_reviews.json bulunamadı. Lütfen önce fetch_reviews.py dosyasını çalıştırın.")
    exit(1)
except json.JSONDecodeError:
    print("HATA: raw_reviews.json bozuk bir JSON dosyası.")
    exit(1)
except Exception as e:
    print(f"BEKLENMEYEN HATA: {str(e)}")
    exit(1)

count = 0
skipped = 0
used_names = set()

for game_name, content in data.items():
    # İçerik doğrulama
    if not isinstance(content, dict) or 'reviews' not in content:
        print(f"UYARI: '{game_name}' oyununda 'reviews' anahtarı yok, atlanıyor.")
        skipped += 1
        continue
        
    # Güvenli dosya adı oluşturma
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', game_name).lower()
    
    # İsim Çakışma (Collision) kontrolü (Örn: iki oyun da aynı safe_name'e denk gelirse)
    original_safe_name = safe_name
    counter = 1
    while safe_name in used_names:
        safe_name = f"{original_safe_name}_{counter}"
        counter += 1
        
    used_names.add(safe_name)
    file_path = os.path.join(OUTPUT_DIR, f"{safe_name}.json")
    
    game_data = {game_name: content}
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False)
        count += 1
    except PermissionError:
        print(f"HATA: {file_path} yazılamadı (İzin hatası).")
    except Exception as e:
        print(f"HATA ({game_name}): {str(e)}")
        
    # İlerleme göstergesi
    if count > 0 and count % 20 == 0:
        print(f"İşlenen oyun sayısı: {count}...")

print("-" * 30)
print(f"İŞLEM TAMAMLANDI!")
print(f"Başarıyla bölünen oyun: {count}")
print(f"Atlanan/Hatalı oyun: {skipped}")
print(f"Dosyalar hazır! AŞAMA 4'e geçip '{OUTPUT_DIR}' klasöründeki {count} dosyayı S3'e yükleyebilirsiniz.")
