# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import requests
from datetime import datetime, timedelta
import time



api_key = "d7ad9abf5c584548a9bc70ede0497dfd"
api_key_altin = "goldapi-4vu9lsm6y4j4r0-io"



def veri_al():
    print("Finansal Planlama ve Yatırım Analiz Aracı")
    gelir = float(input("Aylık geliriniz (TL): "))
    gider = float(input("Aylık giderleriniz (TL): "))
    yatırım_tercihi = input("Yatırım tercihiniz (Ör: Döviz, Altın): ")
    
    finansal_veriler = {
        "gelir": gelir,
        "gider": gider,
        "yatırım_tercihi": yatırım_tercihi
    }
    
    print("\nVerileriniz başarıyla alındı!")
    return finansal_veriler

def risk_seviyesi_belirle(gelir, gider, enflasyon, doviz_degisim):
    # Tasarruf oranı hesaplaması
    tasarruf_orani = ((gelir - gider) / gelir) * 100

    # Temel risk seviyesi belirlemesi: tasarruf oranına göre
    if tasarruf_orani > 30:
        risk_seviyesi = "Düşük Risk"
        oneriler = ["Vadeli Mevduat", "Devlet Tahvili", "Altın"]
    elif 10 <= tasarruf_orani <= 30:
        risk_seviyesi = "Orta Risk"
        oneriler = ["Döviz", "Altın"]
    else:
        risk_seviyesi = "Yüksek Risk"
        oneriler = ["Öncelikle bütçenizi dengeleyin."]

    # Enflasyon etkisinin yatırım önerilerine yansıtılması
    if enflasyon > 30:
        oneriler = [o for o in oneriler if o != "Vadeli Mevduat"]
        oneriler.append("Altın")
    elif enflasyon > 15:
        oneriler.append("Döviz")

    # Döviz değişim oranı yüksekse, döviz önerisini kaldırmak
    if doviz_degisim > 5:
        oneriler = [o for o in oneriler if o != "Döviz"]

    return risk_seviyesi, oneriler


veriler = veri_al()
print("Finansal Veriler:", veriler)

def doviz_verilerini_cek(api_key):
    url = f"https://openexchangerates.org/api/latest.json?app_id={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["rates"]
    except requests.exceptions.RequestException as e:
        print("API'den veri çekerken bir hata oluştu:", e)
        return None
    
