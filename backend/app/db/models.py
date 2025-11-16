from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    detections = relationship("Detection", back_populates="document")

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    pii_type = Column(String)
    pii_hash = Column(String)  # Store hash, not raw value
    encrypted_value = Column(LargeBinary)  # Encrypted with KMS key
    score = Column(Integer, nullable=True)
    masked_value = Column(String, nullable=True)
    start = Column(Integer)
    end = Column(Integer)
    document = relationship("Document", back_populates="detections")

# NOTE: After this change, run DB migration or recreate tables.
