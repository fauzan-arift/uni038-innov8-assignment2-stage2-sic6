from pymongo import MongoClient
from flask import Flask, request, jsonify

app = Flask(__name__)

# Konfigurasi MongoDB
MONGO_URI = "mongodb+srv://fauzanariftricahya:Iqb4ik7xJ93NCLaj@cluster-ojan.jns5d.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-Ojan"
DATABASE_NAME = "iot_data"
COLLECTION_NAME = "sensor"

# Koneksi ke MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    client.admin.command("ping")
    print("Koneksi ke MongoDB berhasil!")
except Exception as e:
    print(f"Gagal terhubung ke MongoDB: {e}")

# Endpoint untuk menerima data dari ESP32
@app.route('/iot_data', methods=['POST'])
def receive_iot_data():
    data = request.json
    if not data:
        return jsonify({"error": "Tidak ada data yang tersedia"}), 400

    try:
        collection.insert_one(data)
        return jsonify({"message": "Data berhasil dimasukkan"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Menjalankan Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
