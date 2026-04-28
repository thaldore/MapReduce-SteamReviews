import requests
import json
import time
import os

def get_steam_reviews(appid, game_name, max_reviews=100):
    url = f"https://store.steampowered.com/appreviews/{appid}"
    all_reviews = []
    cursor = "*"
    
    print(f"\n>>> {game_name} (AppID: {appid}) için yorumlar çekiliyor...")

    while len(all_reviews) < max_reviews:
        params = {
            "json": 1,
            "filter": "all",
            "language": "english",
            "review_type": "all",
            "purchase_type": "all",
            "num_per_page": 100,
            "cursor": cursor
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                print(f"Hata: API {response.status_code} koduyla döndü.")
                break
            
            data = response.json()
            
            if "reviews" in data and len(data["reviews"]) > 0:
                current_batch = data["reviews"]
                all_reviews.extend(current_batch)
                print(f"--- Toplam: {len(all_reviews)} yorum çekildi.")
            else:
                break

            new_cursor = data.get("cursor")
            if not new_cursor or new_cursor == cursor:
                break
            
            cursor = new_cursor
            time.sleep(0.5) # Kısa bir bekleme

        except Exception as e:
            print(f"Hata oluştu: {e}")
            break

    return all_reviews[:max_reviews]

# Popüler ve En İyi 100 Oyun Listesi
games_to_fetch = [
    {"id": "1086940", "name": "Baldur's Gate 3"},
    {"id": "1091500", "name": "Cyberpunk 2077"},
    {"id": "292030", "name": "The Witcher 3: Wild Hunt"},
    {"id": "1174180", "name": "Red Dead Redemption 2"},
    {"id": "1593500", "name": "God of War"},
    {"id": "2322010", "name": "God of War Ragnarök"},
    {"id": "261550", "name": "Mount & Blade II: Bannerlord"},
    {"id": "2694490", "name": "Path Exile 2"},
    {"id": "230410", "name": "Warframe"},
    {"id": "1245620", "name": "Elden Ring"},
    {"id": "2358720", "name": "Black Myth: Wukong"},
    {"id": "1145350", "name": "Hades II"},
    {"id": "582010", "name": "Monster Hunter: World"},
    {"id": "2246340", "name": "Monster Hunter Wilds"},
    {"id": "553850", "name": "Helldivers 2"},
    {"id": "730", "name": "Counter-Strike 2"},
    {"id": "570", "name": "DOTA 2"},
    {"id": "578080", "name": "PUBG: Battlegrounds"},
    {"id": "1172470", "name": "Apex Legends"},
    {"id": "1085660", "name": "Destiny 2"},
    {"id": "3405690", "name": "EA SPORTS FC 26"}, 
    {"id": "892970", "name": "Valheim"},
    {"id": "252490", "name": "Rust"},
    {"id": "346110", "name": "ARK: Survival Evolved"},
    {"id": "1903340", "name": "Clair Obscur: Expedition 33"}, 
    {"id": "1623730", "name": "Palworld"},
    {"id": "367520", "name": "Hollow Knight"},
    {"id": "1145360", "name": "Hades"},
    {"id": "814380", "name": "Sekiro: Shadows Die Twice"},
    {"id": "374320", "name": "Dark Souls III"},
    {"id": "570940", "name": "Dark Souls: Remastered"},
    {"id": "1627720", "name": "Lies of P"},
    {"id": "3321460", "name": "Crimson Desert"}, 
    {"id": "2095290", "name": "Wo Long: Fallen Dynasty"},
    {"id": "1774580", "name": "Star Wars Jedi: Survivor"},
    {"id": "1172380", "name": "Star Wars Jedi: Fallen Order"},
    {"id": "990080", "name": "Hogwarts Legacy"},
    {"id": "2561580", "name": "Horizon Zero Dawn Remastered"},
    {"id": "2420110", "name": "Horizon Forbidden West"},
    {"id": "2215430", "name": "Ghost of Tsushima"},
    {"id": "1888930", "name": "The Last of Us Part I"},
    {"id": "1817070", "name": "Spider-Man Remastered"},
    {"id": "1817190", "name": "Spider-Man: Miles Morales"},
    {"id": "2050650", "name": "Resident Evil 4"},
    {"id": "1196590", "name": "Resident Evil Village"},
    {"id": "883710", "name": "Resident Evil 2"},
    {"id": "2239550", "name": "Assassin's Creed Mirage"},
    {"id": "2208920", "name": "Assassin's Creed Valhalla"},
    {"id": "812140", "name": "Assassin's Creed Odyssey"},
    {"id": "1771300", "name": "Kingdom Come: Deliverance II"},
    {"id": "379430", "name": "Kingdom Come: Deliverance"},
    {"id": "1716740", "name": "Starfield"},
    {"id": "377160", "name": "Fallout 4"},
    {"id": "1151340", "name": "Fallout 76"},
    {"id": "489830", "name": "The Elder Scrolls V: Skyrim SE"},
    {"id": "2054970", "name": "Dragon's Dogma 2"},
    {"id": "2515020", "name": "Final Fantasy XVI"},
    {"id": "2909400", "name": "Final Fantasy VII Rebirth"},
    {"id": "39210", "name": "Final Fantasy XIV Online"},
    {"id": "2344520", "name": "Diablo IV"},
    {"id": "238960", "name": "Path of Exile"},
    {"id": "1599340", "name": "Lost Ark"},
    {"id": "1030840", "name": "Mafia: Definitive Edition"}, 
    {"id": "275850", "name": "No Man's Sky"},
    {"id": "264710", "name": "Subnautica"},
    {"id": "848450", "name": "Subnautica: Below Zero"},
    {"id": "242760", "name": "The Forest"},
    {"id": "1326470", "name": "Sons of the Forest"},
    {"id": "251570", "name": "7 Days to Die"},
    {"id": "813780", "name": "Age of Empires II: Definitive Edition"}, 
    {"id": "1172620", "name": "Sea of Thieves"},
    {"id": "1295660", "name": "Sid Meier's Civilization VII"}, 
    {"id": "594650", "name": "Hunt: Showdown 1896"},
    {"id": "1144200", "name": "Ready or Not"},
    {"id": "1426210", "name": "It Takes Two"}, 
    {"id": "1363080", "name": "Manor Lords"}, 
    {"id": "3017860", "name": "DOOM: The Dark Ages"}, 
    {"id": "550", "name": "Left 4 Dead 2"},
    {"id": "924970", "name": "Back 4 Blood"},
    {"id": "2406770", "name": "Metaphor: ReFantazio"}, 
    {"id": "227300", "name": "Euro Truck Simulator 2"}, 
    {"id": "620", "name": "Portal 2"}, 
    {"id": "3241660", "name": "R.E.P.O."},
    {"id": "2124490", "name": "Silent Hill 2"}, 
    {"id": "3164500", "name": "Schedule I"},
    {"id": "413150", "name": "Stardew Valley"},
    {"id": "105600", "name": "Terraria"},
    {"id": "294100", "name": "RimWorld"},
    {"id": "526870", "name": "Satisfactory"},
    {"id": "427520", "name": "Factorio"},
    {"id": "1845910", "name": "Dragon Age: The Veilguard"}, 
    {"id": "1868140", "name": "Dave the Diver"},
    {"id": "228280", "name": "Baldur's Gate: Enhanced Edition"},
    {"id": "435150", "name": "Divinity: Original Sin 2"},
    {"id": "560130", "name": "Pillars of Eternity II"},
    {"id": "632470", "name": "Disco Elysium"},
    {"id": "2933620", "name": "Call of Duty: Black Ops 6"}, 
    {"id": "2183900", "name": "Warhammer 40K: Space Marine 2"},
    {"id": "1643320", "name": "S.T.A.L.K.E.R. 2"},
    {"id": "1551360", "name": "Forza Horizon 5"}
]

def main():
    full_data = {}
    
    # max_reviews sayısını MapReduce için biraz artırabiliriz ama şimdilik kullanıcıya uyalım
    MAX_REVIEWS_PER_GAME = 1000 

    for game in games_to_fetch:
        reviews = get_steam_reviews(game["id"], game["name"], max_reviews=MAX_REVIEWS_PER_GAME)
        full_data[game["name"]] = {
            "appid": game["id"],
            "reviews": reviews
        }

    output_file = "raw_reviews.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(full_data, f, ensure_ascii=False, indent=4)

    print(f"\n!!! İşlem Tamamlandı. Veriler '{output_file}' dosyasına kaydedildi.")

if __name__ == "__main__":
    main()
