from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_name = Column(String(100), nullable=False)
    patient_email = Column(String(100), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_cpf = Column(String(14), nullable=True)
    appointment_date = Column(DateTime, nullable=False)
    appointment_type = Column(String(50), nullable=False)  # consulta, retorno, exame
    symptoms = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    insurance = Column(String(100), nullable=True)
    status = Column(String(20), default='agendado')  # agendado, confirmado, cancelado, realizado
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'patient_email': self.patient_email,
            'patient_phone': self.patient_phone,
            'patient_cpf': self.patient_cpf,
            'appointment_date': self.appointment_date.isoformat() if self.appointment_date else None,
            'appointment_type': self.appointment_type,
            'symptoms': self.symptoms,
            'medical_history': self.medical_history,
            'insurance': self.insurance,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Contact(Base):
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default='novo')  # novo, lido, respondido
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    patient_name = Column(String(100), nullable=False)
    patient_email = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    review_text = Column(Text, nullable=False)
    treatment_type = Column(String(100), nullable=True)
    is_approved = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_name': self.patient_name,
            'patient_email': self.patient_email,
            'rating': self.rating,
            'review_text': self.review_text,
            'treatment_type': self.treatment_type,
            'is_approved': self.is_approved,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

