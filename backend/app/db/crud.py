
from app.db.models import Document, Detection
from app.core.security import hash_value, encrypt_value

def create_document_and_detections(db, filename, detections):
	doc = Document(filename=filename)
	db.add(doc)
	db.flush()  # get doc.id
	for d in detections:
		det = Detection(
			document_id=doc.id,
			pii_type=d["type"],
			pii_hash=hash_value(d["value"]),
			encrypted_value=encrypt_value(d["value"]),
			score=d.get("score"),
			masked_value=d.get("masked_value"),
			start=d.get("start"),
			end=d.get("end")
		)
		db.add(det)
	db.commit()
	db.refresh(doc)
	return doc.id


def get_document_by_id(db, document_id):
    return db.query(Document).filter(Document.id == document_id).first()

def get_detections_by_document_id(db, document_id):
	return db.query(Detection).filter(Detection.document_id == document_id).all()
