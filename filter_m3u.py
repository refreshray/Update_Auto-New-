import requests

# 1. รายการ URL ต้นทางทั้งหมด (เปลี่ยนเป็น List เพื่อให้วนลูปดึงข้อมูลได้ครบทุกไฟล์)
playlist_urls = [
    "https://github.com/cattv976/iptv/raw/refs/heads/main/cattv.m3u",
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8"
]

# 2. ชื่อช่องที่ต้องการ (Keywords)
KEYWORDS = [
    "Samrujlok", "MySci", "Animal Show", "AsianHits", "MonoPlus", 
    "HBO", "HBOHits", "HBOSignature", "HBOFamily", "Cinemax", 
    "Rock-Entertainment", "ROCKAction", "Warnertv", "CARTOON NETWORK", 
    "CARTOONITO", "NICKELODEON", "NICK JR", "Boomerang", "Dreamworks", 
    "ANIMAX", "Zoo Moo (1080p)", "movies1", "movies2", "movies3", 
    "movies4", "movies5", "Food Network", "Astro Grandstand", 
    "Astro Football", "Astro Premier League", "Astro Premier League2", "MAX 1", "MAX 2"
]

def main():
    # กำหนดบรรทัดหัวข้อ M3U พร้อมลิงก์ EPG (ให้มีแค่อันเดียวตอนเริ่มต้นไฟล์)
    output_lines = ['#EXTM3U url-tvg="https://github.com/refreshray/epg-auto/raw/refs/heads/main/TV_epg.xml"\n']
    
    seen_streams = set() # ป้องกันลิงก์ซ้ำ

    # วนลูปดึงข้อมูลจากทุก URL ต้นทาง
    for url in playlist_urls:
        try:
            print(f"กำลังดาวน์โหลดจาก: {url}")
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                print(f"ไม่สามารถดาวน์โหลดไฟล์จาก {url} ได้ (Status code: {response.status_code})")
                continue
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเชื่อมต่อกับ {url}: {e}")
            continue

        lines = response.text.splitlines()
        is_capturing = False 
        current_block = []

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            # ถ้าเจอหัวข้อช่องใหม่ (#EXTINF)
            if clean_line.startswith("#EXTINF:"):
                # เช็กว่าตรงกับ Keyword ที่ต้องการไหม
                if any(keyword.lower() in clean_line.lower() for keyword in KEYWORDS):
                    is_capturing = True
                    current_block = [clean_line + "\n"]
                else:
                    is_capturing = False
                    current_block = []
            
            # ถ้าอยู่ในสถานะกำลังเก็บข้อมูลช่องนั้นๆ (เก็บ #EXTVLCOPT, #KODIPROP หรือบรรทัดเสริมอื่นๆ)
            elif is_capturing:
                current_block.append(clean_line + "\n")
                
                # ถ้าเจอลิงก์สตรีม (เช็กทั้ง http:// และ https://)
                if clean_line.startswith("http://") or clean_line.startswith("https://"):
                    # ตรวจสอบเพิ่มเติม: ถ้าลิงก์เริ่มต้นด้วย # แปลว่าเป็นลิงก์เสีย (ป้องกันไว้เผื่อติดมา)
                    if clean_line.startswith("#"):
                        is_capturing = False
                        current_block = []
                        continue

                    # ตรวจสอบลิงก์ซ้ำ
                    stream_url = clean_line
                    if stream_url not in seen_streams:
                        seen_streams.add(stream_url)
                        # นำบล็อกข้อมูลช่องนี้ใส่เข้าไปในรายการหลัก
                        output_lines.extend(current_block)
                    
                    # จ็อบบล็อกของช่องนี้แล้ว รีเซ็ตสถานะ
                    is_capturing = False
                    current_block = []

    # บันทึกเป็นไฟล์ใหม่
    output_filename = "Update_playlist.m3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"กรองเพลย์ลิสต์เสร็จเรียบร้อย! บันทึกลงไฟล์ {output_filename} แล้ว (รวมทั้งหมด {len(output_lines)} บรรทัด)")

if __name__ == "__main__":
    main()
