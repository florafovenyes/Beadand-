import json
import csv
from pathlib import Path
from datetime import datetime

class KonyvNyilvantarto: #A könyvnyilvántartó osztály létrehozása
    def __init__(self, filename="konyvek.json"): #Konstruktor függvény, automatikusan lefut objektum létrehozásakor #SELF objektum saját adatait tárolja
        self.filename = filename #Eltároljuk a fájl nevét az objektumban
        self.konyvek = self.betoltes() #Meghívom a betöltés függvényt, visszaadja a könyvek listáját

    def betoltes(self): #Könyvek betöltése soronként
        """Könyvek betöltése fájlból és típusok normalizálása"""
        adatok = [] #Üres lista létrehozáse
        if Path(self.filename).exists(): #Létezik-e a fájl #True/False
            try: #Kezeljük a hibákat
                with open(self.filename, "r", encoding="utf-8") as f: #Megnyitja a fájlt olvasásra, a fált az f változóba teszi
                    if self.filename.endswith(".json"): #A fájl .json végződésű-e
                        adatok = json.load(f) or [] #Beolvassa a JSON fájlt
                    elif self.filename.endswith(".csv"): #A fájl .csv végződésű-e
                        reader = csv.DictReader(f)
                        adatok = list(reader) or [] #A readert listává alakítjuk
            except Exception as e: #Hibakezelés
                print(f" Hiba a betöltéskor: {e}") #Kiírjuk a hiba szövegét

        # Normalizálás: id -> int (ha lehetséges), opcionálisan konvertálhatunk más mezőket is
        for adatbank in adatok:
            if 'id' in adatbank: #Van-e id mező a szótárban
                try:
                    adatbank['id'] = int(adatbank['id']) #Átkonvertálja az id-t számmá
                except Exception:
                    # ha nem konvertálható (pl. üres), hagyjuk az eredetit
                    pass
            if 'oldalszám' in adatbank: #van-e oldalszám mező
                try:
                    adatbank['oldalszám'] = int(adatbank['oldalszám']) #oldalszám konvertálása egész számmá
                except Exception:
                    # ha nem konvertálható, hagyjuk stringként
                    pass
            if 'kiadás_éve' in adatbank: #Létezik-e kiadás éve
                try:
                    adatbank['kiadás_éve'] = int(adatbank['kiadás_éve']) #A kiadás éve intté konvertálása
                except Exception:
                    pass

        return adatok #Visszaadja a feldolgozott adatokat

    def _get_konyv_by_id(self, id_value): #Megkeresi a könyvet, amelyiknek az id-je az, amit beírtunk #Self aktuális objektum, id_value: keresett id
        """Visszaadja a konyv dict-et az id alapján; kezeli az id string/int különbségeket"""
        try:
            target = int(id_value) #Számmá alakítjuk az id-t
        except Exception:
            return None #Ha nem konvertálható, visszatérünk Nincs találattal
        for k in self.konyvek: #Végigmegy az összes könyvön
            try: #A könyv id-ja hibás is lehet
                if int(k.get('id', -1)) == target: #Lekéri az ID-t a szótárból, ez a keresett könyv?
                    return k #Ha megtalálta, visszaadja az egész könyvet
            except Exception: #Ha hibás az id, nem omlik össze a program
                continue #Menjen tovább
        return None #Ha egyetlen könyv sem egyezik meg, nincs találat

    def _next_id(self):
        """Következő egyedi ID (max meglévő + 1)"""
        if not self.konyvek: #Ha nincs még egyetlen könyv sem
            return 1
        idk = [] #Lista az Id-k tárolására
        for k in self.konyvek: #végigmegyünk az összes könyvön
            try:
                idk.append(int(k.get('id', 0))) #id lekérdezése és a listához adása
            except Exception: #hibás Id esetén átugorjuk
                continue
        return max(idk) + 1 if idk else 1 #Legnagyobb id+1, ha nincs id, akkor 1


    def mentes(self):
        """Könyvek mentése fájlba"""
        try:
            if self.filename.endswith(".json"): #.json mentése
                with open(self.filename, "w", encoding="utf-8") as f: #Fájl megnyitása írásra
                    json.dump(self.konyvek, f, indent=2, ensure_ascii=False) #Könyvek mentése json formátumba
            elif self.filename.endswith(".csv"): #csv mentése
                if not self.konyvek: #Ha nincsen egyetlen könyv sem
                    with open(self.filename, "w", newline="", encoding="utf-8-sig") as f:
                        f.write("")  # üres fájl létrehozása
                    print(f"Mentve: {self.filename}")
                    return

                # Oszlopok meghatározása
                fieldnames = list(self.konyvek[0].keys()) #csv oszlopnevei
                with open(self.filename, "w", newline="", encoding="utf-8-sig") as f: #csv megnyitása
                    writer = csv.DictWriter(f, fieldnames=fieldnames) #csv író létrehozása
                    writer.writeheader() #fejléc kiírása
                    for row in self.konyvek: #könyvek kiírása
                        out = {k: row.get(k, "") for k in fieldnames} #biztosítjuk, hogy minden mező létezzen
                        writer.writerow(out) #sor kiírása
            print(f"Mentve: {self.filename}")
        except Exception as e:
            print(f" Hiba a mentéskor: {e}") #hibakezelés

    def uj_konyv_felvetele(self):
        """Új könyv felvétele"""
        print("\n ÚJ KÖNYV FELVÉTELE")

        #Adatok bekérése
        cim = input("Cím: ").strip()
        szerzo = input("Szerző: ").strip()
        isbn = input("ISBN: ").strip()
        kiad_eve = input("Kiadás éve: ").strip()
        oldalszam = input("Oldalszám: ").strip()

        #státusz kiválasztása
        print("\nStátusz opciók:")
        print("1 - Kölcsönözhető")
        print("2 - Nem kölcsönözhető")
        print("3 - Éppen kölcsönzött")
        #Felhasználó választása
        statusz_valaszto = input("Választás (1-3): ").strip()

        status_map = { #szótár a státuszokhoz
            "1": "Kölcsönözhető",
            "2": "Nem kölcsönözhető",
            "3": "Éppen kölcsönzött"
        }
        #
        #A választott státuszt lekérjük, ha hibás, akkor alapértelmezett státusza: kölcsönözhető
        status = status_map.get(statusz_valaszto, "Kölcsönözhető")

        kolcsonozte = input("Ki kölcsönözte ki? (üres, ha senki): ").strip() or "-" #Kölcsönözhetőség megadása, ha üres, akkor "-" lesz a státusz

        #Egy könyv minden adatát egyben tároló szótár
        konyv = {
            "id": self._next_id(),
            "cím": cim,
            "szerző": szerzo,
            "isbn": isbn,
            "kiadás_éve": kiad_eve,
            "oldalszám": oldalszam,
            "státusz": status,
            "kölcsönzötted": kolcsonozte,
            "hozzáadva": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        self.konyvek.append(konyv) #hozzáadja az új könyvet listához        self.mentes()
        self.mentes() #mentés a fájlba
        print(" Könyv hozzáadva!")

    def lista_megjelenites(self):
        """Összes könyv listázása"""
        if not self.konyvek: #ha nincs egy könyv sem
            print("\n A nyilvántartás üres!")
            return

        print(f"\n KÖNYVNYILVÁNTARTÁS ({len(self.konyvek)} könyv)") #megszámolja a könyveket

        for konyv in self.konyvek: #végigmegy az összes könyvön
            self._konyv_megjelenitese(konyv)

    def _konyv_megjelenitese(self, konyv):
        """Egyetlen könyv megjelenítése"""
        print(f"ID: {konyv.get('id', '')} | Cím: {konyv.get('cím', '')}") #id és cím kiírása
        print(f"  Szerző: {konyv.get('szerző', '')} | ISBN: {konyv.get('isbn', '')}") #szerző és isbn kiírása
        print(f"  Kiadás éve: {konyv.get('kiadás_éve', '')} | Oldalszám: {konyv.get('oldalszám', '')}") #kiadás éve és oldalszám kiírása
        print(f"  Státusz: {konyv.get('státusz', '')}") #Státusz kiírása
        if konyv.get('kölcsönzötted', '-') != "-": #Ha van kölcsönző akkor kiírjuk
            print(f"  Kölcsönzötte: {konyv.get('kölcsönzötted', '')}")

    def keres(self):
        """Könyv keresése"""
        print("\n KÖNYV KERESÉSE")
        print("1 - Cím alapján")
        print("2 - Szerző alapján")
        print("3 - ISBN alapján")

        #Felhasználói választás
        choice = input("Választás (1-3): ").strip()
        #keresett szöveg kisbetűsítése
        keresoszoveg = input("Keresési szöveg: ").strip().lower()

        #találatok listázása
        eredmenyek = []

        #Keresés cím alapján
        if choice == "1":
            eredmenyek = [k for k in self.konyvek if keresoszoveg in str(k.get('cím', '')).lower()]
        #Keresés szerző alapján
        elif choice == "2":
            eredmenyek = [k for k in self.konyvek if keresoszoveg in str(k.get('szerző', '')).lower()]
        #Keresés ISBN alapján
        elif choice == "3":
            eredmenyek = [k for k in self.konyvek if keresoszoveg in str(k.get('isbn', '')).lower()]

        #Ha nincs találat
        if not eredmenyek:
            print(" Nincs találat!")
        #Ha van találat
        else:
            print(f"\n {len(eredmenyek)} találat:")
            for konyv in eredmenyek:
                self._konyv_megjelenitese(konyv)  #kiírja az összes találatot

    def modositas(self):
        """Könyv módosítása"""
        print("\n KÖNYV MÓDOSÍTÁSA")
        #könyv keresése id alapján
        konyv_id_input = input("Könyv ID-ja: ").strip()
        konyv = self._get_konyv_by_id(konyv_id_input)

        if not konyv: #ha nincs ilyen könyv
            print("Könyv nem található!")
            return

        print(f"\nJelenlegi adatok:")
        self._konyv_megjelenitese(konyv)

        print("\nMódosítandó mezők (üres = nincs módosítás):")

        #Adatok módosítása
        cim = input(f"Cím [{konyv.get('cím', '')}]: ").strip() or konyv.get('cím', '')
        szerzo = input(f"Szerző [{konyv.get('szerző', '')}]: ").strip() or konyv.get('szerző', '')
        status = input(f"Státusz [{konyv.get('státusz', '')}]: ").strip() or konyv.get('státusz', '')
        kolcsonzottes = input(f"Kölcsönzötte [{konyv.get('kölcsönzötted', '-') }]: ").strip() or konyv.get('kölcsönzötted', '-')

        #Adatok frissítése a könyv szótárban
        konyv['cím'] = cim
        konyv['szerző'] = szerzo
        konyv['státusz'] = status
        konyv['kölcsönzötted'] = kolcsonzottes

        self.mentes() #mentés a fájlba
        print(" Módosítva!")

    def torlodes(self):
        """Könyv törlése"""
        print("\n KÖNYV TÖRLÉSE")

        konyv_id_input = input("Törlendő könyv ID-ja: ").strip()
        konyv = self._get_konyv_by_id(konyv_id_input)

        if not konyv:
            print("Könyv nem található!")
            return

        self._konyv_megjelenitese(konyv)

        megerosites = input("\nBiztosan törölni szeretnéd? (i/n): ").strip().lower()
        if megerosites == "i":
            try:
                self.konyvek.remove(konyv)
                self.mentes()
                print(" Könyv törölve!")
            except ValueError:
                print(" Hiba: a könyv eltávolítása sikertelen.")
        else:
            print("Törlés lemondva.")

    def statisztika(self):
        """Nyilvántartás statisztikái"""
        if not self.konyvek:
            print("\n A nyilvántartás üres!")
            return

        print("\n STATISZTIKA")

        print(f"Összes könyv: {len(self.konyvek)}")

        kolcsonozhetok = len([k for k in self.konyvek if k.get('státusz') == "Kölcsönözhető"])
        kölcsönzött = len([k for k in self.konyvek if k.get('státusz') == "Éppen kölcsönzött"])
        nem_kolcsonozhetok = len([k for k in self.konyvek if k.get('státusz') == "Nem kölcsönözhető"])

        print(f"Kölcsönözhető: {kolcsonozhetok}")
        print(f"Éppen kölcsönzött: {kölcsönzött}")
        print(f"Nem kölcsönözhető: {nem_kolcsonozhetok}")

def main():
    """Fő program"""
    print("\n KÖNYVNYILVÁNTARTÓ PROGRAM")

    fajltipus = input("Fájl típusa (json/csv) [json]: ").strip().lower() or "json"
    filename = f"konyvek.{fajltipus}"

    nyilvantarto = KonyvNyilvantarto(filename)

    while True:
        print("\n FŐMENÜ")
        print("1 - Új könyv felvétele")
        print("2 - Összes könyv listázása")
        print("3 - Könyv keresése")
        print("4 - Könyv módosítása")
        print("5 - Könyv törlése")
        print("6 - Statisztika")
        print("7 - Kilépés")

        choice = input("\n Választás (1-7): ").strip()

        if choice == "1":
            nyilvantarto.uj_konyv_felvetele()
        elif choice == "2":
            nyilvantarto.lista_megjelenites()
        elif choice == "3":
            nyilvantarto.keres()
        elif choice == "4":
            nyilvantarto.modositas()
        elif choice == "5":
            nyilvantarto.torlodes()
        elif choice == "6":
            nyilvantarto.statisztika()
        elif choice == "7":
            print("\n Viszlát!")
            break
        else:
            print("Érvénytelen választás!")

if __name__ == "__main__":
    main()