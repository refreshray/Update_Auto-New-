import requests
import json
import os

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด
playlist_urls = [
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8",
]

# 2. โหลดไฟล์กำหนดชื่อช่อง (channels_map.json) เพื่อใช้เป็นรายชื่อที่ต้องการดึง (Exact Match)
mapping_file = "channels_map.json"
CUSTOM_CHANNELS = {}

if os.path.exists(mapping_file):
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            CUSTOM_CHANNELS = json.load(f)
    except Exception as e:
        print(f"Error loading {mapping_file}: {e}")

# กำหนดบรรทัดหัวข้อ M3U พร้อมลิงก์ EPG (ถ้ามี)
combined_content = '#EXTM3U url-tvg="https://github.com/iptv-org/epg/raw/refs/heads/master/sites/beinsports.com/beinsports.com_au-en.channels.xml"\n'
seen_streams = set()

for url in playlist_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    block_lines = []
                    stream_url = ""
                    
                    # กวาดเก็บข้อความหรือคำสั่งทั้งหมดที่อยู่ "ด้านบน" บรรทัด #EXTINF (เช่น #EXTVLCOPT, #KODIPROP)
                    look_up = i - 1
                    while look_up >= 0 and lines[look_up].strip().startswith("#"):
                        prop_line = lines[look_up].strip()
                        if prop_line and not prop_line.startswith("#EXTINF:"):
                            block_lines.insert(0, prop_line)
                        look_up -= 1
                    
                    # ค้นหาลิงก์สตรีมที่อยู่ "ด้านล่าง"
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        if next_line.startswith("#"):
                            block_lines.append(next_line)
                        else:
                            stream_url = next_line
                            break
                        j += 1
                    
                    if stream_url:
                        # ถ้าลิงก์สตรีมมีเครื่องหมาย # นำหน้า (ลิงก์เสีย/ถูกปิด) ให้ข้ามทันที
                        if stream_url.startswith("#"):
                            i = j
                            continue
                        
                        # ดึงชื่อช่องจากต้นทางหลังคอมมา (,) เพื่อนำมาเทียบชื่อแบบตรงเป๊ะ
                        parts = extinf_line.split(",")
                        original_name = parts[-1].strip() if len(parts) > 1 else extinf_line
                        
                        # ตรวจสอบชื่อช่องว่ามีอยู่ใน channels_map.json แบบตรงกันเป๊ะหรือไม่
                        is_matched = False
                        for exact_name in CUSTOM_CHANNELS.keys():
                            if exact_name.strip() == original_name.strip():
                                is_matched = True
                                break
                        
                        # ถ้าชื่อไม่ตรงกับในไฟล์ Map ให้ข้ามทันที
                        if not is_matched:
                            i = j
                            continue
                        
                        # ถ้าผ่านและลิงก์ยังไม่ซ้ำ ดำเนินการคัดลอกตามต้นฉบับ
                        if stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            
                            # เขียนบรรทัดเสริมทั้งหมดตามต้นฉบับ (เช่น #EXTVLCOPT, #KODIPROP)
                            for b_line in block_lines:
                                combined_content += b_line + "\n"
                            
                            # เขียนบรรทัด #EXTINF และลิงก์สตรีมตามต้นฉบับเดิม
                            combined_content += extinf_line + "\n" + stream_url + "\n"
                        
                        i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully copied exact channels and filtered out broken links!")
