import time
import network
import machine as m
import dht
import ujson
import urequests

# Konfigurasi WiFi
WIFI_SSID = "POCO M3"  
WIFI_PASS = "Palem2f8771"

# URL Server Flask untuk MongoDB
SERVER_URL = "http://192.168.105.57:5000/iot_data"  

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-4p3JS6lOPE6pouh8uHFWg3CjWkBm7B"
DEVICE_LABEL = "ESP32"
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"

HEADERS = {
    "Content-Type": "application/json"
}
UBIDOTS_HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# Fungsi untuk menghubungkan WiFi
def connect_wifi():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print("Menghubungkan ke WiFi", end="")
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASS)
        timeout = 10
        while not sta_if.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        if sta_if.isconnected():
            print(" Terhubung!")
        else:
            print("Gagal terhubung ke jaringan WiFi!")

# Inisialisasi perangkat keras sensor
led = m.Pin(4, m.Pin.OUT)  
sensor = dht.DHT11(m.Pin(5)) 
pir_sensor = m.Pin(18, m.Pin.IN)  

# Fungsi untuk mengirim data ke server Flask
def send_to_server(temp, hum, motion):
    payload = ujson.dumps({
        "temperature": temp,
        "humidity": hum,
        "motion": motion
    })
    print(f"Mengirim data ke server: {payload}")

    try:
        response = urequests.post(SERVER_URL, headers=HEADERS, data=payload)
        status_code = response.status_code
        response.close()

        if status_code == 201:
            print("Data berhasil dikirim ke server MongoDB")
        else:
            print(f"Kesalahan saat mengirim data, kode status: {status_code}")

    except Exception as e:
        print(f"Kesalahan saat mengirim data ke server: {e}")

# Fungsi untuk mengirim data ke Ubidots
def send_to_ubidots(temp, hum, motion):
    payload = ujson.dumps({
        "temperature": temp,
        "humidity": hum,
        "motion": motion
    })
    print(f"Mengirim data ke Ubidots: {payload}")

    try:
        response = urequests.post(UBIDOTS_URL, headers=UBIDOTS_HEADERS, data=payload)
        status_code = response.status_code
        response.close()

        if status_code == 200:
            print("Data berhasil dikirim ke Ubidots")
        else:
            print(f"Kesalahan saat mengirim data, kode status: {status_code}")

    except Exception as e:
        print(f"Kesalahan saat mengirim data ke Ubidots: {e}")

# Fungsi untuk mendapatkan status LED dari Ubidots
def get_led_status():
    url = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/led_control/lv"
    try:
        response = urequests.get(url, headers={"X-Auth-Token": UBIDOTS_TOKEN})
        raw_data = response.text.strip()
        response.close()

        print(f"Raw Response: {raw_data}")

        try:
            led_value = int(float(raw_data))
            print(f"LED Control Value: {led_value}")
            return led_value
        except ValueError:
            print("JSON Parsing Error! Menggunakan default LED OFF.")
            return 0
    except Exception as e:
        print(f"Error getting LED status: {e}")
        return 0


# Menghubungkan ke WiFi
connect_wifi()

# Loop utama
while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected():
            print("Koneksi WiFi terputus, mencoba menyambungkan kembali...")
            connect_wifi()

        sensor.measure()
        temperature = sensor.temperature()
        humidity = sensor.humidity()
        motion_detected = pir_sensor.value()

        send_to_server(temperature, humidity, motion_detected)
        send_to_ubidots(temperature, humidity, motion_detected)

        led_status = get_led_status()
        led.value(led_status)  # 1 = ON, 0 = OFF
        print("LED ON" if led_status == 1 else "LED OFF")

        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
