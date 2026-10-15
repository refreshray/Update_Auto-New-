import requests
import json
import os

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด
playlist_urls = [
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8",
]

# 2. กำหนด KEYWORDS สำหรับกรองช่องที่ต้องการ
KEYWORDS = ["beIN Sports 1 (Australia)", "beIN Sports 2 (Australia)", "beIN Sports 3 (Australia)"]

# 3. โหลดไฟล์กำหนดค่าแยก (channels_map.json) สำหรับตั้งค่า tvg-id, logo, group เอง
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
                    
                    # กวาดหา #KODIPROP รอบๆ บรรทัด
                    look_up = i - 1
                    while look_up >= 0 and (lines[look_up].strip().startswith("#KODIPROP") or not lines[look_up].strip()):
                        if lines[look_up].strip().startswith("#KODIPROP"):
                            props.insert(0, lines[look_up].strip())
                        look_up -= 1
                    
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
                    
                    if stream_url:
                        # ดึงชื่อช่องต้นทางมาตรวจสอบ
                        parts = extinf_line.split(",")
                        original_name = parts[-1].strip().lower() if len(parts) > 1 else extinf_line.lower()
                        
                        # 4. ตรวจสอบเงื่อนไข KEYWORDS
                        matched_keyword = True
                        if KEYWORDS:
                            matched_keyword = False
                            for kw in KEYWORDS:
                                if kw.lower() in original_name or kw.lower() in extinf_line.lower():
                                    matched_keyword = True
                                    break
                        
                        # ถ้าไม่ผ่าน Keyword ให้ข้ามไป
                        if not matched_keyword:
                            i = j
                            continue
                        
                        # 5. เช็กกับไฟล์ Custom Mapping (channels_map.json) แบบยืดหยุ่น
                        matched_custom = None
                        for keyword, info in CUSTOM_CHANNELS.items():
                            clean_keyword = keyword.lower().replace(" ", "")
                            clean_name = original_name.lower().replace(" ", "")
                            clean_extinf = extinf_line.lower().replace(" ", "")
                            
                            if clean_keyword in clean_name or clean_keyword in clean_extinf:
                                matched_custom = info
                                break
                        
                        # ถ้าลิงก์ยังไม่ซ้ำ ดำเนินการจัดเก็บ
                        if stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            
                            # เขียน #KODIPROP
                            unique_props = list(dict.fromkeys(props))
                            for prop in unique_props:
                                combined_content += prop + "\n"
                            
                            # ถ้าเจอในไฟล์ Mapping ให้ใช้ข้อมูลที่เรากำหนดเอง
                            if matched_custom:
                                custom_extinf = (
                                    f'#EXTINF:-1 '
                                    f'tvg-id="{matched_custom.get("tvg-id", "")}" '
                                    f'tvg-name="{matched_custom.get("tvg-name", "")}" '
                                    f'tvg-logo="{matched_custom.get("tvg-logo", "")}" '
                                    f'group-title="{matched_custom.get("group-title", "General")}", '
                                    f'{matched_custom.get("name", original_name)}'
                                )
                                combined_content += custom_extinf + "\n" + stream_url + "\n"
                            else:
                                combined_content += extinf_line + "\n" + stream_url + "\n"
                        
                        i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์รวม
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully filtered by keywords, mapped config, and merged playlist!")