def altin_fiyatlarini_cek(api_key_altin):
    url = "https://www.goldapi.io/api/XAU/USD"

    headers = {
        "x-access-token": api_key_altin,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Altın fiyatlarını çekme
        gram_altin_buy = data.get("price", None)  # Ons fiyatı USD cinsinden
        gram_altin_sell = gram_altin_buy  # Satış fiyatı için ek veri yoksa aynı değeri kullan

        if gram_altin_buy:
            gram_altin_buy /= 31.1035  # Ons'u gram altına çevirme
            gram_altin_sell /= 31.1035

        return gram_altin_buy, gram_altin_sell

    except requests.exceptions.RequestException as e:
        print(f"API Hatası: {e}")
        return None, None



gram_altin_buy, gram_altin_sell = altin_fiyatlarini_cek(api_key_altin)

if gram_altin_buy and gram_altin_sell:
    print(f"💰 Güncel Gram Altın Alış Fiyatı: {gram_altin_buy:.2f} USD")
    print(f"💰 Güncel Gram Altın Satış Fiyatı: {gram_altin_sell:.2f} USD")
else:
    print("❌ Güncel altın fiyatları alınamadı.")

def gecmis_altin_verilerini_cek(api_key_altin, gun_sayisi=10):
    try:
        gun_sayisi = int(gun_sayisi)  # Eğer string gelirse integer'a çevir
    except ValueError:
        print("❌ Hata: gun_sayisi bir tam sayı olmalıdır!")
        return None

    fiyatlar = []
    
    for i in range(gun_sayisi):
        tarih = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        url = f"https://www.goldapi.io/api/XAU/USD/{tarih}"

        headers = {
            "x-access-token": api_key_altin,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 403:  # ✅ 403 hatalarını geç
                continue  

            response.raise_for_status()
            data = response.json()

            if "price" in data:
                gram_altin = data["price"] / 31.1035  # Ons'tan gram altına çevirme
                fiyatlar.append(gram_altin)

            time.sleep(1)  # API limit aşımını önlemek için bekleme süresi

        except requests.exceptions.RequestException:
            continue  # ❌ Hata mesajlarını tamamen kaldır

    if fiyatlar:
        return sum(fiyatlar) / len(fiyatlar)  # ✅ Ortalama hesapla ve döndür
    else:
        return None



# Güncellenmiş API key ile çağırma
api_key_altin = "goldapi-4vu9lsm6y4j4r0-io"
gecmis_ortalama_altin = gecmis_altin_verilerini_cek(api_key_altin, 10)

if gecmis_ortalama_altin:
    print(f"\n📊 Son 10 günün ortalama gram altın fiyatı: {gecmis_ortalama_altin:.2f} USD")
else:
    print("\n❌ Geçmiş altın fiyatları alınamadı.")


gram_altin_buy, gram_altin_sell = altin_fiyatlarini_cek(api_key_altin)
usd_to_try = doviz_verilerini_cek(api_key).get("TRY", 1)  # TRY kuru yoksa 1 al
if gram_altin_buy is not None and usd_to_try is not None:
    gram_altin_buy_try = gram_altin_buy * usd_to_try  # USD'den TRY'ye çevir
else:
    gram_altin_buy_try = None  # Eğer veri çekilemezse None olarak ata


if gram_altin_buy_try is not None:
    print(f"💰 Güncel Gram Altın Alış Fiyatı: {gram_altin_buy_try:.2f} TRY")
else:
    print("❌ Güncel Gram Altın fiyatı TRY cinsinden hesaplanamadı.")



enflasyon_orani = 44.38  
doviz_volatilite = 3  


gecmis_fiyatlar = gecmis_altin_verilerini_cek(api_key_altin)
if gecmis_ortalama_altin is not None:
    print(f"\n📊 Son 10 günün ortalama gram altın fiyatı: {gecmis_ortalama_altin:.2f} USD")

risk, yatırım_önerileri = risk_seviyesi_belirle(veriler["gelir"], veriler["gider"], enflasyon_orani, doviz_volatilite)

print(f"\nRisk Seviyeniz: {risk}")
print("Önerilen Yatırım Seçenekleri:")
for öneri in yatırım_önerileri:
    print(f"- {öneri}")

def gecmis_doviz_verilerini_cek(api_key, gun_sayisi=10):
    url = "https://openexchangerates.org/api/historical/{}.json?app_id={}"
    tarihler = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(gun_sayisi)]
    fiyatlar_usd = []
    fiyatlar_eur = []

    for tarih in tarihler:
        try:
            response = requests.get(url.format(tarih, api_key))
            response.raise_for_status()
            data = response.json()
            
            if "TRY" in data["rates"] and "USD" in data["rates"] and "EUR" in data["rates"]:
                fiyatlar_usd.append(data["rates"]["TRY"] / data["rates"]["USD"])  # TL'nin USD karşısındaki değeri
                fiyatlar_eur.append(data["rates"]["TRY"] / data["rates"]["EUR"])  # TL'nin EUR karşısındaki değeri
        except requests.exceptions.RequestException as e:
            print(f"{tarih} için döviz verisi alınamadı:", e)
            fiyatlar_usd.append(None)
            fiyatlar_eur.append(None)

    return fiyatlar_usd, fiyatlar_eur  # 2 liste döndürülüyor


    try:
        gun_sayisi = int(gun_sayisi)  # Eğer string gelirse integer'a çevir
    except ValueError:
        print("❌ Hata: gun_sayisi bir tam sayı olmalıdır!")
        return None

    fiyatlar = []
    
    for i in range(gun_sayisi):
        tarih = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        url = f"https://www.goldapi.io/api/XAU/USD/{tarih}"

        headers = {
            "x-access-token": api_key_altin,
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "price" in data:
                gram_altin = data["price"] / 31.1035  # Ons'tan gram altına çevirme
                fiyatlar.append(gram_altin)

            time.sleep(1)  # API limit aşımını önlemek için bekleme süresi

        except requests.exceptions.RequestException as e:
            print(f"❌ {tarih} için veri alınamadı: {e}")

    if fiyatlar:
        ortalama_fiyat = sum(fiyatlar) / len(fiyatlar)  # Ortalama hesapla
        return ortalama_fiyat  # Liste yerine sadece ortalama dön

    print("\n❌ Geçmiş altın fiyatları alınamadı.")
    return None




def hesapla_sma(fiyatlar, period=10):
    if not fiyatlar or len(fiyatlar) < period:  # Liste boş veya 10'dan az eleman varsa
        return None  
    return sum(fiyatlar[-period:]) / period  # Son 10 günün ortalaması

if veriler["yatırım_tercihi"].lower() == "döviz":
    gecmis_fiyatlar_usd, gecmis_fiyatlar_eur = gecmis_doviz_verilerini_cek(api_key)
    
    if gecmis_fiyatlar_usd and len(gecmis_fiyatlar_usd) >= 10:
        sma_10_usd = hesapla_sma(gecmis_fiyatlar_usd)
        print(f"\nTL'nin USD Karşısındaki SMA-10: {sma_10_usd:.4f} TRY")
    else:
        print("\nUSD için SMA-10 hesaplanamadı, yeterli veri yok.")

    if gecmis_fiyatlar_eur and len(gecmis_fiyatlar_eur) >= 10:
        sma_10_eur = hesapla_sma(gecmis_fiyatlar_eur)
        print(f"TL'nin EUR Karşısındaki SMA-10: {sma_10_eur:.4f} TRY")
    else:
        print("EUR için SMA-10 hesaplanamadı, yeterli veri yok.")

if veriler["yatırım_tercihi"].lower() == "altın":
    gecmis_fiyatlar = gecmis_altin_verilerini_cek(api_key_altin, 10)


        
       

def tablo_goster(yatırım_tercihi, fiyatlar_usd=None, fiyatlar_eur=None, fiyatlar_altin=None):
    if yatırım_tercihi.lower() == "döviz":
        if fiyatlar_usd and fiyatlar_eur:
            tarih_araligi = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(len(fiyatlar_usd))]
            df = pd.DataFrame({
                "Tarih": tarih_araligi,
                "USD/TRY": fiyatlar_usd,
                "EUR/TRY": fiyatlar_eur
            })
            print("\nTL'nin USD ve EUR Karşısındaki Değeri (Son 10 Gün):")
            print(df.to_string(index=False))  # Tablonun daha okunaklı görünmesi için index kaldırıldı
    elif yatırım_tercihi.lower() == "altın":
        if fiyatlar_altin:
            tarih_araligi = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(len(fiyatlar_altin))]
            df = pd.DataFrame({
                "Tarih": tarih_araligi,
                "Altın (TL)": fiyatlar_altin
            })
            print("\nAltın Fiyatları (Son 10 Gün - TL):")
            print(df.to_string(index=False))

