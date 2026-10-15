import requests

# รายการลิงก์ M3U ทั้งหมดที่คุณต้องการดึงมารวมกัน
playlist_urls = [
    "https://example.com/playlist1.m3u",
    "https://example.com/playlist2.m3u"
]

combined_content = "#EXTM3U\n"
seen_urls = set()  # ใช้เก็บลิงก์สตรีมที่ไม่ให้ซ้ำกัน

for url in playlist_urls:
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            lines = response.text.splitlines()
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # ข้ามบรรทัดหัวข้อหรือบรรทัดว่าง
                if line.startswith("#EXTM3U") or not line:
                    i += 1
                    continue
                
                # ถ้าเจอข้อมูลช่อง (#EXTINF) ให้มองหาลิงก์สตรีมในบรรทัดถัดไป
                if line.startswith("#EXTINF:"):
                    extinf_line = line
                    stream_url = ""
                    
                    # ค้นหาบรรทัดที่เป็น URL ของสตรีมถัดไป
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith("#"):
                            stream_url = next_line
                            break
                        j += 1
                    
                    # ถ้าเจอ URL และยังไม่เคยมีอยู่ในระบบ ให้เพิ่มเข้าไป
                    if stream_url:
                        if stream_url not in seen_urls:
                            seen_urls.add(stream_url)
                            combined_content += extinf_line + "\n" + stream_url + "\n"
                        # ข้าม index ไปยังตำแหน่งหลัง URL ที่ประมวลผลแล้ว
                        i = j
                i += 1
        else:
            print(f"Failed to fetch {url} with status {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

# บันทึกรวมเป็นไฟล์เดียวแบบไม่มีรายการซ้ำ
with open("Update_playlist.m3u", "w", encoding="utf-8") as f:
    f.write(combined_content)

print("Successfully merged and removed duplicates into Update_playlist.m3u")
