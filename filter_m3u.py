import requests
import json
import os

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด
playlist_urls = [
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8",
]

# 2. กำหนด KEYWORDS สำหรับกรองช่องที่ต้องการ
KEYWORDS = ["beIN Sports 1 (Australia)", "beIN Sports 2 (Australia)", "beIN Sports 3 (Australia)","MAX 1","MAX 2"]

# 2. โหลดไฟล์กำหนดค่า (channels_map.json)
# สคริปต์จะใช้รายชื่อ (Key) ในไฟล์นี้เป็นตัวกรองหลักทันที ช่องไหนไม่มีใน JSON จะถูกข้ามทั้งหมด
mapping_file = "channels_map.json"
CUSTOM_CHANNELS = {}

if os.path.exists(mapping_file):
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            CUSTOM_CHANNELS = json.load(f)
    except Exception as e:
        print(f"Error loading {mapping_file}: {e}")

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
                    props = []
                    stream_url = ""
                    
                    # กวาดหา #KODIPROP หรือบรรทัดเสริมอื่นๆ เช่น #EXTVLCOPT
                    look_up = i - 1
                    while look_up >= 0 and (lines[look_up].strip().startswith("#") or not lines[look_up].strip()):
                        prop_line = lines[look_up].strip()
                        if prop_line and not prop_line.startswith("#EXTINF:"):
                            props.insert(0, prop_line)
                        look_up -= 1
                    
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        if next_line.startswith("#"):
                            props.append(next_line)
                        else:
                            stream_url = next_line
                            break
                        j += 1
                    
                    if stream_url:
                        # ถ้า URL ต้นทางมีเครื่องหมาย # นำหน้า (ลิงก์เสีย/ถูกปิด) ให้ข้ามทันที
                        if stream_url.startswith("#"):
                            i = j
                            continue
                        
                        # ดึงชื่อช่องต้นทางมาเช็ก
                        parts = extinf_line.split(",")
                        original_name = parts[-1].strip() if len(parts) > 1 else extinf_line
                        
                        # 3. ตรวจสอบชื่อช่องแบบเทียบกับ keys ใน channels_map.json (แบบตรงตัวหรือพิมพ์เล็ก/ใหญ่ไม่ตรงกันได้)
                        matched_custom = None
                        for exact_name, info in CUSTOM_CHANNELS.items():
                            # เปรียบเทียบชื่อแบบตัวพิมพ์เล็ก-ใหญ่ชนกันตรงๆ หรือตัดช่องว่างส่วนเกิน
                            if exact_name.strip().lower() == original_name.strip().lower():
                                matched_custom = info
                                break
                        
                        # ถ้าชื่อช่องนี้ "ไม่มี" อยู่ใน channels_map.json ให้ข้ามทันที (ไม่ดึงมั่วซั่ว)
                        if not matched_custom:
                            i = j
                            continue
                        
                        # ถ้าเจอและลิงก์ยังไม่ซ้ำ
                        if stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            
                            # กรองบรรทัดตั้งค่าเสริม
                            unique_props = list(dict.fromkeys(props))
                            for prop in unique_props:
                                if not prop.startswith("#http"):
                                    combined_content += prop + "\n"
                            
                            # สร้างบรรทัด #EXTINF ใหม่ตามข้อมูลที่เราตั้งไว้ใน JSON
                            custom_extinf = (
                                f'#EXTINF:-1 '
                                f'tvg-id="{matched_custom.get("tvg-id", "")}" '
                                f'tvg-name="{matched_custom.get("tvg-name", "")}" '
                                f'tvg-logo="{matched_custom.get("tvg-logo", "")}" '
                                f'group-title="{matched_custom.get("group-title", "General")}", '
                                f'{matched_custom.get("name", original_name)}'
                            )
                            combined_content += custom_extinf + "\n" + stream_url + "\n"
                        
                        i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully filtered by exact channel names from JSON!")
