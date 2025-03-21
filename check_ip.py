import geoip2.database
import os
import concurrent.futures
import time
import sys
import threading

def spinner_animation():
    animation = "|/-\\"
    idx = 0
    while not spinner_animation.done:
        sys.stdout.write("\r" + "Đang xử lý... " + animation[idx % len(animation)])
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
spinner_animation.done = False

def check_ip_with_maxmind(ip_address, proxy):
    try:
        reader = geoip2.database.Reader('dataip.mmdb')     
        response = reader.city(ip_address)
        country = response.country.name or "Không có thông tin"
        region = response.subdivisions.most_specific.name if response.subdivisions else "Không có thông tin"
        city = response.city.name or None
        latitude = response.location.latitude
        longitude = response.location.longitude
        postal = response.postal.code if response.postal else None
        timezone = response.location.time_zone or "Không có thông tin"
        accuracy = response.location.accuracy_radius
        reader.close()
        if country == "Vietnam":
            if region == "Không có thông tin" or city is None or accuracy > 100:
                return "not_info", proxy, None
            elif "Ho Chi Minh" in region or "Hồ Chí Minh" in region:
                return "hcm", proxy, None
            elif "Hanoi" in region or "Hà Nội" in region:
                return "hanoi", proxy, None
            else:
                location = f"{region}, {city}" if city else region
                return "lonxon", proxy, location
        else:
            return "not_info", proxy, None
    except geoip2.errors.AddressNotFoundError:
        return "not_info", proxy, None
    except Exception as e:
        return "not_info", proxy, None
def process_proxy_ips(proxies, max_workers=20):
    try:
        if not os.path.exists('data'):
            os.makedirs('data')
        for filename in ['hanoi.txt', 'hcm.txt', 'lonxon.txt', 'not_info.txt']:
            with open(f'data/{filename}', 'w', encoding='utf-8') as f:
                f.write("")
    except Exception as e:
        print(f"Lỗi khi tạo file: {e}")
    results = {"hanoi": [], "hcm": [], "lonxon": [], "not_info": []}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for proxy in proxies:
            proxy_parts = proxy.split(":")
            if len(proxy_parts) >= 4:
                ip = proxy_parts[0]
                futures.append(executor.submit(check_ip_with_maxmind, ip, proxy))
            else:
                with open('data/not_info.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{proxy}\n")
                    f.flush()
                results["not_info"].append(proxy)
        
        for future in concurrent.futures.as_completed(futures):
            try:
                category, proxy, location = future.result()
                results[category].append(proxy)
                with open(f'data/{category}.txt', 'a', encoding='utf-8') as f:
                    if category == "lonxon" and location:
                        f.write(f"{proxy}|{location}\n")
                    else:
                        f.write(f"{proxy}\n")
                    f.flush()
                
            except Exception as e:
                with open('data/not_info.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{proxy}\n")
                    f.flush()
    
    return results

def main():
    try:
        with open("proxy.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        if not proxies:
            print("File proxy.txt rỗng hoặc không có proxy hợp lệ. Yêu cầu định dạng ip:port:user:pass")
            return
        if not os.path.exists('dataip.mmdb'):
            return
        print(f"Đang kiểm tra {len(proxies)} proxy.")
        spinner_animation.done = False
        spinner_thread = threading.Thread(target=spinner_animation)
        spinner_thread.start()
        
        results = process_proxy_ips(proxies)
        spinner_animation.done = True
        spinner_thread.join()
        
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()
        
        print("\n===== Kết quả phân loại =====")
        print(f"Số proxy ở Hà Nội: {len(results['hanoi'])} (lưu trong data/hanoi.txt)")
        print(f"Số proxy ở Hồ Chí Minh: {len(results['hcm'])} (lưu trong data/hcm.txt)")
        print(f"Số proxy ở vị trí khác: {len(results['lonxon'])} (lưu trong data/lonxon.txt, định dạng proxy|vị trí)")
        print(f"Số proxy không có đủ thông tin: {len(results['not_info'])} (lưu trong data/not_info.txt)")
        print(f"Tổng thời gian chạy: {time.time() - start_time:.2f} giây")
    
    except FileNotFoundError:
        print("Không tìm thấy file proxy.txt. Vui lòng tạo file với mỗi hàng có định dạng ip:port:user:pass")
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        spinner_animation.done = True

if __name__ == "__main__":
    start_time = time.time()
    main()