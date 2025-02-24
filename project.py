import time
import network
import machine as m
import dht
import ujson
import urequests

# 🔹 Konfigurasi WiFi
WIFI_SSID = "POCO M3"  # Ganti dengan WiFi kamu
WIFI_PASS = "Palem2f8771"  # Ganti dengan password WiFi kamu

# 🔹 Konfigurasi REST API & Ubidots
UBIDOTS_TOKEN = "BBUS-4p3JS6lOPE6pouh8uHFWg3CjWkBm7B"  # Ganti dengan token kamu
DEVICE_LABEL = "ESP32_Wokwi"  # Nama perangkat di Ubidots
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# 🔹 Fungsi koneksi WiFi
def connect_wifi():
    print("Connecting to WiFi", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASS)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    print(" Connected!")

# 🔹 Setup hardware
led = m.Pin(4, m.Pin.OUT)  # LED di GPIO 4
sensor = dht.DHT11(m.Pin(5))  # Sensor DHT11 di GPIO 5
pir_sensor = m.Pin(18, m.Pin.IN)  # Sensor PIR pada GPIO 14

# 🔹 Fungsi kirim data ke Ubidots
def send_to_ubidots(temp, hum):
    payload = ujson.dumps({
        "temperature": temp,
        "humidity": hum
    })
    
    print(f"📤 Sending data to Ubidots: {payload}")
    
    try:
        response = urequests.post(UBIDOTS_URL, headers=HEADERS, data=payload)
        print(f"✅ Response: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"⚠️ Error sending data: {e}")

def send_motion_data(motion):
    payload = ujson.dumps({"motion": motion})
    print(f"Mengirim data gerakan ke Ubidots: {payload}")
    
    try:
        response = urequests.post(UBIDOTS_URL, headers=HEADERS, data=payload)
        print(f"Respon: {response.status_code}")
        response.close()
    except Exception as e:
        print(f"Terjadi kesalahan saat mengirim data gerakan: {e}")

# 🔹 Fungsi cek status LED dari Ubidots
# 🔹 Fungsi cek status LED dari Ubidots
# 🔹 Fungsi cek status LED dari Ubidots
def get_led_status():
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/led_control/lv"  # HARUS /lv
    try:
        response = urequests.get(url, headers={"X-Auth-Token": UBIDOTS_TOKEN})
        raw_data = response.text.strip()  # Bersihkan whitespace
        response.close()

        print(f"📝 Raw Response: {raw_data}")  # Debugging respons

        # **Konversi ke integer, menangani error parsing**
        try:
            led_value = int(float(raw_data))  # Convert ke angka
            print(f"📩 LED Control Value: {led_value}")
            return led_value
        except ValueError:
            print("⚠️ JSON Parsing Error! Menggunakan default LED OFF.")
            return 0  # Default OFF jika error
        
    except Exception as e:
        print(f"⚠️ Error getting LED status: {e}")
        return 0  # Default OFF jika ada kesalahan



# 🔹 Jalankan WiFi
connect_wifi()

# 🔹 Loop utama
while True:
    try:
        # **Baca Sensor DHT**
        sensor.measure()
        motion_detected = pir_sensor.value()
        temperature = sensor.temperature()
        humidity = sensor.humidity()

        # **Kirim data ke Ubidots**
        send_to_ubidots(temperature, humidity)
        
        
        send_motion_data(motion_detected)

        # **Cek status LED dari Ubidots**
        led_status = get_led_status()
        
        # **Nyalakan atau Matikan LED berdasarkan nilai led_control**
        if led_status == 1:
            led.on()
            print("💡 LED ON")
        else:
            led.off()
            print("💡 LED OFF")

        time.sleep(5)  # Delay untuk menghindari rate limit

    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(2)  # Jika error, coba lagi
