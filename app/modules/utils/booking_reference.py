import random
import string
from datetime import datetime

def generate_booking_reference():

    random_part = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=4
        )
    )

    return f"CMX-{datetime.utcnow().strftime('%Y%m%d')}-{random_part}"
