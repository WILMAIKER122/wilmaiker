from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import pymongo
import os
import jwt
import bcrypt
import uuid
from bson import ObjectId

# Environment variables
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
JWT_SECRET = os.environ.get('JWT_SECRET', 'hotel-secret-key-2025')
JWT_ALGORITHM = 'HS256'

# Database connection
client = pymongo.MongoClient(MONGO_URL)
db = client['hotel_reservations']

# Collections
workers_collection = db['workers']
clients_collection = db['clients']
rooms_collection = db['rooms']
reservations_collection = db['reservations']

# FastAPI app
app = FastAPI(title="Hotel Reservation System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class WorkerCreate(BaseModel):
    email: str
    password: str
    name: str
    phone: str
    hotel_name: str

class WorkerLogin(BaseModel):
    email: str
    password: str

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str
    identification: str

class RoomCreate(BaseModel):
    room_number: str
    room_type: str
    price_per_night: float
    capacity: int
    description: str

class ReservationCreate(BaseModel):
    client_id: str
    room_id: str
    check_in_date: str
    check_out_date: str
    guests: int

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(worker_id: str) -> str:
    payload = {
        'worker_id': worker_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        worker_id = payload.get('worker_id')
        if not worker_id:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        worker = workers_collection.find_one({'worker_id': worker_id})
        if not worker:
            raise HTTPException(status_code=401, detail="Trabajador no encontrado")
        
        return worker
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

# API Routes

# Worker Authentication
@app.post("/api/workers/register")
async def register_worker(worker: WorkerCreate):
    # Check if worker already exists
    if workers_collection.find_one({'email': worker.email}):
        raise HTTPException(status_code=400, detail="El trabajador ya existe")
    
    # Create worker
    worker_id = str(uuid.uuid4())
    worker_data = {
        'worker_id': worker_id,
        'email': worker.email,
        'password': hash_password(worker.password),
        'name': worker.name,
        'phone': worker.phone,
        'hotel_name': worker.hotel_name,
        'created_at': datetime.utcnow()
    }
    
    workers_collection.insert_one(worker_data)
    
    # Create default rooms for the hotel
    default_rooms = [
        {
            'room_id': str(uuid.uuid4()),
            'room_number': '101',
            'room_type': 'Simple',
            'price_per_night': 50.0,
            'capacity': 2,
            'description': 'Habitación simple con cama matrimonial',
            'hotel_name': worker.hotel_name,
            'is_available': True,
            'created_at': datetime.utcnow()
        },
        {
            'room_id': str(uuid.uuid4()),
            'room_number': '201',
            'room_type': 'Doble',
            'price_per_night': 80.0,
            'capacity': 4,
            'description': 'Habitación doble con dos camas',
            'hotel_name': worker.hotel_name,
            'is_available': True,
            'created_at': datetime.utcnow()
        },
        {
            'room_id': str(uuid.uuid4()),
            'room_number': '301',
            'room_type': 'Suite',
            'price_per_night': 150.0,
            'capacity': 6,
            'description': 'Suite de lujo con jacuzzi',
            'hotel_name': worker.hotel_name,
            'is_available': True,
            'created_at': datetime.utcnow()
        }
    ]
    
    rooms_collection.insert_many(default_rooms)
    
    return {'message': 'Trabajador registrado exitosamente', 'worker_id': worker_id}

@app.post("/api/workers/login")
async def login_worker(worker: WorkerLogin):
    # Find worker
    worker_data = workers_collection.find_one({'email': worker.email})
    if not worker_data or not verify_password(worker.password, worker_data['password']):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    # Create token
    token = create_token(worker_data['worker_id'])
    
    return {
        'token': token,
        'worker': {
            'worker_id': worker_data['worker_id'],
            'name': worker_data['name'],
            'email': worker_data['email'],
            'hotel_name': worker_data['hotel_name']
        }
    }

@app.get("/api/workers/profile")
async def get_worker_profile(current_worker = Depends(verify_token)):
    return {
        'worker_id': current_worker['worker_id'],
        'name': current_worker['name'],
        'email': current_worker['email'],
        'hotel_name': current_worker['hotel_name']
    }

# Client Management
@app.post("/api/clients")
async def create_client(client: ClientCreate, current_worker = Depends(verify_token)):
    # Check if client already exists
    if clients_collection.find_one({'email': client.email}):
        raise HTTPException(status_code=400, detail="El cliente ya existe")
    
    client_id = str(uuid.uuid4())
    client_data = {
        'client_id': client_id,
        'name': client.name,
        'email': client.email,
        'phone': client.phone,
        'identification': client.identification,
        'hotel_name': current_worker['hotel_name'],
        'created_by': current_worker['worker_id'],
        'created_at': datetime.utcnow()
    }
    
    clients_collection.insert_one(client_data)
    
    return {'message': 'Cliente registrado exitosamente', 'client_id': client_id}

@app.get("/api/clients")
async def get_clients(current_worker = Depends(verify_token)):
    clients = list(clients_collection.find({
        'hotel_name': current_worker['hotel_name']
    }, {'_id': 0}))
    
    return clients

# Room Management
@app.post("/api/rooms")
async def create_room(room: RoomCreate, current_worker = Depends(verify_token)):
    room_id = str(uuid.uuid4())
    room_data = {
        'room_id': room_id,
        'room_number': room.room_number,
        'room_type': room.room_type,
        'price_per_night': room.price_per_night,
        'capacity': room.capacity,
        'description': room.description,
        'hotel_name': current_worker['hotel_name'],
        'is_available': True,
        'created_at': datetime.utcnow()
    }
    
    rooms_collection.insert_one(room_data)
    
    return {'message': 'Habitación creada exitosamente', 'room_id': room_id}

@app.get("/api/rooms")
async def get_rooms(current_worker = Depends(verify_token)):
    rooms = list(rooms_collection.find({
        'hotel_name': current_worker['hotel_name']
    }, {'_id': 0}))
    
    return rooms

@app.get("/api/rooms/available")
async def get_available_rooms(current_worker = Depends(verify_token)):
    rooms = list(rooms_collection.find({
        'hotel_name': current_worker['hotel_name'],
        'is_available': True
    }, {'_id': 0}))
    
    return rooms

# Reservation Management
@app.post("/api/reservations")
async def create_reservation(reservation: ReservationCreate, current_worker = Depends(verify_token)):
    # Validate client exists
    client = clients_collection.find_one({'client_id': reservation.client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Validate room exists and is available
    room = rooms_collection.find_one({'room_id': reservation.room_id, 'is_available': True})
    if not room:
        raise HTTPException(status_code=404, detail="Habitación no disponible")
    
    # Parse dates
    try:
        check_in = datetime.strptime(reservation.check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(reservation.check_out_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido")
    
    if check_in >= check_out:
        raise HTTPException(status_code=400, detail="La fecha de salida debe ser posterior a la de entrada")
    
    # Calculate total price
    nights = (check_out - check_in).days
    total_price = nights * room['price_per_night']
    
    # Create reservation
    reservation_id = str(uuid.uuid4())
    reservation_data = {
        'reservation_id': reservation_id,
        'client_id': reservation.client_id,
        'room_id': reservation.room_id,
        'check_in_date': check_in,
        'check_out_date': check_out,
        'guests': reservation.guests,
        'nights': nights,
        'total_price': total_price,
        'status': 'active',
        'hotel_name': current_worker['hotel_name'],
        'created_by': current_worker['worker_id'],
        'created_at': datetime.utcnow()
    }
    
    reservations_collection.insert_one(reservation_data)
    
    # Mark room as unavailable
    rooms_collection.update_one(
        {'room_id': reservation.room_id},
        {'$set': {'is_available': False}}
    )
    
    return {
        'message': 'Reserva creada exitosamente',
        'reservation_id': reservation_id,
        'total_price': total_price,
        'nights': nights
    }

@app.get("/api/reservations")
async def get_reservations(current_worker = Depends(verify_token)):
    reservations = list(reservations_collection.find({
        'hotel_name': current_worker['hotel_name']
    }, {'_id': 0}))
    
    # Add client and room details
    for reservation in reservations:
        client = clients_collection.find_one({'client_id': reservation['client_id']})
        room = rooms_collection.find_one({'room_id': reservation['room_id']})
        
        reservation['client_name'] = client['name'] if client else 'Cliente no encontrado'
        reservation['room_number'] = room['room_number'] if room else 'Habitación no encontrada'
    
    return reservations

@app.delete("/api/reservations/{reservation_id}")
async def cancel_reservation(reservation_id: str, current_worker = Depends(verify_token)):
    reservation = reservations_collection.find_one({'reservation_id': reservation_id})
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Update reservation status
    reservations_collection.update_one(
        {'reservation_id': reservation_id},
        {'$set': {'status': 'cancelled', 'cancelled_at': datetime.utcnow()}}
    )
    
    # Mark room as available
    rooms_collection.update_one(
        {'room_id': reservation['room_id']},
        {'$set': {'is_available': True}}
    )
    
    return {'message': 'Reserva cancelada exitosamente'}

# Dashboard Stats
@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_worker = Depends(verify_token)):
    hotel_name = current_worker['hotel_name']
    
    # Count stats
    total_clients = clients_collection.count_documents({'hotel_name': hotel_name})
    total_rooms = rooms_collection.count_documents({'hotel_name': hotel_name})
    available_rooms = rooms_collection.count_documents({'hotel_name': hotel_name, 'is_available': True})
    active_reservations = reservations_collection.count_documents({'hotel_name': hotel_name, 'status': 'active'})
    
    return {
        'total_clients': total_clients,
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': total_rooms - available_rooms,
        'active_reservations': active_reservations
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)