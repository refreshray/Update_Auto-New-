import requests

# 1. URL ต้นทางของคุณ
M3U_URL = "https://github.com/cattv976/iptv/raw/refs/heads/main/cattv.m3u","https://github.com/babygen-sys/tvplus-playlist/raw/refs/heads/main/K_PRO.m3u8"

# 2. ชื่อช่องที่ต้องการ
KEYWORDS = [
    "Samrujlok", "MySci", "Animal Show", "AsianHits", "MonoPlus", 
    "HBO", "HBOHits", "HBOSignature", "HBOFamily", "Cinemax", 
    "Rock-Entertainment", "ROCKAction", "Warnertv", "CARTOON NETWORK", 
    "CARTOONITO", "NICKELODEON", "NICK JR", "Boomerang", "Dreamworks", 
    "ANIMAX", "Zoo Moo (1080p)", "movies1", "movies2", "movies3", 
    "movies4", "movies5", "Food Network", "Astro Grandstand", 
    "Astro Football", "Astro Premier League", "Astro Premier League2","MAX 1","MAX 2"
]

def main():
    try:
        response = requests.get(M3U_URL, timeout=10)
        if response.status_code != 200:
            print(f"ไม่สามารถดาวน์โหลดไฟล์ได้ (Status code: {response.status_code})")
            return
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
        return

    lines = response.text.splitlines()
    output_lines = ['#EXTM3U url-tvg="https://github.com/refreshray/epg-auto/raw/refs/heads/main/TV_epg.xml"\n']
    
    is_capturing = False # ตัวแปรเช็คว่ากำลังเก็บข้อมูลช่องที่ต้องการอยู่หรือไม่

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # ถ้าเจอหัวข้อช่องใหม่
        if clean_line.startswith("#EXTINF:"):
            if any(keyword.lower() in clean_line.lower() for keyword in KEYWORDS):
                is_capturing = True
                output_lines.append(clean_line + "\n")
            else:
                is_capturing = False
        
        # ถ้าอยู่ในสถานะกำลังเก็บข้อมูล (เช่น บรรทัด #EXTVLCOPT หรือ ลิงก์สตรีม)
        elif is_capturing:
            output_lines.append(clean_line + "\n")
            # ถ้าเจอลิงก์สตรีม ถือว่าจบบล็อกของช่องนี้แล้ว ให้ปิดการเก็บสำหรับช่องนี้
            if clean_line.startswith("http://") or clean_line.startswith("https://"):
                is_capturing = False

    # บันทึกเป็นไฟล์ใหม่
    output_filename = "Update_playlist.m3u"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"กรองเพลย์ลิสต์เสร็จเรียบร้อย! บันทึกลงไฟล์ {output_filename} แล้ว (พบทั้งหมด {len(output_lines)} บรรทัด)")

if __name__ == "__main__":
    main()
