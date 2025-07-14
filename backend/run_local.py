#!/usr/bin/env python3
"""
Script para ejecutar el backend del sistema de reservas de hotel en local
"""

import os
import sys
import subprocess
import time

def check_mongodb():
    """Verificar si MongoDB está corriendo"""
    try:
        import pymongo
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
        client.server_info()
        print("✅ MongoDB está corriendo")
        return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        print("Asegúrate de que MongoDB esté instalado y ejecutándose")
        return False

def install_dependencies():
    """Instalar dependencias si no están instaladas"""
    try:
        import bcrypt
        import fastapi
        import uvicorn
        import pymongo
        import jwt
        print("✅ Todas las dependencias están instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("Instalando dependencias...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def main():
    print("=== Iniciando Backend del Sistema de Reservas de Hotel ===")
    
    # Verificar MongoDB
    if not check_mongodb():
        return
    
    # Instalar dependencias
    if not install_dependencies():
        return
    
    # Configurar variables de entorno
    os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
    os.environ['JWT_SECRET'] = 'hotel-secret-key-local-2025'
    
    print("✅ Configuración completada")
    print("🚀 Iniciando servidor backend en http://localhost:8001")
    print("📖 Documentación API disponible en http://localhost:8001/docs")
    print("Presiona Ctrl+C para detener el servidor")
    
    # Ejecutar servidor
    try:
        import uvicorn
        uvicorn.run("server:app", host="0.0.0.0", port=8001, reload=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido")
    except Exception as e:
        print(f"❌ Error ejecutando servidor: {e}")

if __name__ == "__main__":
    main()