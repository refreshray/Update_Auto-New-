import requests

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด (ใส่ได้หลายแหล่ง)
playlist_urls = [
    "https://github.com/konanda-sg/Upcoming-and-Live-Sports-Data/raw/refs/heads/main/Sports_data.m3u",
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8"
]

# 2. คำค้นหา (Keywords) ที่ต้องการดึง (ถ้าใส่ไว้ บอทจะดึงเฉพาะช่องที่มีชื่อตรงกับคำเหล่านี้)
# ถ้าอยากให้ดึงทุกช่องโดยไม่กรองคำ ให้ปล่อยรายการนี้ว่างไว้ เช่น KEYWORDS = []
KEYWORDS = ["BeIN1 SPORTSFHD", "BEIN2 SPORTS FHD", "BEIN3 SPORTS FHD", "SKY MAIN EVENT","beIN Sports 1 (Australia)","beIN Sports 2 (Australia)","beIN Sports 3 (Australia)"]

combined_content = "#EXTM3U\n"
seen_streams = set()

for url in playlist_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            # เก็บค่าชั่วคราวสำหรับรอบปัจจุบัน
            current_props = []
            current_extinf = ""
            
            for line in lines:
                line_str = line.strip()
                if not line_str or line_str.startswith("#EXTM3U"):
                    continue
                
                # ถ้าเจอ #KODIPROP หรือบรรทัดตั้งค่าอื่นๆ เก็บสะสมไว้
                if line_str.startswith("#KODIPROP:"):
                    current_props.append(line_str)
                
                # ถ้าเจอ #EXTINF ให้เก็บไว้เป็นข้อมูลช่องหลัก
                elif line_str.startswith("#EXTINF:"):
                    current_extinf = line_str
                    current_props = [] # ล้างค่า prop เก่าถ้ามีอันใหม่ซ้อน
                
                # ถ้าบรรทัดนี้ไม่ใช่ขึ้นต้นด้วย # แสดงว่าเป็น URL ของสตรีม
                elif not line_str.startswith("#") and current_extinf:
                    stream_url = line_str
                    
                    # ตรวจสอบ Keyword จากชื่อช่อง (#EXTINF)
                    parts = current_extinf.split(",")
                    channel_name = parts[-1].strip() if len(parts) > 1 else current_extinf
                    
                    matched = True
                    if KEYWORDS:
                        matched = False
                        for kw in KEYWORDS:
                            if kw.lower() in channel_name.lower():
                                matched = True
                                break
                    
                    # ถ้าผ่านเงื่อนไขและลิงก์ไม่ซ้ำ
                    if matched and stream_url not in seen_streams:
                        seen_streams.add(stream_url)
                        
                        # เขียนบรรทัด #KODIPROP (ถ้ามี)
                        for prop in current_props:
                            combined_content += prop + "\n"
                        
                        # เขียนข้อมูลช่องและลิงก์สตรีมที่ถูกต้องคู่กัน
                        combined_content += current_extinf + "\n" + stream_url + "\n"
                    
                    # รีเซ็ตค่าเพื่อรอจับคู่ชุดถัดไป
                    current_extinf = ""
                    current_props = []
                    
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully filtered and paired correctly!")
