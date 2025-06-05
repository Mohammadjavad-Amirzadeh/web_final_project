from app import create_app
import time
import threading
from datetime import datetime, timedelta, UTC
from app.models.reservation import Reservation
from app.extensions import db

app = create_app()

def delete_old_reservations():
    with app.app_context():
        while True:
            now = datetime.now(UTC)
            cutoff = now - timedelta(minutes=1)

            old_reservations = Reservation.query.filter(
                Reservation.created_at < cutoff,
                Reservation.confirmed_at == None,
                Reservation.half_paid_at == None,
                Reservation.fully_paid_at == None,
                Reservation.is_free_mode == False
            ).all()

            if old_reservations:
                print(f"[{datetime.now(UTC).isoformat()}] Deleting {len(old_reservations)} old reservations...")
                for res in old_reservations:
                    db.session.delete(res)
                db.session.commit()
            else:
                print(f"[{datetime.now(UTC).isoformat()}] No old reservations found.")

            time.sleep(60)

def start_cleaner_thread():
    cleaner_thread = threading.Thread(target=delete_old_reservations, daemon=True)
    cleaner_thread.start()

if __name__ == "__main__":
    start_cleaner_thread()
    app.run(debug=True)