def verileri_gorsellestir(yatırım_tercihi, gun_sayisi=10):
    plt.figure(figsize=(10, 5))
    
    if yatırım_tercihi.lower() == "döviz":
        # Döviz verilerini al
        gecmis_fiyatlar_usd, gecmis_fiyatlar_eur = gecmis_doviz_verilerini_cek(api_key, gun_sayisi)

        if gecmis_fiyatlar_usd and gecmis_fiyatlar_eur:
            # USD Grafiği
            plt.subplot(2, 1, 1)
            plt.plot(range(1, len(gecmis_fiyatlar_usd) + 1), gecmis_fiyatlar_usd, marker='o', linestyle='-', color='blue', label="TL'nin USD Karşısındaki Değeri")
            plt.xlabel("Gün")
            plt.ylabel("USD/TRY")
            plt.title("Son 10 Günlük TL - USD Değeri")
            plt.legend()
            plt.grid(True)

            # EUR Grafiği
            plt.subplot(2, 1, 2)
            plt.plot(range(1, len(gecmis_fiyatlar_eur) + 1), gecmis_fiyatlar_eur, marker='o', linestyle='-', color='red', label="TL'nin EUR Karşısındaki Değeri")
            plt.xlabel("Gün")
            plt.ylabel("EUR/TRY")
            plt.title("Son 10 Günlük TL - EUR Değeri")
            plt.legend()
            plt.grid(True)

    plt.tight_layout()
    plt.show()

# Kullanıcının seçtiği yatırım aracına göre grafik gösterimi
verileri_gorsellestir(veriler["yatırım_tercihi"])
