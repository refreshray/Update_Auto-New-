import requests

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด (ใส่ได้หลายแหล่ง)
playlist_urls = [
    "https://github.com/konanda-sg/Upcoming-and-Live-Sports-Data/raw/refs/heads/main/Sports_data.m3u",
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8"
]

# 2. คำค้นหา (Keywords) ที่ต้องการดึง (ถ้าใส่ไว้ บอทจะดึงเฉพาะช่องที่มีชื่อตรงกับคำเหล่านี้)
# ถ้าอยากให้ดึงทุกช่องโดยไม่กรองคำ ให้ปล่อยรายการนี้ว่างไว้ เช่น KEYWORDS = []
KEYWORDS = ["beIN Sports 1 (Australia)","beIN Sports 2 (Australia)","beIN Sports 3 (Australia)"]

combined_content = "#EXTM3U\n"
seen_streams = set()

for url in playlist_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # มองหาจุดเริ่มต้นของช่อง (#EXTINF)
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    props = []
                    stream_url = ""
                    
                    # 1. ลองกวาดหา #KODIPROP ที่อยู่ "ด้านบน" ย้อนขึ้นไป (ถ้ามี)
                    look_up = i - 1
                    while look_up >= 0 and (lines[look_up].strip().startswith("#KODIPROP") or not lines[look_up].strip()):
                        if lines[look_up].strip().startswith("#KODIPROP"):
                            props.insert(0, lines[look_up].strip()) # แทรกไว้ข้างหน้า
                        look_up -= 1
                    
                    # 2. ค้นหา URL และ #KODIPROP ที่อยู่ "ด้านล่าง" ลงมา
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        
                        if next_line.startswith("#KODIPROP:"):
                            props.append(next_line)
                        elif not next_line.startswith("#"):
                            stream_url = next_line
                            break
                        j += 1
                    
                    # ถ้าเจอ URL ของสตรีม
                    if stream_url:
                        # ตรวจสอบเงื่อนไข Keywords จากชื่อช่อง
                        parts = extinf_line.split(",")
                        channel_name = parts[-1].strip() if len(parts) > 1 else extinf_line
                        
                        matched = True
                        if KEYWORDS:
                            matched = False
                            for kw in KEYWORDS:
                                if kw.lower() in channel_name.lower():
                                    matched = True
                                    break
                        
                        # ถ้าผ่าน Keyword และลิงก์ไม่ซ้ำ
                        if matched and stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            
                            # จัดเรียงพิมพ์ออกไปตามลำดับที่ถูกต้องเสมอ: #KODIPROP -> #EXTINF -> URL
                            # กรอง #KODIPROP ที่ซ้ำกันในชุดเดียวกันออกด้วย set เพื่อความสะอาด
                            unique_props = []
                            for p in props:
                                if p not in unique_props:
                                    unique_props.append(p)
                            
                            for prop in unique_props:
                                combined_content += prop + "\n"
                            
                            combined_content += extinf_line + "\n" + stream_url + "\n"
                    
                    i = j  # ข้ามไปประมวลผลต่อจากตำแหน่ง URL ล่าสุด
                i += 1
                
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully cleaned and ordered playlist!")
