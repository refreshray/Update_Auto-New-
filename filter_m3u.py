import requests
import json
import os

# 1. รายการลิงก์ M3U ต้นทางทั้งหมด
playlist_urls = [
    "https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8",
]

# 2. โหลดไฟล์กำหนดค่า (channels_map.json)
mapping_file = "channels_map.json"
CUSTOM_CHANNELS = {}

if os.path.exists(mapping_file):
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            CUSTOM_CHANNELS = json.load(f)
    except Exception as e:
        print(f"Error loading {mapping_file}: {e}")

# กำหนดบรรทัดหัวข้อ M3U พร้อมลิงก์ EPG
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
                    
                    # กวาดเก็บข้อความหรือคำสั่งทั้งหมดที่อยู่รอบๆ บรรทัด #EXTINF (เช่น #EXTVLCOPT, #KODIPROP)
                    look_up = i - 1
                    while look_up >= 0 and lines[look_up].strip().startswith("#"):
                        prop_line = lines[look_up].strip()
                        if prop_line and not prop_line.startswith("#EXTINF:"):
                            block_lines.insert(0, prop_line)
                        look_up -= 1
                    
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
                        # ถ้าลิงก์สตรีมมีเครื่องหมาย # นำหน้า (ลิงก์เสีย) ให้ข้ามทันที
                        if stream_url.startswith("#"):
                            i = j
                            continue
                        
                        # ดึงชื่อช่องจากต้นทางหลังคอมมา (,) เพื่อเทียบชื่อแบบตรงเป๊ะ
                        parts = extinf_line.split(",")
                        original_name = parts[-1].strip() if len(parts) > 1 else extinf_line
                        
                        # ตรวจสอบชื่อช่องว่ามีอยู่ใน channels_map.json หรือไม่
                        matched_config = None
                        for exact_name, config in CUSTOM_CHANNELS.items():
                            if exact_name.strip() == original_name.strip():
                                matched_config = config
                                break
                        
                        # ถ้าไม่มีชื่อนี้ใน JSON ให้ข้ามไป
                        if matched_config is None:
                            i = j
                            continue
                        
                        # ถ้าผ่านและลิงก์ยังไม่ซ้ำ
                        if stream_url not in seen_streams:
                            seen_streams.add(stream_url)
                            
                            # เขียนบรรทัดเสริมทั้งหมดตามต้นฉบับ (#EXTVLCOPT, #KODIPROP)
                            for b_line in block_lines:
                                combined_content += b_line + "\n"
                            
                            # ดึงค่าจาก JSON มาใช้ ถ้าค่าไหนเว้นว่างไว้ จะใช้ข้อมูลจากต้นฉบับเดิมแทน
                            custom_tvg_id = matched_config.get("tvg-id", "").strip()
                            custom_tvg_name = matched_config.get("tvg-name", "").strip()
                            custom_tvg_logo = matched_config.get("tvg-logo", "").strip()
                            custom_group = matched_config.get("group-title", "").strip()
                            custom_name = matched_config.get("name", "").strip()
                            
                            # หากระบุข้อมูลใน JSON ให้ประกอบร่างใหม่ตามที่ต้องการ แต่ถ้าปล่อยว่างจะดึงต้นฉบับมาใช้
                            # (สามารถแยก parse ค่าจาก extinf_line เดิมมาใช้สำรองได้)
                            final_name = custom_name if custom_name else original_name
                            
                            # สร้างบรรทัด #EXTINF ใหม่โดยใช้ค่าที่เราตั้งใจ custom
                            # (ถ้าใน JSON เว้นว่างช่องไหนไว้ จะดึงจากค่าเดิมของต้นฉบับมาใส่ให้)
                            final_extinf = extinf_line
                            if custom_tvg_id or custom_tvg_name or custom_tvg_logo or custom_group or custom_name:
                                # ดึงค่าเก่ามาเป็นฐาน
                                # สร้างบรรทัดใหม่โดยอิงค่า Custom
                                t_id = custom_tvg_id if custom_tvg_id else ""
                                t_name = custom_tvg_name if custom_tvg_name else original_name
                                t_logo = custom_tvg_logo if custom_tvg_logo else ""
                                t_group = custom_group if custom_group else "General"
                                
                                final_extinf = f'#EXTINF:-1 tvg-id="{t_id}" tvg-name="{t_name}" tvg-logo="{t_logo}" group-title="{t_group}", {final_name}'
                            
                            combined_content += final_extinf + "\n" + stream_url + "\n"
                        
                        i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกไฟล์ผลลัพธ์
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully generated playlist with flexible JSON mapping!")
