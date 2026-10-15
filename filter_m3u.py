import requests

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด (ใส่ได้หลายแหล่ง)
playlist_urls = [
    "https://github.com/konanda-sg/Upcoming-and-Live-Sports-Data/raw/refs/heads/main/Sports_data.m3u",
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8"
]

# 2. คำค้นหา (Keywords) ที่ต้องการดึง (ถ้าใส่ไว้ บอทจะดึงเฉพาะช่องที่มีชื่อตรงกับคำเหล่านี้)
# ถ้าอยากให้ดึงทุกช่องโดยไม่กรองคำ ให้ปล่อยรายการนี้ว่างไว้ เช่น KEYWORDS = []
KEYWORDS = ["BeIN1 SPORTSFHD", "BEIN2 SPORTS FHD", "BEIN3 SPORTS FHD", "SKY MAIN EVENT"]

combined_content = "#EXTM3U\n"
seen_streams = set()  # ใช้ป้องกันลิงก์สตรีมซ้ำ
seen_names = set()    # ใช้ป้องกันชื่อช่องซ้ำ (ถ้าต้องการ)

for url in playlist_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("#EXTM3U") or not line:
                    i += 1
                    continue
                
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    stream_url = ""
                    
                    # ค้นหาลิงก์สตรีมในบรรทัดถัดไป
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            stream_url = next_line
                            break
                        j += 1
                    
                    if stream_url:
                        # ตรวจสอบเงื่อนไข Keywords (ถ้ามีการกำหนดค่าไว้)
                        matched = True
                        if KEYWORDS:
                            matched = False
                            for kw in KEYWORDS:
                                if kw.lower() in extinf_line.lower():
                                    matched = True
                                    break
                        
                        # ถ้าผ่านเงื่อนไข Keyword และยังไม่เคยมีลิงก์หรือชื่อนี้มาก่อน
                        if matched and stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            combined_content += extinf_line + "\n" + stream_url + "\n"
                            i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกผลลัพธ์รวมลงไฟล์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully filtered, merged, and removed duplicates!")
